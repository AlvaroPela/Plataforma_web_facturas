"""HU1 - Iniciar sesión con correo, contraseña y 2FA."""
from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencias import obtener_usuario_actual
from app.models import Usuario
from app.schemas import Activar2FAEntrada, LoginEntrada, LoginRespuesta, MSG_CODIGO, UsuarioSesion
from app.security import (
    HASH_FALSO, ahora_utc, crear_token, decodificar_token, generar_secreto_totp,
    qr_en_base64, uri_totp, verificar_codigo_totp, verificar_contrasena,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Mensajes exactos de los criterios de aceptación de la HU1
MSG_CREDENCIALES = "Usuario o contraseña incorrectos"
MSG_INACTIVA = "Su cuenta se encuentra inactiva, comuníquese con el administrador"
MSG_BLOQUEADA = "Cuenta bloqueada temporalmente"


def _a_sesion(usuario: Usuario) -> UsuarioSesion:
    return UsuarioSesion(
        id=usuario.id,
        nombre=usuario.nombre_completo,
        correo=usuario.correo,
        rol=usuario.rol.nombre,
        debe_cambiar_contrasena=usuario.debe_cambiar_contrasena,
    )


def _registrar_fallo(db: Session, usuario: Usuario, mensaje: str) -> HTTPException:
    """Suma un intento fallido; al llegar al máximo bloquea la cuenta."""
    usuario.intentos_fallidos += 1
    if usuario.intentos_fallidos >= settings.max_intentos_fallidos:
        usuario.bloqueado_hasta = ahora_utc() + timedelta(minutes=settings.minutos_bloqueo)
        usuario.intentos_fallidos = 0
        db.commit()
        return HTTPException(status.HTTP_423_LOCKED, MSG_BLOQUEADA)
    db.commit()
    return HTTPException(status.HTTP_401_UNAUTHORIZED, mensaje)


def _emitir_sesion(db: Session, usuario: Usuario) -> LoginRespuesta:
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.ultimo_ingreso = ahora_utc()
    db.commit()
    token = crear_token(
        {"sub": str(usuario.id), "rol": usuario.rol.nombre},
        settings.jwt_minutos_expiracion,
        "acceso",
    )
    return LoginRespuesta(estado="autenticado", access_token=token, usuario=_a_sesion(usuario))


@router.post("/login", response_model=LoginRespuesta)
def iniciar_sesion(datos: LoginEntrada, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.correo == datos.correo))

    # 1. El correo no existe: mismo mensaje y mismo tiempo que una clave errada
    if usuario is None:
        verificar_contrasena(datos.contrasena, HASH_FALSO)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, MSG_CREDENCIALES)

    # 2. Cuenta bloqueada por intentos fallidos
    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora_utc():
        raise HTTPException(status.HTTP_423_LOCKED, MSG_BLOQUEADA)

    # 3. Contraseña incorrecta
    if not verificar_contrasena(datos.contrasena, usuario.contrasena_hash):
        raise _registrar_fallo(db, usuario, MSG_CREDENCIALES)

    # 4. Cuenta inactiva (se valida después de la clave para no revelar cuentas)
    if not usuario.activo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, MSG_INACTIVA)

    # 5. Primer ingreso: aún no ha vinculado Google/Microsoft Authenticator
    if not usuario.totp_activo:
        if not usuario.totp_secreto:
            usuario.totp_secreto = generar_secreto_totp()
            db.commit()
        token_conf = crear_token({"sub": str(usuario.id)}, 10, "configurar_2fa")
        return LoginRespuesta(
            estado="configurar_2fa",
            token_configuracion=token_conf,
            qr=qr_en_base64(uri_totp(usuario.totp_secreto, usuario.correo)),
            secreto=usuario.totp_secreto,
        )

    # 6. Código de verificación de 6 dígitos
    if not datos.codigo or not verificar_codigo_totp(usuario.totp_secreto, datos.codigo):
        raise _registrar_fallo(db, usuario, MSG_CODIGO)

    # 7. Todo correcto
    return _emitir_sesion(db, usuario)


@router.post("/2fa/activar", response_model=LoginRespuesta)
def activar_2fa(datos: Activar2FAEntrada, db: Session = Depends(get_db)):
    """Primer ingreso: el usuario escaneó el QR y envía el primer código."""
    try:
        payload = decodificar_token(datos.token_configuracion, "configurar_2fa")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La configuración expiró, inicie sesión nuevamente")

    usuario = db.get(Usuario, int(payload["sub"]))
    if usuario is None or not usuario.activo or usuario.totp_activo or not usuario.totp_secreto:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Solicitud no válida")

    if not verificar_codigo_totp(usuario.totp_secreto, datos.codigo):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, MSG_CODIGO)

    usuario.totp_activo = True
    return _emitir_sesion(db, usuario)


@router.get("/yo", response_model=UsuarioSesion)
def usuario_en_sesion(usuario: Usuario = Depends(obtener_usuario_actual)):
    """El frontend lo usa para pintar el menú según el rol."""
    return _a_sesion(usuario)
