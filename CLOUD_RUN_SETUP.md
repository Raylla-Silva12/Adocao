# 🚀 Deploy no Cloud Run com Cloud SQL

## Opção Rápida (Recomendado - Automatizado)

Se você tem Google Cloud CLI instalado:

```bash
# 1. Abra o terminal na pasta do projeto
cd c:\Users\Exterminador\ 2\ MIL\Desktop\Adocao

# 2. Execute o setup (cria Cloud SQL + faz deploy)
bash setup-cloud-sql.sh seu-project-id us-central1
```

Substitua `seu-project-id` pelo seu Project ID do Google Cloud.

**O que ele faz:**
- ✅ Cria instância PostgreSQL no Cloud SQL
- ✅ Configura banco de dados
- ✅ Gera senhas seguras
- ✅ Faz build e deploy no Cloud Run
- ✅ Conecta Cloud SQL ao Cloud Run

Tempo estimado: **~10 minutos**

---

## Opção Manual (Passo a Passo)

### Passo 1: Preparar Google Cloud

```bash
# Instalar Google Cloud CLI se não tiver
# https://cloud.google.com/sdk/docs/install

# Fazer login
gcloud auth login
gcloud auth application-default login

# Configurar projeto
gcloud config set project seu-project-id
```

### Passo 2: Habilitar APIs

```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Passo 3: Criar instância Cloud SQL

```bash
gcloud sql instances create adocao-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1
```

### Passo 4: Criar banco de dados

```bash
gcloud sql databases create adocao_gatos \
    --instance=adocao-db
```

### Passo 5: Criar usuário e senha

```bash
gcloud sql users set-password postgres \
    --instance=adocao-db \
    --password=sua-senha-super-secreta
```

### Passo 6: Obter connection name

```bash
gcloud sql instances describe adocao-db \
    --format='value(connectionName)'
```

Vai retornar algo como: `seu-projeto:us-central1:adocao-db`

### Passo 7: Fazer deploy

```bash
gcloud run deploy adocao-gatos \
    --image gcr.io/seu-project-id/adocao-gatos:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/seu-projeto:us-central1:adocao-db,\
DB_USER=postgres,\
DB_PASSWORD=sua-senha-super-secreta,\
DB_NAME=adocao_gatos,\
JWT_SECRET_KEY=chave-super-secreta-aqui,\
ADMIN_EMAIL=admin@example.com,\
ADMIN_PASSWORD=admin123 \
    --add-cloudsql-instances seu-projeto:us-central1:adocao-db
```

---

## ✅ Verificar se funcionou

Depois do deploy, você vai receber uma URL como:
```
https://adocao-gatos-xxx.run.app
```

Teste acessando:
```bash
curl https://adocao-gatos-xxx.run.app/health
```

Deve retornar:
```json
{
  "status": "ok",
  "database": "connected"
}
```

---

## 💰 Custos

**Cloud SQL (db-f1-micro):**
- Primeiros 12 meses: GRÁTIS (Google Cloud free tier)
- Depois: ~$4/mês

**Cloud Run:**
- Primeiros 2 milhões de requisições/mês: GRÁTIS
- 512MB de memória: GRÁTIS para este plano

Total estimado: **Praticamente grátis** para um projeto pessoal

---

## 🔒 Segurança

Para produção, considere:

1. **Usar Secret Manager** em vez de env vars:
   ```bash
   gcloud secrets create db-password --data-file=-
   gcloud run deploy adocao-gatos ... --set-secrets=DB_PASSWORD=db-password:latest
   ```

2. **Usar Cloud Armor** para proteger a API

3. **Habilitar SSL/TLS** (Cloud Run faz isso automaticamente)

4. **Usar VPC Connector** para isolar a conexão ao banco

Mas para um projeto pessoal inicial, as env vars funcionam bem.

---

## ❓ Precisa de ajuda?

Se der erro, verifique:

- ✅ Google Cloud CLI instalado: `gcloud --version`
- ✅ Autenticado: `gcloud auth list`
- ✅ Projeto configurado: `gcloud config get project`
- ✅ APIs habilitadas: `gcloud services list --enabled`
