"""
Modelos de dados.
"""
from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Pet(db.Model):
    """Modelo para Pet (Gato, Cão, etc)."""
    __tablename__ = "pets"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, index=True)
    species = db.Column(db.String(50), nullable=False)  # gato, cão, etc
    breed = db.Column(db.String(255), nullable=True)
    age_years = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    temperament = db.Column(db.String(255), nullable=True)  # dócil, tímido, brincalhão, etc
    is_vaccinated = db.Column(db.Boolean, default=False)
    is_neutered = db.Column(db.Boolean, default=False)
    photo_url = db.Column(db.String(500), nullable=True)
    owner_contact = db.Column(db.String(50), nullable=True)  # só visível no admin
    status = db.Column(
        db.String(50),
        default="available",
        nullable=False,
        index=True
    )  # available, adopted, pending
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Pet {self.name}>"
    
    def to_dict(self, admin=False):
        """Converte o modelo para dicionário. Campos internos só com admin=True."""
        data = {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age_years": self.age_years,
            "description": self.description,
            "temperament": self.temperament,
            "is_vaccinated": self.is_vaccinated,
            "is_neutered": self.is_neutered,
            "photo_url": self.photo_url,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if admin:
            data["owner_contact"] = self.owner_contact
        return data


class Admin(db.Model):
    """Modelo para usuários Admin."""
    __tablename__ = "admins"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Admin {self.email}>"
