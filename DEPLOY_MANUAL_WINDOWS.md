# DEPLOY RAPIDO PARA CLOUD RUN - GUIA PASSO A PASSO

## PASSO 1: Autenticar no Google Cloud

```powershell
gcloud auth login
gcloud auth application-default login
```

Isso vai abrir o navegador. Faça login com sua conta Google.

## PASSO 2: Configurar variáveis

```powershell
$PROJECT_ID = "project-89f158a9-2682-485e-a79"
$REGION = "us-central1"
$DB_PASSWORD = "sua-senha-super-secreta-123"
$JWT_SECRET = "sua-chave-jwt-super-secreta-456"
```

## PASSO 3: Configurar projeto gcloud

```powershell
gcloud config set project $PROJECT_ID
gcloud config list
```

Verifique se o project_id está correto.

## PASSO 4: Habilitar APIs

```powershell
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

Isso leva alguns minutos.

## PASSO 5: Criar instância Cloud SQL

```powershell
gcloud sql instances create adocao-db `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$REGION `
    --no-backup `
    --availability-type=ZONAL
```

Isso leva ~5 minutos. Espere completar!

## PASSO 6: Criar banco de dados

```powershell
gcloud sql databases create adocao_gatos --instance=adocao-db
```

## PASSO 7: Configurar usuário

```powershell
gcloud sql users set-password postgres `
    --instance=adocao-db `
    --password=$DB_PASSWORD
```

## PASSO 8: Obter Connection Name

```powershell
$CONNECTION_NAME = gcloud sql instances describe adocao-db --format='value(connectionName)'
Write-Host "Connection: $CONNECTION_NAME"
```

Salve este valor! Vai ser algo como: `seu-projeto:us-central1:adocao-db`

## PASSO 9: Fazer build e push no Google Container Registry

```powershell
cd "c:\Users\Exterminador 2 MIL\Desktop\Adocao"
gcloud builds submit --region=$REGION --tag gcr.io/$PROJECT_ID/adocao-gatos:latest
```

Isso leva ~3-5 minutos. Vá tomar um café!

## PASSO 10: Deploy no Cloud Run

```powershell
gcloud run deploy adocao-gatos `
    --image gcr.io/$PROJECT_ID/adocao-gatos:latest `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --cpu 1 `
    --memory 512Mi `
    --timeout 120 `
    --max-instances 10 `
    --set-env-vars="FLASK_ENV=production,DB_HOST=/cloudsql/$CONNECTION_NAME,DB_USER=postgres,DB_PASSWORD=$DB_PASSWORD,DB_NAME=adocao_gatos,JWT_SECRET_KEY=$JWT_SECRET,ADMIN_EMAIL=admin@example.com,ADMIN_PASSWORD=admin123" `
    --add-cloudsql-instances $CONNECTION_NAME
```

## PASSO 11: Obter URL de acesso

```powershell
gcloud run services describe adocao-gatos --platform managed --region $REGION --format='value(status.url)'
```

Isso vai retornar algo como: `https://adocao-gatos-xxx.run.app`

## PASSO 12: Testar

Abra no navegador:
```
https://adocao-gatos-xxx.run.app/health
```

Deve retornar:
```json
{
  "status": "ok",
  "database": "connected"
}
```

Se der erro, verifique:
- Cloud SQL está rodando: `gcloud sql instances list`
- Cloud Run está rodando: `gcloud run services list --platform managed`
- Logs: `gcloud run services describe adocao-gatos --platform managed --region $REGION`

---

## COPIAR E COLAR RAPIDO

Se quiser rodar tudo de uma vez em um script:

```powershell
$PROJECT_ID = "project-89f158a9-2682-485e-a79"
$REGION = "us-central1"
$DB_PASSWORD = "senha123"
$JWT_SECRET = "jwt456"

gcloud config set project $PROJECT_ID
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud sql instances create adocao-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=$REGION --no-backup --availability-type=ZONAL
gcloud sql databases create adocao_gatos --instance=adocao-db
gcloud sql users set-password postgres --instance=adocao-db --password=$DB_PASSWORD

$CONNECTION_NAME = gcloud sql instances describe adocao-db --format='value(connectionName)'

cd "c:\Users\Exterminador 2 MIL\Desktop\Adocao"
gcloud builds submit --region=$REGION --tag gcr.io/$PROJECT_ID/adocao-gatos:latest

gcloud run deploy adocao-gatos --image gcr.io/$PROJECT_ID/adocao-gatos:latest --platform managed --region $REGION --allow-unauthenticated --cpu 1 --memory 512Mi --timeout 120 --max-instances 10 --set-env-vars="FLASK_ENV=production,DB_HOST=/cloudsql/$CONNECTION_NAME,DB_USER=postgres,DB_PASSWORD=$DB_PASSWORD,DB_NAME=adocao_gatos,JWT_SECRET_KEY=$JWT_SECRET,ADMIN_EMAIL=admin@example.com,ADMIN_PASSWORD=admin123" --add-cloudsql-instances $CONNECTION_NAME

gcloud run services describe adocao-gatos --platform managed --region $REGION --format='value(status.url)'
```

Copy e cole no PowerShell tudo de uma vez!
