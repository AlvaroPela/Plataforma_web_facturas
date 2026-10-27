"""Modelos ORM: cada clase representa una tabla creada en 01_schema_seguridad.sql."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Rol(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)


class TipoDocumento(Base):
    __tablename__ = "tipos_documento"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(5), unique=True)
    nombre: Mapped[str] = mapped_column(String(40))


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    primer_nombre: Mapped[str] = mapped_column(String(50))
    segundo_nombre: Mapped[str | None] = mapped_column(String(50))
    primer_apellido: Mapped[str] = mapped_column(String(50))
    segundo_apellido: Mapped[str | None] = mapped_column(String(50))
    tipo_documento_id: Mapped[int] = mapped_column(ForeignKey("tipos_documento.id"))
    numero_documento: Mapped[str] = mapped_column(String(20))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255))
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    totp_secreto: Mapped[str | None] = mapped_column(String(64))
    totp_activo: Mapped[bool] = mapped_column(Boolean, default=False)

    intentos_fallidos: Mapped[int] = mapped_column(SmallInteger, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime)

    debe_cambiar_contrasena: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_ingreso: Mapped[datetime | None] = mapped_column(DateTime)

    rol: Mapped[Rol] = relationship(lazy="joined")

    @property
    def nombre_completo(self) -> str:
        return f"{self.primer_nombre} {self.primer_apellido}"
