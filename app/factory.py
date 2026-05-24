"""
Aplicação Flask principal para o sistema de adoção de pets.
Configurado para rodar no Google Cloud Run.
"""
import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from app.extensions import db, migrate, jwt
from app.config import Config, get_config
from app.api import auth_bp, pets_bp
from app.web import web_bp
from app.utils.errors import register_error_handlers
from app.schema import upgrade_schema
from sqlalchemy import text

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _ensure_default_admin(app):
    """Cria admin padrão na primeira execução (local e nuvem)."""
    if app.config.get("TESTING"):
        return

    admin_email = app.config.get("ADMIN_EMAIL")
    admin_password = app.config.get("ADMIN_PASSWORD")
    if not admin_email or not admin_password:
        return

    from app.models import Admin
    from app.auth import register_admin

    if Admin.query.filter_by(email=admin_email).first():
        return

    try:
        register_admin(admin_email, admin_password)
        logger.info("Admin padrão criado: %s", admin_email)
    except ValueError as exc:
        logger.warning("Não foi possível criar admin padrão: %s", exc)


def create_app(config_class=None):
    """Factory pattern para criar a aplicação Flask."""
    if config_class is None:
        config_class = get_config()
    elif isinstance(config_class, str):
        config_class = get_config(config_class)

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # CORS - Permitir requisições de qualquer origem em desenvolvimento
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Registrar blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(pets_bp, url_prefix="/api/pets")
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Health check - importante para Cloud Run
    @app.route("/health")
    def health():
        try:
            # Verificar conexão com banco de dados
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500
    
    # Liveness probe para Cloud Run
    @app.route("/live")
    def liveness():
        return jsonify({"status": "alive"}), 200
    
    @app.route("/api")
    def api_index():
        """Informações da API REST (o site fica em /)."""
        return jsonify({
            "name": "Adoção de Pets API",
            "version": "1.0.0",
            "health": "/health",
            "pets": "/api/pets",
            "auth": "/api/auth",
        }), 200

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        """Serve fotos enviadas localmente."""
        upload_dir = app.config.get("UPLOAD_FOLDER", "uploads")
        return send_from_directory(upload_dir, filename)

    @app.route("/favicon.ico")
    def favicon():
        """Compatibilidade com navegadores que buscam /favicon.ico automaticamente."""
        return send_from_directory(
            os.path.join(app.root_path, "static", "img"),
            "favicon.svg",
            mimetype="image/svg+xml",
        )
    
    # Criar tabelas se não existirem
    with app.app_context():
        try:
            db.create_all()
            upgrade_schema()
            _ensure_default_admin(app)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    return app
