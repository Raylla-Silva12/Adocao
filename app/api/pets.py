"""
Endpoints de pets.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from app.models import Pet
from app.extensions import db
from app.utils.uploads import upload_file, delete_file
from app.utils.errors import NotFoundError, ValidationError
from app.utils.validators import validate_pet_data, validate_pet_photo

pets_bp = Blueprint("pets", __name__)


def _get_pet(pet_id):
    return db.session.get(Pet, pet_id)


def _pet_validation_data(pet, data):
    """Mescla dados existentes com a requisição para validação parcial."""
    return {
        "name": data.get("name", pet.name),
        "species": data.get("species", pet.species),
        "age_years": data.get("age_years", pet.age_years),
        "owner_contact": data.get("owner_contact", pet.owner_contact or ""),
    }


def _is_admin_request():
    """True quando a requisição traz JWT válido de admin."""
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity() is not None
    except Exception:
        return False


def _serialize_pet(pet, admin=None):
    if admin is None:
        admin = _is_admin_request()
    return pet.to_dict(admin=admin)


@pets_bp.route("", methods=["GET"])
def list_pets():
    """
    Lista todos os pets.
    GET /api/pets?status=available&limit=10&offset=0
    """
    status = request.args.get("status")
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    # Limitar valores
    limit = min(limit, 100)

    query = Pet.query
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    pets = query.order_by(Pet.created_at.desc()).limit(limit).offset(offset).all()

    return jsonify({
        "total": total,
        "limit": limit,
        "offset": offset,
        "pets": [_serialize_pet(pet) for pet in pets]
    }), 200


@pets_bp.route("/<pet_id>", methods=["GET"])
def get_pet(pet_id):
    """
    Obtém detalhes de um pet específico.
    GET /api/pets/<pet_id>
    """
    pet = _get_pet(pet_id)

    if not pet:
        raise NotFoundError("Pet não encontrado")

    return jsonify(_serialize_pet(pet)), 200


@pets_bp.route("", methods=["POST"])
@jwt_required()
def create_pet():
    """
    Cria um novo pet.
    POST /api/pets
    Header: Authorization: Bearer <token>
    Content-Type: multipart/form-data
    
    Fields:
    - name (required)
    - species (required)
    - breed (optional)
    - age_years (optional)
    - description (optional)
    - temperament (optional)
    - is_vaccinated (optional, boolean)
    - is_neutered (optional, boolean)
    - owner_contact (required)
    - photo (required, file)
    """
    try:
        data = request.form.to_dict()
        
        # Converter booleanos
        if "is_vaccinated" in data:
            data["is_vaccinated"] = data["is_vaccinated"].lower() == "true"
        if "is_neutered" in data:
            data["is_neutered"] = data["is_neutered"].lower() == "true"
        
        validate_pet_data(data)

        photo_file = request.files.get("photo")
        validate_pet_photo(photo_file, existing_photo_url=None)
        
        pet = Pet(
            name=data["name"],
            species=data["species"],
            breed=data.get("breed"),
            age_years=int(data["age_years"]) if data.get("age_years") else None,
            description=data.get("description"),
            temperament=data.get("temperament"),
            is_vaccinated=data.get("is_vaccinated", False),
            is_neutered=data.get("is_neutered", False),
            owner_contact=data["owner_contact"].strip(),
        )
        
        try:
            pet.photo_url = upload_file(photo_file)
        except ValueError as e:
            raise ValidationError(str(e))
        
        db.session.add(pet)
        db.session.commit()
        
        return jsonify({
            "message": "Pet criado com sucesso",
            "pet": _serialize_pet(pet, admin=True)
        }), 201
    
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erro ao criar pet: {str(e)}")


@pets_bp.route("/<pet_id>", methods=["PUT"])
@jwt_required()
def update_pet(pet_id):
    """
    Atualiza um pet existente.
    PUT /api/pets/<pet_id>
    Header: Authorization: Bearer <token>
    Content-Type: multipart/form-data
    """
    try:
        pet = _get_pet(pet_id)
        
        if not pet:
            raise NotFoundError("Pet não encontrado")
        
        data = request.form.to_dict()
        
        # Atualizar campos
        if "name" in data:
            pet.name = data["name"]
        if "species" in data:
            pet.species = data["species"]
        if "breed" in data:
            pet.breed = data["breed"]
        if "age_years" in data and data["age_years"]:
            pet.age_years = int(data["age_years"])
        if "description" in data:
            pet.description = data["description"]
        if "temperament" in data:
            pet.temperament = data["temperament"]
        if "status" in data:
            pet.status = data["status"]
        if "is_vaccinated" in data:
            pet.is_vaccinated = data["is_vaccinated"].lower() == "true"
        if "is_neutered" in data:
            pet.is_neutered = data["is_neutered"].lower() == "true"
        if "owner_contact" in data:
            pet.owner_contact = data["owner_contact"].strip()

        validate_pet_data(_pet_validation_data(pet, data))

        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            if pet.photo_url:
                delete_file(pet.photo_url)
            try:
                pet.photo_url = upload_file(photo_file)
            except ValueError as e:
                raise ValidationError(str(e))

        validate_pet_photo(photo_file, existing_photo_url=pet.photo_url)
        
        db.session.commit()
        
        return jsonify({
            "message": "Pet atualizado com sucesso",
            "pet": _serialize_pet(pet, admin=True)
        }), 200
    
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erro ao atualizar pet: {str(e)}")


@pets_bp.route("/<pet_id>", methods=["DELETE"])
@jwt_required()
def delete_pet(pet_id):
    """
    Deleta um pet.
    DELETE /api/pets/<pet_id>
    Header: Authorization: Bearer <token>
    """
    try:
        pet = _get_pet(pet_id)
        
        if not pet:
            raise NotFoundError("Pet não encontrado")
        
        # Deletar foto
        if pet.photo_url:
            delete_file(pet.photo_url)
        
        db.session.delete(pet)
        db.session.commit()
        
        return jsonify({"message": "Pet deletado com sucesso"}), 200
    
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erro ao deletar pet: {str(e)}")


@pets_bp.route("/<pet_id>/photo", methods=["POST"])
@jwt_required()
def upload_pet_photo(pet_id):
    """
    Faz upload de foto de um pet existente.
    POST /api/pets/<pet_id>/photo
    Header: Authorization: Bearer <token>
    Content-Type: multipart/form-data
    Body: photo (file)
    """
    try:
        pet = _get_pet(pet_id)
        
        if not pet:
            raise NotFoundError("Pet não encontrado")
        
        if "photo" not in request.files:
            raise ValidationError("Nenhum arquivo foi enviado")
        
        file = request.files["photo"]
        if not file.filename:
            raise ValidationError("Arquivo inválido")
        
        # Deletar foto anterior
        if pet.photo_url:
            delete_file(pet.photo_url)
        
        try:
            pet.photo_url = upload_file(file)
        except ValueError as e:
            raise ValidationError(str(e))
        
        db.session.commit()
        
        return jsonify({
            "message": "Foto enviada com sucesso",
            "photo_url": pet.photo_url
        }), 200
    
    except (NotFoundError, ValidationError) as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erro ao fazer upload de foto: {str(e)}")
