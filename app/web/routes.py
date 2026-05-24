"""
Rotas da interface web (HTML).
A API REST continua em /api/*.
"""
from flask import Blueprint, render_template, request, abort
from app.models import Pet

web_bp = Blueprint("web", __name__)


def _status_label(status: str) -> str:
    labels = {
        "available": "Disponível",
        "adopted": "Adotado",
        "pending": "Em processo",
    }
    return labels.get(status, status)


@web_bp.app_template_filter("status_label")
def status_label_filter(status):
    return _status_label(status)


@web_bp.route("/")
def home():
    """Página inicial com destaques."""
    featured = (
        Pet.query.filter_by(status="available")
        .order_by(Pet.created_at.desc())
        .limit(6)
        .all()
    )
    total_available = Pet.query.filter_by(status="available").count()
    return render_template(
        "index.html",
        pets=featured,
        total_available=total_available,
    )


@web_bp.route("/gatos")
def list_pets():
    """Catálogo de gatos disponíveis para adoção."""
    status = request.args.get("status", "available")
    query = Pet.query.filter_by(species="gato")
    if status and status != "all":
        query = query.filter_by(status=status)
    pets = query.order_by(Pet.created_at.desc()).all()
    return render_template(
        "gatos.html",
        pets=pets,
        current_status=status,
    )


@web_bp.route("/gatos/<pet_id>")
def pet_detail(pet_id):
    """Página de detalhes de um gato."""
    pet = Pet.query.get(pet_id)
    if not pet:
        abort(404)
    related = (
        Pet.query.filter(
            Pet.id != pet.id,
            Pet.species == "gato",
            Pet.status == "available",
        )
        .order_by(Pet.created_at.desc())
        .limit(3)
        .all()
    )
    return render_template("gato.html", pet=pet, related=related)


@web_bp.route("/admin")
def admin_login_page():
    """Tela de login do administrador."""
    return render_template("admin/login.html")


@web_bp.route("/admin/painel")
def admin_dashboard_page():
    """Painel administrativo (gerencia pets via API)."""
    return render_template("admin/painel.html")
