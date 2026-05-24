# Guia de Arquitetura e Padrões

## 📁 Estrutura do Projeto

```
adocao-gatos/
│
├── app/                          # Pacote principal da aplicação
│   ├── __init__.py              # Inicializador do pacote
│   ├── config.py                # Configurações por ambiente
│   ├── extensions.py            # Extensões do Flask (db, migrate, jwt)
│   ├── models.py                # Modelos SQLAlchemy
│   ├── auth.py                  # Lógica de autenticação
│   │
│   ├── api/                     # Blueprints com rotas REST
│   │   ├── __init__.py
│   │   ├── auth.py              # Endpoints de autenticação
│   │   └── pets.py              # Endpoints de pets (CRUD)
│   │
│   ├── web/                     # Interface HTML (site + admin)
│   │   ├── routes.py
│   │   └── email_templates.py
│   │
│   ├── templates/               # Templates Jinja2
│   ├── static/                  # CSS, JS, imagens
│   │
│   └── utils/                   # Utilitários
│       ├── __init__.py
│       ├── errors.py            # Classes de erro customizadas
│       ├── uploads.py           # Gerenciamento de upload de arquivos
│       └── validators.py        # Validadores de dados
│
├── tests/                        # Testes unitários e integração
│   ├── __init__.py
│   └── test_api.py              # Testes dos endpoints
│
├── uploads/                      # Pasta de uploads (gitignored)
│   └── *.jpg, *.png, etc
│
├── docs/                         # Documentação
│   ├── QUICKSTART.md
│   ├── BACKEND.md
│   ├── ARCHITECTURE.md
│   ├── CLOUD_SQL.md
│   ├── DATABASE.md
│   └── insomnia_collection.json
│
├── scripts/                      # Deploy e setup GCP
│   ├── setup-cloud-sql.sh
│   ├── setup-cloud-sql.ps1
│   ├── setup-gcs.ps1
│   ├── deploy-gcp.sh
│   └── deploy-gcp.bat
│
├── app.py                        # Entry point da aplicação
├── seed.py                       # Script para popular o banco
├── manage_db.py                  # CLI para gerenciar banco de dados
├── gunicorn_config.py            # Configuração do Gunicorn
│
├── Dockerfile                    # Container para Cloud Run
├── .dockerignore                 # Arquivos ignorados no Docker
├── docker-compose.yml            # Orquestração local
│
├── requirements.txt              # Dependências Python
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore                    # Arquivos ignorados pelo Git
├── Makefile                      # Comandos úteis
│
├── cloudbuild.yaml               # CI/CD do Google Cloud
│
└── README.md                     # Overview do projeto
```

## 🏗️ Padrões de Arquitetura

### 1. Factory Pattern

A aplicação usa o factory pattern para criar instâncias do Flask:

```python
# app.py
def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    db.init_app(app)
    jwt.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(pets_bp)
    
    return app

app = create_app()
```

**Benefícios:**
- Fácil criar múltiplas instâncias para testes
- Suportar múltiplos ambientes (dev, test, prod)
- Melhor testabilidade

### 2. Blueprints

Rotas são organizadas em blueprints separados por domínio:

```python
# app/api/auth.py
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    pass

# app/api/pets.py
pets_bp = Blueprint("pets", __name__)

@pets_bp.route("", methods=["GET"])
def list_pets():
    pass
```

**Benefícios:**
- Separação de responsabilidades
- Fácil manutenção
- Reutilizável em diferentes apps

### 3. Application Context

Operações de banco de dados usam app context:

```python
with app.app_context():
    db.create_all()
    admin = Admin.query.first()
```

### 4. Extensões Inicializadas Globalmente

```python
# app/extensions.py
db = SQLAlchemy()
jwt = JWTManager()

# app/config.py
db.init_app(app)
jwt.init_app(app)
```

**Benefícios:**
- Importável em qualquer arquivo da app
- Sem circular imports

## 🗄️ Padrão de Modelos

### Modelo Base

```python
class Pet(db.Model):
    __tablename__ = "pets"
    
    # ID
    id = db.Column(db.String(36), primary_key=True, 
                  default=lambda: str(uuid.uuid4()))
    
    # Dados
    name = db.Column(db.String(255), nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Serializa para JSON"""
        return {
            "id": self.id,
            "name": self.name,
            # ...
        }
```

