"""Crea el primer administrador (la HU3 'Crear usuario' llega en otro sprint).
Ejecutar desde la carpeta backend:  python -m scripts.crear_admin
"""
from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Rol, TipoDocumento, Usuario
from app.schemas import PATRON_CORREO
from app.security import cumple_politica, hashear_contrasena


def main() -> None:
    print("=== Crear administrador inicial ===")
    primer_nombre = input("Primer nombre: ").strip()
    primer_apellido = input("Primer apellido: ").strip()
    numero_documento = input("Número de cédula: ").strip()
    correo = input("Correo: ").strip().lower()
    contrasena = getpass("Contraseña: ")

    if not PATRON_CORREO.match(correo):
        print("Verificar correo"); return
    if not numero_documento.isdigit():
        print("El documento solo acepta números"); return
    if not cumple_politica(contrasena):
        print("La contraseña no cumple con los requisitos de seguridad"); return

    with SessionLocal() as db:
        if db.scalar(select(Usuario).where(Usuario.correo == correo)):
            print("El usuario se encuentra registrado"); return
        rol = db.scalar(select(Rol).where(Rol.nombre == "administrador"))
        tipo = db.scalar(select(TipoDocumento).where(TipoDocumento.codigo == "CC"))
        db.add(Usuario(
            primer_nombre=primer_nombre, primer_apellido=primer_apellido,
            tipo_documento_id=tipo.id, numero_documento=numero_documento,
            correo=correo, contrasena_hash=hashear_contrasena(contrasena),
            rol_id=rol.id, activo=True, debe_cambiar_contrasena=False,
        ))
        db.commit()
    print("El registro fue exitoso. Inicie sesión para vincular el 2FA.")


if __name__ == "__main__":
    main()
