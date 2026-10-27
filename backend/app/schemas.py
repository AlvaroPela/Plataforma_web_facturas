"""Esquemas Pydantic: definen y validan lo que entra y sale de la API."""
import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
MSG_CODIGO = "Código de verificación inválido o vencido"


def _validar_codigo(valor: str | None) -> str | None:
    if valor is not None and not re.fullmatch(r"\d{6}", valor):
        raise ValueError(MSG_CODIGO)
    return valor


class LoginEntrada(BaseModel):
    correo: str
    contrasena: str = Field(min_length=1, max_length=64)
    # Opcional SOLO para el primer ingreso (aún no hay app vinculada).
    codigo: str | None = None

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not PATRON_CORREO.match(valor):
            raise ValueError("Verificar correo")
        return valor

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, valor: str | None) -> str | None:
        return _validar_codigo(valor)


class Activar2FAEntrada(BaseModel):
    token_configuracion: str
    codigo: str

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, valor: str) -> str:
        return _validar_codigo(valor)


class UsuarioSesion(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    debe_cambiar_contrasena: bool


class LoginRespuesta(BaseModel):
    estado: Literal["autenticado", "configurar_2fa"]
    # Cuando estado = "autenticado"
    access_token: str | None = None
    token_type: str = "bearer"
    usuario: UsuarioSesion | None = None
    # Cuando estado = "configurar_2fa" (primer ingreso)
    token_configuracion: str | None = None
    qr: str | None = None
    secreto: str | None = None  # por si el usuario prefiere digitarlo en la app
