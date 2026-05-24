"""
Handlers de erros.
"""
from flask import jsonify, request, render_template


class APIError(Exception):
    """Classe base para erros de API."""
    
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code


class ValidationError(APIError):
    """Erro de validação."""
    
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(APIError):
    """Recurso não encontrado."""
    
    def __init__(self, message="Recurso não encontrado"):
        super().__init__(message, 404)


class UnauthorizedError(APIError):
    """Não autorizado."""
    
    def __init__(self, message="Não autorizado"):
        super().__init__(message, 401)


def register_error_handlers(app):
    """Registra handlers de erro."""
    
    @app.errorhandler(APIError)
    def handle_api_error(e):
        response = {"error": e.message}
        return jsonify(response), e.status_code
    
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api"):
            return jsonify({"error": "Não encontrado"}), 404
        return render_template("404.html"), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Erro interno do servidor"}), 500
    
    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({"error": "Dados inválidos"}), 422
