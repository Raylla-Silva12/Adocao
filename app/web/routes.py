"""
Rotas da interface web (HTML).
A API REST continua em /api/*.
"""
import urllib.parse

from flask import Blueprint, render_template, request, abort, redirect, url_for
from app.models import Pet
from app.web.email_templates import (
    LIST_PET_SUBJECT,
    LIST_PET_BODY,
    adopt_pet_subject,
    adopt_pet_body,
)

web_bp = Blueprint("web", __name__)


def _status_label(status: str) -> str:
    labels = {
        "available": "Disponível",
        "adopted": "Adotado",
        "pending": "Em processo",
    }
    return labels.get(status, status)


def _species_label(species: str) -> str:
    labels = {
        "gato": "Gato",
        "cao": "Cão",
    }
    return labels.get(species, species)


@web_bp.app_template_filter("status_label")
def status_label_filter(status):
    return _status_label(status)


@web_bp.app_template_filter("species_label")
def species_label_filter(species):
    return _species_label(species)


@web_bp.app_context_processor
def inject_contact():
    """Disponibiliza e-mail e textos de contato nos templates."""
    from flask import current_app
    return {
        "contact_email": current_app.config["CONTACT_EMAIL"],
        "list_pet_subject": LIST_PET_SUBJECT,
        "list_pet_body": LIST_PET_BODY,
    }


@web_bp.app_template_global()
def adopt_pet_email_subject(pet_name):
    return adopt_pet_subject(pet_name)


@web_bp.app_template_global()
def adopt_pet_email_body(pet_name, pet_type, profile_url):
    return adopt_pet_body(pet_name, pet_type, profile_url)


@web_bp.app_template_global()
def email_compose_url(email, subject, body):
    """
    Gera link para compor e-mail no navegador.
    Gmail abre na web; outros endereços usam mailto.
    """
    if email.lower().endswith("@gmail.com"):
        params = urllib.parse.urlencode(
            {
                "view": "cm",
                "fs": "1",
                "to": email,
                "su": subject,
                "body": body,
            },
            quote_via=urllib.parse.quote,
        )
        return f"https://mail.google.com/mail/?{params}"

    params = urllib.parse.urlencode(
        {"subject": subject, "body": body},
        quote_via=urllib.parse.quote,
    )
    return f"mailto:{email}?{params}"


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


@web_bp.route("/pets")
def list_pets():
    """Catálogo de gatos e cães disponíveis para adoção."""
    status = request.args.get("status", "available")
    species = request.args.get("species", "all")

    query = Pet.query
    if species and species != "all":
        query = query.filter_by(species=species)
    if status and status != "all":
        query = query.filter_by(status=status)

    pets = query.order_by(Pet.created_at.desc()).all()
    return render_template(
        "pets.html",
        pets=pets,
        current_status=status,
        current_species=species,
    )


@web_bp.route("/pets/<pet_id>")
def pet_detail(pet_id):
    """Página de detalhes de um pet."""
    pet = Pet.query.get(pet_id)
    if not pet:
        abort(404)
    related = (
        Pet.query.filter(
            Pet.id != pet.id,
            Pet.status == "available",
        )
        .order_by(Pet.created_at.desc())
        .limit(3)
        .all()
    )
    return render_template("pet.html", pet=pet, related=related)


@web_bp.route("/gatos")
def list_pets_legacy():
    """Redireciona URL antiga para o catálogo."""
    return redirect(url_for("web.list_pets", **request.args), code=301)


@web_bp.route("/gatos/<pet_id>")
def pet_detail_legacy(pet_id):
    """Redireciona URL antiga para o perfil do pet."""
    return redirect(url_for("web.pet_detail", pet_id=pet_id), code=301)


@web_bp.route("/admin")
def admin_login_page():
    """Tela de login do administrador."""
    return render_template("admin/login.html")


@web_bp.route("/admin/painel")
def admin_dashboard_page():
    """Painel administrativo (gerencia pets via API)."""
    return render_template("admin/painel.html")
