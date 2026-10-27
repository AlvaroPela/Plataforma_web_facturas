"""Conexión a MySQL con SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # revisa que la conexión siga viva (clave en la nube)
    pool_recycle=3600,    # renueva conexiones antes de que MySQL las cierre
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia de FastAPI: abre una sesión por petición y siempre la cierra."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