**Padrões:**
- UUIDs para IDs (melhor para distribuição)
- `created_at` e `updated_at` em todo modelo
- Método `to_dict()` para serialização
- Índices em campos pesquisáveis
- NOT NULL explícito

## 🔐 Padrão de Segurança

### Autenticação JWT

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/api/protected")
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    # ...
```

### Validação de Entrada

```python
def validate_pet_data(data):
    if not data.get("name"):
        raise ValidationError("Nome é obrigatório")
    if len(data.get("name", "")) > 255:
        raise ValidationError("Nome muito longo")
```

### Tratamento de Erros

```python
class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_api_error(e):
    return jsonify({"error": e.message}), e.status_code
```

## 📡 Padrão de Endpoints

### Listar (GET /resource)

```python
@pets_bp.route("", methods=["GET"])
def list_pets():
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    total = Pet.query.count()
    pets = Pet.query.limit(limit).offset(offset).all()
    
    return jsonify({
        "total": total,
        "limit": limit,
        "offset": offset,
        "pets": [pet.to_dict() for pet in pets]
    }), 200
```

### Obter Um (GET /resource/:id)

```python
@pets_bp.route("/<pet_id>", methods=["GET"])
def get_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet:
        raise NotFoundError("Pet não encontrado")
    return jsonify(pet.to_dict()), 200
```

### Criar (POST /resource)

```python
@pets_bp.route("", methods=["POST"])
@jwt_required()
def create_pet():
    validate_pet_data(request.form.to_dict())
    
    pet = Pet(**request.form.to_dict())
    db.session.add(pet)
    db.session.commit()
    
    return jsonify({
        "message": "Pet criado com sucesso",
        "pet": pet.to_dict()
    }), 201
```

### Atualizar (PUT /resource/:id)

```python
@pets_bp.route("/<pet_id>", methods=["PUT"])
@jwt_required()
def update_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet:
        raise NotFoundError("Pet não encontrado")
    
    for key, value in request.form.items():
        if hasattr(pet, key):
            setattr(pet, key, value)
    
    db.session.commit()
    return jsonify({"message": "Updated", "pet": pet.to_dict()}), 200
```

### Deletar (DELETE /resource/:id)

```python
@pets_bp.route("/<pet_id>", methods=["DELETE"])
@jwt_required()
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet:
        raise NotFoundError("Pet não encontrado")
    
    db.session.delete(pet)
    db.session.commit()
    
    return jsonify({"message": "Pet deletado"}), 200
```

## 📊 Padrão de Resposta

### Sucesso

```json
{
  "total": 10,
  "limit": 20,
  "offset": 0,
  "pets": [...]
}
```

ou

```json
{
  "message": "Success message",
  "data": {...}
}
```

### Erro

```json
{
  "error": "Error message"
}
```

### Status Codes

| Código | Significado |
|--------|-------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Não autorizado |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Dados semânticos inválidos |
| 500 | Internal Server Error - Erro do servidor |

## 🧪 Padrão de Testes

```python
@pytest.fixture
def app():
    """Cria app para testes."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente para fazer requisições."""
    return app.test_client()

class TestPets:
    def test_list_empty(self, client):
        response = client.get("/api/pets")
        assert response.status_code == 200
```

## 🚀 Deployment Stages

### Desenvolvimento

```bash
# Docker Compose local
docker-compose up

# Ou Flask direto
python app.py
```

### Testes

```bash
pytest
pytest --cov=app
```

### Staging (antes de produção)

```bash
# Deploy em staging no Cloud Run
gcloud run deploy adocao-gatos-staging ...
```

### Produção

```bash
# Deploy com Cloud Build
gcloud builds submit --config=cloudbuild.yaml
```

## 📈 Escalabilidade

### Horizontal (mais instâncias)

Cloud Run auto-escala baseado em:
- Requisições por segundo
- CPU
- Memória

### Vertical (mais recursos)

```bash
gcloud run deploy adocao-gatos \
  --cpu 2 \
  --memory 1Gi
```

### Cache

Implementar com Redis:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route("/api/pets")
@cache.cached(timeout=300)
def list_pets():
    pass
```

## 🔄 CI/CD Pipeline

```
GitHub Push
    ↓
Cloud Build Trigger
    ↓
Docker Build & Push
    ↓
Tests (pytest)
    ↓
Deploy to Cloud Run
    ↓
Health Check
```

## 📚 Referências

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [12 Factor App](https://12factor.net/)
