# Backend Flask - Sistema de Adoção de Pets

API REST completa para um sistema de adoção de pets, otimizada para rodar no Google Cloud Run.

## Funcionalidades

- ✅ **Cadastro de Animais**: Criar, ler, atualizar e deletar pets
- ✅ **Upload de Fotos**: Suporte a local e Google Cloud Storage
- ✅ **Listagem com Filtros**: Filtrar por status e paginação
- ✅ **Edição de Pets**: Atualizar informações e fotos
- ✅ **Exclusão**: Deletar pets com limpeza de arquivos
- ✅ **PostgreSQL**: Banco de dados relacional
- ✅ **SQLAlchemy**: ORM robusto
- ✅ **JWT Admin**: Autenticação de administradores
- ✅ **Docker**: Containerizado e pronto para Cloud Run
- ✅ **Health Check**: Endpoint para verificação de saúde

## Stack Técnico

- **Framework**: Flask
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **File Upload**: Werkzeug + Google Cloud Storage
- **Container**: Docker + Gunicorn
- **Cloud**: Google Cloud Run

## Instalação Local

### Pré-requisitos

- Python 3.11+
- PostgreSQL 12+
- pip

### Setup

1. **Clone o repositório**
```bash
git clone <repo>
cd adocao-gatos
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Inicialize o banco de dados**
```bash
python seed.py
```

6. **Inicie o servidor**
```bash
python app.py
```

O servidor estará disponível em `http://localhost:8080`

## Variáveis de Ambiente

```env
# Flask
FLASK_ENV=development

# Database
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=adocao_gatos

# JWT
JWT_SECRET_KEY=sua_chave_secreta_muito_longa

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# Google Cloud Storage (opcional)
GCS_BUCKET=seu-bucket-name

# Upload
UPLOAD_FOLDER=uploads
```

## Endpoints da API

### Autenticação

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Resposta** (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "id": "admin-id",
    "email": "admin@example.com"
  }
}
```

#### Obter Dados do Admin
```http
GET /api/auth/me
Authorization: Bearer <token>
```

#### Registrar Admin
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "novo@example.com",
  "password": "senha123"
}
```

### Pets

#### Listar Pets
```http
GET /api/pets?status=available&limit=20&offset=0
```

**Parâmetros**:
- `status` (opcional): `available`, `adopted`, `pending`
- `limit` (opcional, padrão: 20): Máximo de resultados
- `offset` (opcional, padrão: 0): Deslocamento para paginação

**Resposta** (200):
```json
{
  "total": 10,
  "limit": 20,
  "offset": 0,
  "pets": [
    {
      "id": "pet-id",
      "name": "Miau",
      "species": "gato",
      "breed": "Siamês",
      "age_years": 2,
      "description": "Gato dócil e carinhoso",
      "temperament": "dócil",
      "is_vaccinated": true,
      "is_neutered": true,
      "photo_url": "/uploads/image.jpg",
      "status": "available",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

#### Obter Pet Específico
```http
GET /api/pets/<pet_id>
```

#### Criar Pet
```http
POST /api/pets
Authorization: Bearer <token>
Content-Type: multipart/form-data

name=Miau&species=gato&breed=Siamês&age_years=2&photo=@image.jpg
```

**Campos**:
- `name` (obrigatório)
- `species` (obrigatório): gato, cão, etc
- `breed` (opcional)
- `age_years` (opcional)
- `description` (opcional)
- `temperament` (opcional)
- `is_vaccinated` (opcional)
- `is_neutered` (opcional)
- `photo` (opcional): arquivo de imagem

#### Atualizar Pet
```http
PUT /api/pets/<pet_id>
Authorization: Bearer <token>
Content-Type: multipart/form-data

name=Novo Nome&status=adopted
```

#### Deletar Pet
```http
DELETE /api/pets/<pet_id>
Authorization: Bearer <token>
```

#### Upload de Foto
```http
POST /api/pets/<pet_id>/photo
Authorization: Bearer <token>
Content-Type: multipart/form-data

photo=@image.jpg
```

### Health Check
```http
GET /health
```

## Deploy no Google Cloud Run

### Pré-requisitos

- Google Cloud Project configurado
- Cloud SQL com PostgreSQL
- Cloud Storage bucket (opcional, para fotos)
- Google Cloud CLI instalado

### Passo 1: Prepare o projeto

```bash
# Configure as variáveis de ambiente
export PROJECT_ID=seu-project-id
export REGION=us-central1
export SERVICE_NAME=adocao-gatos

