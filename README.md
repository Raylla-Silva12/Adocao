# Sistema de Adoção de Pets

Plataforma web completa para adoção de gatos e cães, com site público, painel administrativo e API REST. Otimizada para Google Cloud Run.

## Funcionalidades

- Catálogo público de pets com filtros por espécie e status
- Painel admin com autenticação JWT
- CRUD de pets com upload de fotos (local ou Google Cloud Storage)
- PostgreSQL + SQLAlchemy
- Docker Compose para desenvolvimento local
- Deploy automatizado para Google Cloud Run

## Início rápido

### Docker Compose (recomendado)

```bash
docker-compose up
```

Acesse: http://localhost:8080 — admin: `admin@example.com` / `admin123`

### Sem Docker

Requer PostgreSQL. Copie `.env.example` para `.env` e ajuste as credenciais.

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

### Testes

```bash
pytest
```

## Deploy no Google Cloud

```bash
# Setup completo (Cloud SQL + Cloud Run)
./scripts/setup-cloud-sql.sh seu-project-id us-central1

# Windows
.\scripts\setup-cloud-sql.ps1 seu-project-id us-central1

# Apenas build e deploy (sem criar infra)
./scripts/deploy-gcp.sh seu-project-id
```

Detalhes em [docs/CLOUD_SQL.md](docs/CLOUD_SQL.md).

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | Guia rápido de uso |
| [docs/BACKEND.md](docs/BACKEND.md) | API REST completa |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Estrutura e padrões do código |
| [docs/CLOUD_SQL.md](docs/CLOUD_SQL.md) | Deploy no Google Cloud |
| [docs/DATABASE.md](docs/DATABASE.md) | Modelo de dados |
| [docs/insomnia_collection.json](docs/insomnia_collection.json) | Collection para testes da API |

## Estrutura do projeto

```
app/
├── api/              # Endpoints REST (auth, pets)
├── web/              # Interface HTML (site + admin)
├── utils/            # Uploads, validação, erros
├── templates/        # Templates Jinja2
├── static/           # CSS, JS, imagens
├── models.py         # Modelos SQLAlchemy
├── config.py         # Configurações por ambiente
└── factory.py        # Factory da aplicação Flask

docs/                 # Documentação
scripts/              # Scripts de deploy e setup GCP
tests/                # Testes com pytest
```

## Credenciais padrão (desenvolvimento)

```
Email: admin@example.com
Senha: admin123
```

Altere em produção via variáveis de ambiente (`ADMIN_EMAIL`, `ADMIN_PASSWORD`, `JWT_SECRET_KEY`).

## Comandos úteis

```bash
make dev              # Docker Compose
make test             # Executar testes
make db-seed          # Popular banco
python manage_db.py upgrade  # Migrar schema em DB existente
python check_setup.py # Verificar estrutura do projeto
```

## Stack

Flask 3 · PostgreSQL 15 · SQLAlchemy 2 · JWT · Docker · Gunicorn · Google Cloud Run
