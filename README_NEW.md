# 🐱 Sistema de Adoção de Pets - Backend Flask

**API REST completa e profissional para um sistema de adoção de pets, otimizado para Google Cloud Run.**

## ✨ Features

- ✅ **CRUD Completo** - Cadastro, leitura, atualização e exclusão de pets
- ✅ **Upload de Fotos** - Suporte a local e Google Cloud Storage
- ✅ **Autenticação JWT** - Endpoints protegidos com tokens JWT
- ✅ **Admin Panel** - Sistema de autenticação de administradores
- ✅ **PostgreSQL** - Banco de dados relacional robusto
- ✅ **SQLAlchemy ORM** - Mapeamento objeto-relacional
- ✅ **Docker** - Containerizado para Cloud Run
- ✅ **CI/CD** - Cloud Build integration
- ✅ **Testes** - Cobertura de testes com pytest
- ✅ **Validação** - Validação completa de dados de entrada
- ✅ **Health Check** - Endpoint de health check para Cloud Run

## 🚀 Quick Start (5 minutos)

### Com Docker Compose

```bash
# Clone o repositório
git clone <repo>
cd adocao-gatos

# Inicie tudo com Docker Compose
docker-compose up

# Aguarde a inicialização... pronto! ✅
```

API disponível em: `http://localhost:8080`

### Sem Docker

```bash
# 1. Configure o ambiente
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Edite com suas credenciais PostgreSQL

# 4. Inicialize o banco
python seed.py

# 5. Inicie a API
python app.py
```

## 📖 Documentação

| Documento | Conteúdo |
|-----------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Guia rápido - 5 minutos para começar |
| **[BACKEND.md](BACKEND.md)** | Documentação completa da API |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Padrões, estrutura e decisões arquiteturais |
| **[CLOUD_SQL.md](CLOUD_SQL.md)** | Guia de deploy no Google Cloud Run |

## 🔐 Credenciais Padrão

```
Email:    admin@example.com
Senha:    admin123
```

⚠️ **Altere em produção!**

## 📡 Exemplos de Requisições

### Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Criar Pet

```bash
curl -X POST http://localhost:8080/api/pets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Miau" \
  -F "species=gato" \
  -F "breed=Siamês" \
  -F "age_years=2"
```

### Listar Pets

```bash
curl http://localhost:8080/api/pets
```

Veja mais em **[QUICKSTART.md](QUICKSTART.md)**

## 🛠️ Stack Técnico

```
Backend:      Flask 3.0
Database:     PostgreSQL 15
ORM:          SQLAlchemy 2.0
Auth:         Flask-JWT-Extended
Container:    Docker + Gunicorn
Cloud:        Google Cloud Run
```

## 📁 Estrutura do Projeto

```
app/
├── api/
│   ├── auth.py           # Endpoints de autenticação
│   └── pets.py           # Endpoints de CRUD
├── utils/
│   ├── errors.py         # Classes de erro
│   ├── uploads.py        # Gerenciamento de uploads
│   └── validators.py     # Validação de dados
├── models.py             # Modelos SQLAlchemy
├── auth.py               # Lógica de autenticação
├── config.py             # Configurações
└── extensions.py         # Extensões do Flask
```

Ver documentação completa em **[ARCHITECTURE.md](ARCHITECTURE.md)**

## 🧪 Testes

```bash
# Instale pytest
pip install pytest pytest-cov

# Execute os testes
pytest

# Com cobertura
pytest --cov=app
```

## 🚀 Deploy no Google Cloud Run

### 1. Setup Rápido

```bash
# Configure credenciais do GCP
gcloud auth login
gcloud config set project seu-project-id

# Crie o banco de dados Cloud SQL
gcloud sql instances create adocao-db --database-version POSTGRES_15

# Faça deploy
./deploy.sh seu-project-id
```

### 2. Configuração Manual

Veja instruções detalhadas em **[CLOUD_SQL.md](CLOUD_SQL.md)**

## 📊 Endpoints Principais

| Método | Endpoint | Autenticação | Descrição |
|--------|----------|--------------|-----------|
| POST | `/api/auth/login` | Não | Fazer login |
| GET | `/api/auth/me` | ✅ | Dados do admin |
| GET | `/api/pets` | Não | Listar pets |
| GET | `/api/pets/:id` | Não | Obter pet |
| POST | `/api/pets` | ✅ | Criar pet |
| PUT | `/api/pets/:id` | ✅ | Atualizar pet |
| DELETE | `/api/pets/:id` | ✅ | Deletar pet |
| POST | `/api/pets/:id/photo` | ✅ | Upload de foto |
| GET | `/health` | Não | Health check |

## 🔑 Variáveis de Ambiente

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
JWT_SECRET_KEY=sua_chave_muito_secreta

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

Ver `.env.example` para template completo.

## 🛠️ Comandos Úteis

```bash
# Com Makefile
make help              # Lista todos os comandos
make dev               # Inicia com Docker Compose
make test              # Executa testes
make lint              # Valida código
make format            # Formata com black
make deploy-gcp        # Deploy no GCP

# CLI do banco de dados
python manage_db.py init-db      # Inicializar
python manage_db.py reset-db      # Resetar (⚠️ deleta dados!)
python manage_db.py seed-admin    # Criar novo admin
```

## 🐳 Docker

```bash
# Build
docker build -t adocao-gatos:latest .

# Run
docker run -p 8080:8080 \
  -e DB_HOST=localhost \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e DB_NAME=adocao_gatos \
  adocao-gatos:latest
```

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📋 Checklist para Deploy

- [ ] Alterar `JWT_SECRET_KEY` em produção
- [ ] Alterar credenciais de admin
- [ ] Configurar CORS para dominios específicos
- [ ] Configurar Cloud SQL backup automático
- [ ] Ativar Cloud Logging e Monitoring
- [ ] Testar health check endpoint
- [ ] Configurar SSL/TLS (automático no Cloud Run)
- [ ] Revisar dados sensíveis em logs

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| `Connection refused` | PostgreSQL não está rodando |
| `Database does not exist` | Execute `python seed.py` |
| `Invalid token` | Token expirou ou é inválido, faça login novamente |
| `Permission denied` | Crie pasta: `mkdir -p uploads` |

Veja mais em **[BACKEND.md](BACKEND.md#troubleshooting)**

## 📞 Suporte

- 📖 Leia a documentação completa em [BACKEND.md](BACKEND.md)
- 🐛 Abra uma issue para bugs
- 💡 Discuta features em discussions

## 📄 Licença

MIT License - veja [LICENSE.md](LICENSE.md) para detalhes

## 👨‍💻 Autor

Desenvolvido com ❤️ para um sistema de adoção de pets.

---

**Pronto para começar?** Leia [QUICKSTART.md](QUICKSTART.md) em 5 minutos! 🚀