# Configure a autenticação
gcloud auth login
gcloud config set project $PROJECT_ID
```

### Passo 2: Crie a instância PostgreSQL (se não existir)

```bash
gcloud sql instances create adocao-db \
  --database-version POSTGRES_15 \
  --region $REGION \
  --tier db-f1-micro
```

### Passo 3: Crie o banco de dados

```bash
gcloud sql databases create adocao_gatos \
  --instance adocao-db
```

### Passo 4: Configure as variáveis de ambiente no Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/<PROJECT_ID>:us-central1:adocao-db,\
DB_USER=postgres,\
DB_PASSWORD=sua_senha,\
DB_NAME=adocao_gatos,\
JWT_SECRET_KEY=sua_chave_secreta,\
ADMIN_EMAIL=admin@example.com,\
ADMIN_PASSWORD=admin123 \
  --add-cloudsql-instances <PROJECT_ID>:us-central1:adocao-db
```

### Passo 5: Inicialize o banco de dados

```bash
# Crie um job único para rodar o seed
gcloud run jobs create adocao-seed \
  --source . \
  --region $REGION \
  --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/<PROJECT_ID>:us-central1:adocao-db,\
DB_USER=postgres,\
DB_PASSWORD=sua_senha,\
DB_NAME=adocao_gatos \
  --add-cloudsql-instances <PROJECT_ID>:us-central1:adocao-db \
  --execute-now
```

Ou use Cloud Build:

```bash
gcloud builds submit --config=cloudbuild.yaml
```

## Estrutura do Projeto

```
adocao-gatos/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configurações
│   ├── extensions.py          # Extensões (SQLAlchemy, JWT, etc)
│   ├── models.py              # Modelos de dados
│   ├── auth.py                # Lógica de autenticação
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py            # Endpoints de autenticação
│   │   └── pets.py            # Endpoints de pets
│   └── utils/
│       ├── __init__.py
│       ├── errors.py          # Classes de erro
│       ├── uploads.py         # Gerenciamento de uploads
│       └── validators.py      # Validadores
├── app.py                     # Entry point
├── seed.py                    # Seed do banco de dados
├── manage_db.py               # CLI para gerenciar DB
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Dockerfile para Cloud Run
├── .dockerignore              # Arquivos a ignorar no Docker
├── cloudbuild.yaml            # Config para Cloud Build
├── app.yaml                   # Config para App Engine
├── README.md                  # Este arquivo
└── .env.example               # Template de variáveis de ambiente
```

## Gerenciamento do Banco de Dados

### Inicializar
```bash
python manage_db.py init-db
```

### Resetar (drop + create + seed)
```bash
python manage_db.py reset-db
```

### Criar novo admin
```bash
python manage_db.py seed-admin
```

### Usar Flask-Migrate para migrações (opcional)

```bash
# Criar uma migração após alterar modelos
flask db migrate -m "Descrição da mudança"

# Aplicar a migração
flask db upgrade

# Ver histórico
flask db history
```

## Testes

```bash
# Instale as dependências de teste
pip install pytest pytest-cov

# Execute os testes
pytest

# Com cobertura
pytest --cov=app tests/
```

## Segurança

- ✅ JWT para autenticação
- ✅ Senhas com hash usando Werkzeug
- ✅ CORS configurável
- ✅ Validação de entrada em todos os endpoints
- ✅ Limite de tamanho de arquivo (10MB)
- ✅ Sanitização de nomes de arquivo

### Recomendações para Produção

1. **JWT_SECRET_KEY**: Use uma chave aleatória e segura
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Database**: Use senha forte para PostgreSQL

3. **CORS**: Configure origins específicos em produção

4. **HTTPS**: Cloud Run fornece HTTPS automaticamente

5. **Variáveis de Ambiente**: Use Secret Manager do GCP

## Troubleshooting

### Erro de conexão com banco de dados

```
Verifique as variáveis de ambiente DB_HOST, DB_USER, DB_PASSWORD
```

### Erro ao fazer upload de arquivo

```
- Verifique permissões da pasta 'uploads'
- Para GCS, configure GCS_BUCKET e credenciais
```

### JWT Token inválido

```
- Regere o token com o novo JWT_SECRET_KEY
- Verifique se o token não expirou
```

## Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
2. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
3. Push para a branch (`git push origin feature/AmazingFeature`)
4. Abra um Pull Request

## Licença

MIT License - veja LICENSE.md para detalhes

## Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação do Flask
- Verifique a documentação do Cloud Run
