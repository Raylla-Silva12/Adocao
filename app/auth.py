"""
Autenticação JWT.
"""
from flask import jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Admin
from app.extensions import db


def register_admin(email, password):
    """Registra um novo admin."""
    if Admin.query.filter_by(email=email).first():
        raise ValueError("Email já existe")
    
    admin = Admin(
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def authenticate_admin(email, password):
    """Autentica um admin e retorna o token."""
    admin = Admin.query.filter_by(email=email).first()
    
    if not admin or not check_password_hash(admin.password_hash, password):
        raise ValueError("Email ou senha incorretos")
    
    if not admin.is_active:
        raise ValueError("Admin inativo")
    
    access_token = create_access_token(identity=admin.id)
    return access_token, admin


def get_admin_by_id(admin_id):
    """Retorna um admin pelo ID."""
    return Admin.query.get(admin_id)
