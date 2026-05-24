# Configuração para Cloud SQL no Google Cloud Run

## Variáveis de Ambiente para Cloud SQL

### Via Cloud Run Service Account Connection

Se estiver usando Cloud Run com Cloud SQL:

```bash
# Para Unix socket (recomendado)
DB_HOST=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_NAME=adocao_gatos

# Para TCP (menos comum)
DB_HOST=10.0.0.5  # IP privado do Cloud SQL
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_NAME=adocao_gatos
```

## Dockerfile Otimizado para Cloud Run

O Dockerfile incluído usa:
- Python 3.11-slim (imagem base leve)
- Multi-stage build (opcional, para produção)
- Gunicorn com 4 workers
- Health check automático

## Deploy com Cloud SQL

### Passo 1: Crie a instância Cloud SQL

```bash
PROJECT_ID=seu-project-id
REGION=us-central1

gcloud sql instances create adocao-db \
  --database-version POSTGRES_15 \
  --region $REGION \
  --tier db-f1-micro \
  --backup-start-time=02:00 \
  --retained-backups-count=7 \
  --transaction-log-retention-days=7
```

### Passo 2: Crie o banco de dados

```bash
gcloud sql databases create adocao_gatos \
  --instance=adocao-db
```

### Passo 3: Configure o usuário

```bash
# Gerar senha aleatória
PASSWORD=$(openssl rand -base64 32)

gcloud sql users create postgres \
  --instance=adocao-db \
  --password=$PASSWORD

echo "Salve esta senha: $PASSWORD"
```

### Passo 4: Faça deploy no Cloud Run

```bash
PROJECT_ID=seu-project-id
REGION=us-central1
SERVICE_NAME=adocao-gatos

# Build da imagem
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --cpu 1 \
  --memory 512Mi \
  --timeout 120 \
  --max-instances 10 \
  --min-instances 1 \
  --no-allow-unauthenticated \
  --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/$PROJECT_ID:$REGION:adocao-db,\
DB_USER=postgres,\
DB_PASSWORD=$PASSWORD,\
DB_NAME=adocao_gatos,\
JWT_SECRET_KEY=$(openssl rand -base64 32),\
ADMIN_EMAIL=admin@example.com,\
ADMIN_PASSWORD=$(openssl rand -base64 16) \
  --add-cloudsql-instances $PROJECT_ID:$REGION:adocao-db \
  --service-account cloud-run-service@$PROJECT_ID.iam.gserviceaccount.com
```

### Passo 5: Inicialize o banco

```bash
# Crie um Cloud Run job para executar migrações
gcloud run jobs create adocao-init \
  --image gcr.io/$PROJECT_ID/adocao-gatos:latest \
  --region $REGION \
  --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/$PROJECT_ID:$REGION:adocao-db,\
DB_USER=postgres,\
DB_PASSWORD=$PASSWORD,\
DB_NAME=adocao_gatos \
  --add-cloudsql-instances $PROJECT_ID:$REGION:adocao-db \
  --task-timeout=600 \
  --execute-now
```

Ou use Cloud Build com steps:

```yaml
# cloudbuild.yaml
steps:
  # Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/adocao-gatos:latest', '.']

  # Push
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/adocao-gatos:latest']

  # Run migrations
  - name: 'gcr.io/cloud-builders/cloud-sql-proxy'
    args: ['$PROJECT_ID:$REGION:adocao-db']

  # Deploy
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'adocao-gatos'
      - '--image=gcr.io/$PROJECT_ID/adocao-gatos:latest'
      - '--platform=managed'
      - '--region=$REGION'
```

## Monitoramento

### Cloud Logging

```bash
# Ver logs da aplicação
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=adocao-gatos" \
  --limit 50 \
  --format json
```

### Cloud Monitoring

Configure alertas para:
- Taxa de erro > 5%
- Latência p95 > 1s
- Instâncias máximas atingidas

## Backup e Recovery

### Backup Automático

```bash
gcloud sql backups create \
  --instance=adocao-db \
  --description="Backup manual"
```

### Restore

```bash
gcloud sql backups restore <BACKUP_ID> \
  --backup-instance=adocao-db
```

## Segurança

- ✅ Cloud SQL usa SSL para conexões
- ✅ VPC Service Controls para acesso controlado
- ✅ Cloud IAM para autenticação de serviços
- ✅ Secret Manager para credenciais sensíveis

### Use Secret Manager

```bash
# Criar secrets
echo -n "sua_senha_secreta" | gcloud secrets create db-password --data-file=-

# Usar no Cloud Run
gcloud run deploy adocao-gatos \
  --update-secrets DB_PASSWORD=db-password:latest
```

## Custo Estimado

- **Cloud SQL (db-f1-micro)**: ~$7.35/mês
- **Cloud Run (512MB, 1 CPU)**: ~$6/mês (100k requisições)
- **Cloud Storage (uploads)**: ~$0.02/GB/mês
- **Total estimado**: ~$15/mês

## Performance

### Índices Recomendados

```sql
-- Já inclusos nos modelos:
CREATE INDEX idx_pets_status ON pets(status);
CREATE INDEX idx_pets_name ON pets(name);
CREATE INDEX idx_admins_email ON admins(email UNIQUE);
```

### Connection Pooling

Configurado automaticamente via SQLAlchemy:
- Pool size: 10
- Max overflow: 20
- Pool timeout: 30s

## Troubleshooting

### Erro: "Connection refused"

```bash
# Verificar se Cloud SQL está acessível
gcloud sql connect adocao-db --user=postgres
```

### Erro: "Access denied"

```bash
# Verificar permissões IAM
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/cloudsql.client"
```

### Performance lenta

```bash
# Verificar CPU/Memory da instância
gcloud sql instances describe adocao-db \
  --format="value(settings.tier)"

# Aumentar se necessário
gcloud sql instances patch adocao-db --tier db-n1-standard-1
```

## Referências

- [Cloud SQL Docs](https://cloud.google.com/sql/docs)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance.html)
