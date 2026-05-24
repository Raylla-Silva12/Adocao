# 🚀 QUICKSTART - Backend Flask Adoção de Pets

Guia rápido para começar a usar a API.

## ⚡ Início Rápido (5 minutos)

### 1. Com Docker Compose (Recomendado)

```bash
# Clone ou navegue até o projeto
cd adocao-gatos

# Inicie tudo com um comando
docker-compose up -d

# Aguarde 5 segundos para o banco inicializar
# A API estará disponível em http://localhost:8080
```

✅ Pronto! Banco de dados PostgreSQL + API Flask rodando.

### 2. Local (sem Docker)

```bash
# Instale Python 3.11+
# Configure PostgreSQL

# 1. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Edite .env com suas credenciais PostgreSQL

# 4. Inicialize o banco
python seed.py

# 5. Inicie a API
python app.py
```

## 📝 Primeiros Passos

### 1. Faça Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

Resposta:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "id": "admin-id",
    "email": "admin@example.com"
  }
}
```

Salve o `token` para os próximos passos!

### 2. Crie um Pet

```bash
curl -X POST http://localhost:8080/api/pets \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "name=Miau" \
  -F "species=gato" \
  -F "breed=Siamês" \
  -F "age_years=2"
```

### 3. Liste os Pets

```bash
curl http://localhost:8080/api/pets
```

### 4. Obtenha um Pet Específico

```bash
curl http://localhost:8080/api/pets/PET_ID_AQUI
```

### 5. Atualize um Pet

```bash
curl -X PUT http://localhost:8080/api/pets/PET_ID_AQUI \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "status=adopted"
```

### 6. Delete um Pet

```bash
curl -X DELETE http://localhost:8080/api/pets/PET_ID_AQUI \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 📤 Upload de Fotos

```bash
curl -X POST http://localhost:8080/api/pets/PET_ID_AQUI/photo \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "photo=@/path/to/image.jpg"
```

## 🧪 Testes

```bash
# Execute todos os testes
pytest

# Com cobertura
pytest --cov=app

# Teste específico
pytest tests/test_api.py::TestPets::test_list_pets_empty
```

## 🐳 Docker

### Build da imagem

```bash
make docker-build
# ou
docker build -t adocao-gatos:latest .
```

### Executar a imagem

```bash
make docker-run
# ou
docker run -p 8080:8080 \
  -e DB_HOST=localhost \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e DB_NAME=adocao_gatos \
  adocao-gatos:latest
```

## 🌐 Endpoints Principais

| Método | Endpoint | Autenticação | Descrição |
|--------|----------|--------------|-----------|
| POST | `/api/auth/login` | Não | Fazer login |
| GET | `/api/auth/me` | Sim | Dados do admin |
| GET | `/api/pets` | Não | Listar pets |
| GET | `/api/pets/:id` | Não | Obter um pet |
| POST | `/api/pets` | Sim | Criar pet |
| PUT | `/api/pets/:id` | Sim | Atualizar pet |
| DELETE | `/api/pets/:id` | Sim | Deletar pet |
| POST | `/api/pets/:id/photo` | Sim | Upload de foto |
| GET | `/health` | Não | Health check |

## 🔑 Credenciais Padrão

```
Email: admin@example.com
Password: admin123
```

**⚠️ Altere em produção!**

## 📚 Documentação Completa

Veja o arquivo `BACKEND.md` para documentação completa com:
- Guia de instalação detalhado
- Variáveis de ambiente
- Descrição de todos os endpoints
- Deploy no Google Cloud Run
- Troubleshooting
- E muito mais!

## 🆘 Problemas Comuns

### Erro: "Connection refused"
- PostgreSQL não está rodando
- Verifique: `psql -U postgres -h localhost`

### Erro: "Database does not exist"
- Execute: `python seed.py`

### Erro: "Invalid token"
- Token expirou ou é inválido
- Faça login novamente para obter um novo token

### Erro: "Permission denied" no upload
- Crie a pasta: `mkdir -p uploads`
- Altere permissões: `chmod 755 uploads`

## 💡 Dicas Úteis

### Use Insomnia ou Postman

1. Importe o arquivo `insomnia_collection.json`
2. Configure a variável `baseUrl`
3. Após fazer login, copie o token para `{{ token }}`
4. Pronto para testar todos os endpoints!

### Makefile Commands

```bash
make help           # Lista todos os comandos
make dev            # Inicia com Docker Compose
make test           # Executa testes
make lint           # Valida código
make format         # Formata código com black
make clean          # Remove arquivos temporários
```

## 🚀 Deploy Rápido no GCP

1. Configure o Google Cloud:
```bash
gcloud auth login
gcloud config set project seu-project-id
```

2. Crie o banco de dados:
```bash
gcloud sql instances create adocao-db --database-version POSTGRES_15
gcloud sql databases create adocao_gatos --instance adocao-db
```

3. Faça deploy:
```bash
./deploy.sh seu-project-id
```

## 📞 Suporte

- Leia `BACKEND.md` para documentação completa
- Execute `pytest -v` para verificar se tudo está funcionando
- Verifique os logs: `docker-compose logs -f app`

---

**Happy coding! 🎉**
