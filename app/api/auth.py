"""
Endpoints de autenticação.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.auth import authenticate_admin, register_admin, get_admin_by_id
from app.utils.errors import ValidationError, UnauthorizedError
from app.utils.validators import validate_admin_data, validate_login_data

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login de admin.
    POST /api/auth/login
    {
        "email": "admin@example.com",
        "password": "senha123"
    }
    """
    try:
        data = request.get_json() or {}
        validate_login_data(data)

        token, admin = authenticate_admin(data["email"], data["password"])
        
        return jsonify({
            "token": token,
            "admin": {
                "id": admin.id,
                "email": admin.email
            }
        }), 200
    
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except ValidationError as e:
        raise e
    except Exception as e:
        raise Exception(f"Erro ao fazer login: {str(e)}")


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_admin():
    """
    Retorna dados do admin autenticado.
    GET /api/auth/me
    Header: Authorization: Bearer <token>
    """
    try:
        admin_id = get_jwt_identity()
        admin = get_admin_by_id(admin_id)
        
        if not admin:
            raise UnauthorizedError("Admin não encontrado")
        
        return jsonify({
            "id": admin.id,
            "email": admin.email,
            "is_active": admin.is_active
        }), 200
    
    except Exception as e:
        raise Exception(f"Erro ao obter dados do admin: {str(e)}")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registra um novo admin.
    POST /api/auth/register
    {
        "email": "admin@example.com",
        "password": "senha123"
    }
    """
    try:
        data = request.get_json() or {}
        validate_admin_data(data)
        
        admin = register_admin(data["email"], data["password"])
        
        return jsonify({
            "message": "Admin registrado com sucesso",
            "admin": {
                "id": admin.id,
                "email": admin.email
            }
        }), 201
    
    except ValueError as e:
        raise ValidationError(str(e))
    except ValidationError as e:
        raise e
    except Exception as e:
        raise Exception(f"Erro ao registrar admin: {str(e)}")
