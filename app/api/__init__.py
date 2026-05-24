"""
Inicializador do pacote API.
"""
from app.api.auth import auth_bp
from app.api.pets import pets_bp

__all__ = ["auth_bp", "pets_bp"]
