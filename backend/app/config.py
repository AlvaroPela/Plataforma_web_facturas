"""Configuración central. Todo valor que cambie entre local y nube vive en .env."""
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "facturas_db"
    db_user: str
    db_password: str

    jwt_secret: str
    jwt_algoritmo: str = "HS256"
    jwt_minutos_expiracion: int = 60

    totp_emisor: str = "Plataforma Facturas"
    max_intentos_fallidos: int = 5
    minutos_bloqueo: int = 15

    cors_origenes: list[str] = ["http://localhost:5173"]

    @property
    def database_url(self) -> str:
        # quote_plus protege contraseñas con caracteres como # @ :
        return (
            f"mysql+pymysql://{self.db_user}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()
