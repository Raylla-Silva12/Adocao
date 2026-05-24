"""
Configurações da aplicação Flask.
Suporta múltiplos ambientes: desenvolvimento, testes e produção.
"""
import os
import urllib.parse
from datetime import timedelta


def _build_database_uri() -> str:
    """
    Monta a URI do PostgreSQL.
    Cloud Run + Cloud SQL: DB_HOST=/cloudsql/PROJECT:REGION:INSTANCE
    """
    user = os.getenv("DB_USER", "postgres")
    password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "password"))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "adocao_gatos")

    # Socket Unix do Cloud SQL (produção no Cloud Run)
    if host.startswith("/cloudsql/"):
        return f"postgresql+psycopg2://{user}:{password}@/{name}?host={host}"

    # Desenvolvimento local ou TCP
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


class Config:
    """Configurações base."""

    # Database
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "adocao_gatos")

    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seu-secret-key-super-secreto")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # Google Cloud Storage
    GCS_BUCKET = os.getenv("GCS_BUCKET", "")

    # Admin credentials
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configurações de testes."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Configurações de produção."""
    DEBUG = False
    TESTING = False


# Seletor de configuração
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env=None):
    """Retorna a configuração apropriada."""
    if env is None:
        env = os.getenv("FLASK_ENV", "production")
    return config.get(env, ProductionConfig)
