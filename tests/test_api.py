"""
Testes da API.
Execute com: pytest tests/test_api.py
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import Pet, Admin
from app.auth import register_admin
import json


@pytest.fixture
def app():
    """Cria uma aplicação Flask para testes."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente Flask para fazer requisições."""
    return app.test_client()


@pytest.fixture
def admin_token(app):
    """Cria um admin e retorna seu token."""
    with app.app_context():
        admin = register_admin("admin@test.com", "password123")
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=admin.id)
        return token


class TestAuth:
    """Testes de autenticação."""
    
    def test_login_success(self, client, app):
        """Testa login bem-sucedido."""
        with app.app_context():
            register_admin("admin@test.com", "password123")
        
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "password123"},
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert data["admin"]["email"] == "admin@test.com"
    
    def test_login_invalid_credentials(self, client):
        """Testa login com credenciais inválidas."""
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "wrong"},
            content_type="application/json"
        )
        
        assert response.status_code == 401
    
    def test_register_success(self, client):
        """Testa registro bem-sucedido."""
        response = client.post(
            "/api/auth/register",
            json={"email": "novo@test.com", "password": "password123"},
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["admin"]["email"] == "novo@test.com"
    
    def test_register_invalid_email(self, client):
        """Testa registro com email inválido."""
        response = client.post(
            "/api/auth/register",
            json={"email": "invalid", "password": "password123"},
            content_type="application/json"
        )
        
        assert response.status_code == 400


class TestPets:
    """Testes de pets."""
    
    def test_list_pets_empty(self, client):
        """Testa listagem de pets vazia."""
        response = client.get("/api/pets")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 0
        assert len(data["pets"]) == 0
    
    def test_list_pets_with_data(self, client, app):
        """Testa listagem de pets com dados."""
        with app.app_context():
            pet = Pet(
                name="Miau",
                species="gato",
                breed="Siamês",
                age_years=2
            )
            db.session.add(pet)
            db.session.commit()
        
        response = client.get("/api/pets")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 1
        assert data["pets"][0]["name"] == "Miau"
    
    def test_get_pet_success(self, client, app):
        """Testa obtenção de pet específico."""
        with app.app_context():
            pet = Pet(
                name="Miau",
                species="gato",
                breed="Siamês"
            )
            db.session.add(pet)
            db.session.commit()
            pet_id = pet.id
        
        response = client.get(f"/api/pets/{pet_id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Miau"
    
    def test_get_pet_not_found(self, client):
        """Testa obtenção de pet inexistente."""
        response = client.get("/api/pets/invalid-id")
        
        assert response.status_code == 404
    
    def test_create_pet_unauthorized(self, client):
        """Testa criação de pet sem autenticação."""
        response = client.post(
            "/api/pets",
            data={"name": "Miau", "species": "gato"}
        )
        
        assert response.status_code == 401
    
    def test_create_pet_success(self, client, admin_token):
        """Testa criação bem-sucedida de pet."""
        response = client.post(
            "/api/pets",
            data={
                "name": "Miau",
                "species": "gato",
                "breed": "Siamês",
                "age_years": "2"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["pet"]["name"] == "Miau"
        assert data["pet"]["species"] == "gato"
    
    def test_create_pet_missing_required_fields(self, client, admin_token):
        """Testa criação de pet com campos obrigatórios faltando."""
        response = client.post(
            "/api/pets",
            data={"name": "Miau"},  # Falta species
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
    
    def test_update_pet_success(self, client, app, admin_token):
        """Testa atualização bem-sucedida de pet."""
        with app.app_context():
            pet = Pet(name="Miau", species="gato")
            db.session.add(pet)
            db.session.commit()
            pet_id = pet.id
        
        response = client.put(
            f"/api/pets/{pet_id}",
            data={"name": "Novo Nome"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["pet"]["name"] == "Novo Nome"
    
    def test_delete_pet_success(self, client, app, admin_token):
        """Testa exclusão bem-sucedida de pet."""
        with app.app_context():
            pet = Pet(name="Miau", species="gato")
            db.session.add(pet)
            db.session.commit()
            pet_id = pet.id
        
        response = client.delete(
            f"/api/pets/{pet_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # Verificar se foi deletado
        response = client.get(f"/api/pets/{pet_id}")
        assert response.status_code == 404
    
    def test_list_pets_by_status(self, client, app):
        """Testa filtro de status na listagem."""
        with app.app_context():
            pet1 = Pet(name="Miau", species="gato", status="available")
            pet2 = Pet(name="Rex", species="cão", status="adopted")
            db.session.add_all([pet1, pet2])
            db.session.commit()
        
        response = client.get("/api/pets?status=available")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 1
        assert data["pets"][0]["name"] == "Miau"


class TestHealthCheck:
    """Testes de health check."""
    
    def test_health_check(self, client):
        """Testa endpoint de health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
