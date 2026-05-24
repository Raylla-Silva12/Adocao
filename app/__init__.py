"""
Inicializador do pacote app.
"""
from app.extensions import db, migrate, jwt
from app.factory import create_app

app = create_app()

__all__ = ["db", "migrate", "jwt", "create_app", "app"]
