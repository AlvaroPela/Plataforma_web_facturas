"""Seguridad: hash de contraseñas, 2FA (TOTP) y tokens JWT."""
import base64
import io
import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pyotp
import qrcode

from app.config import settings


def ahora_utc() -> datetime:
    """Fecha/hora UTC sin zona, igual a como se guarda en DATETIME de MySQL."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------- Contraseñas ----------------------------
def hashear_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_contrasena(contrasena: str, contrasena_hash: str) -> bool:
    return bcrypt.checkpw(contrasena.encode("utf-8"), contrasena_hash.encode("utf-8"))


# Hash falso: se verifica cuando el correo no existe para que la respuesta
# tarde lo mismo y un atacante no pueda adivinar qué correos están registrados.
HASH_FALSO = hashear_contrasena("contrasena-que-no-existe")

POLITICA_CONTRASENA = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,64}$")


def cumple_politica(contrasena: str) -> bool:
    """HU2/HU5: mín. 8 caracteres, mayúscula, minúscula, número y carácter especial."""
    return bool(POLITICA_CONTRASENA.match(contrasena))


# ------------------------------- 2FA ---------------------------------
def generar_secreto_totp() -> str:
    return pyotp.random_base32()


def uri_totp(secreto: str, correo: str) -> str:
    """Texto que va dentro del QR; la app Authenticator lo entiende."""
    return pyotp.TOTP(secreto).provisioning_uri(name=correo, issuer_name=settings.totp_emisor)


def qr_en_base64(texto: str) -> str:
    """Genera el QR como imagen PNG lista para usar en un <img src=...> de React."""
    imagen = qrcode.make(texto)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def verificar_codigo_totp(secreto: str, codigo: str) -> bool:
    # valid_window=1 tolera 30 s de desfase entre el reloj del celular y el servidor
    return pyotp.TOTP(secreto).verify(codigo, valid_window=1)


# ------------------------------- JWT ---------------------------------
def crear_token(datos: dict, minutos: int, tipo: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {**datos, "tipo": tipo, "iat": ahora, "exp": ahora + timedelta(minutes=minutos)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str, tipo_esperado: str) -> dict:
    """Lanza jwt.PyJWTError si el token es falso, está vencido o es de otro tipo."""
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algoritmo])
    if payload.get("tipo") != tipo_esperado:
        raise jwt.InvalidTokenError("Tipo de token incorrecto")
    return payload
