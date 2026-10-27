"""Dependencias reutilizables: usuario autenticado y control por rol."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.security import decodificar_token

esquema_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Debe iniciar sesión")
    try:
        payload = decodificar_token(credenciales.credentials, "acceso")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión expiró, inicie sesión nuevamente")

    usuario = db.get(Usuario, int(payload["sub"]))
    if usuario is None or not usuario.activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión no es válida")
    return usuario


def requiere_roles(*roles_permitidos: str):
    """Uso: Depends(requiere_roles("administrador")) en cualquier endpoint futuro."""
    def verificador(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.rol.nombre not in roles_permitidos:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tiene permisos para acceder a esta opción")
        return usuario
    return verificador
