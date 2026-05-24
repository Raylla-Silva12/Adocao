"""
Validadores para dados de entrada.
"""
from app.utils.errors import ValidationError


def validate_pet_data(data):
    """Valida dados de um pet."""
    errors = []
    
    if not data.get("name"):
        errors.append("Nome é obrigatório")
    elif len(data.get("name", "")) > 255:
        errors.append("Nome muito longo (máx 255 caracteres)")
    
    if not data.get("species"):
        errors.append("Espécie é obrigatória")
    
    if data.get("age_years") is not None:
        try:
            age = int(data.get("age_years"))
            if age < 0 or age > 50:
                errors.append("Idade deve estar entre 0 e 50")
        except (ValueError, TypeError):
            errors.append("Idade deve ser um número")

    if data.get("owner_contact") is not None:
        contact = str(data.get("owner_contact", "")).strip()
        if len(contact) > 50:
            errors.append("Contato do responsável muito longo (máx 50 caracteres)")
    
    if errors:
        raise ValidationError(", ".join(errors))
    
    return True


def validate_admin_data(data):
    """Valida dados de admin."""
    errors = []
    
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email:
        errors.append("Email é obrigatório")
    elif "@" not in email or "." not in email.split("@")[1]:
        errors.append("Email inválido")
    
    if not password:
        errors.append("Senha é obrigatória")
    elif len(password) < 6:
        errors.append("Senha deve ter no mínimo 6 caracteres")
    
    if errors:
        raise ValidationError(", ".join(errors))
    
    return True
