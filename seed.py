"""
Script para inicializar o banco de dados com um admin padrão.
Execute com: python seed.py
"""
import os
from app import create_app
from app.extensions import db
from app.models import Admin, Pet
from app.auth import register_admin


def seed_database():
    """Popula o banco de dados com dados iniciais."""
    app = create_app()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se admin já existe
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        existing_admin = Admin.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            try:
                admin = register_admin(admin_email, admin_password)
                print(f"✓ Admin criado: {admin.email}")
            except ValueError as e:
                print(f"✗ Erro ao criar admin: {e}")
        else:
            print(f"✓ Admin já existe: {admin_email}")

        if Pet.query.count() == 0:
            demos = [
                Pet(
                    name="Mingau",
                    species="gato",
                    breed="SRD",
                    age_years=2,
                    description="Calmo e carinhoso. Adora colo e janela ensolarada.",
                    temperament="dócil",
                    is_vaccinated=True,
                    is_neutered=True,
                    status="available",
                ),
                Pet(
                    name="Pipoca",
                    species="gato",
                    breed="SRD",
                    age_years=1,
                    description="Cheia de energia, ideal para famílias ativas.",
                    temperament="brincalhona",
                    is_vaccinated=True,
                    is_neutered=False,
                    status="available",
                ),
                Pet(
                    name="Thor",
                    species="gato",
                    breed="Persa",
                    age_years=4,
                    description="Majestoso e tranquilo. Convive bem com crianças.",
                    temperament="tranquilo",
                    is_vaccinated=True,
                    is_neutered=True,
                    status="available",
                ),
            ]
            for pet in demos:
                db.session.add(pet)
            db.session.commit()
            print(f"✓ {len(demos)} gatos de exemplo criados")
        
        print("✓ Banco de dados inicializado com sucesso!")


if __name__ == "__main__":
    seed_database()
