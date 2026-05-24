#!/bin/bash
set -e

PROJECT_ID="project-89f158a9-2682-485e-a79"
REGION="us-central1"
DB_PASSWORD="AdocaoGatos2024!"
JWT_SECRET="jwt-secret-adocao-gatos-2024"

echo "Fazendo deploy..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Configurar projeto
gcloud config set project $PROJECT_ID

# Verificar/criar SQL
echo "Checando Cloud SQL..."
gcloud sql instances describe adocao-db 2>/dev/null || gcloud sql instances create adocao-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --no-backup

# Criar banco
gcloud sql databases create adocao_gatos --instance=adocao-db 2>/dev/null || true

# Set password  
gcloud sql users set-password postgres --instance=adocao-db --password=$DB_PASSWORD

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe adocao-db --format='value(connectionName)')
echo "Connection: $CONNECTION_NAME"

# Build
cd /c/Users/Exterminador\ 2\ MIL/Desktop/Adocao
echo "Building Docker image..."
gcloud builds submit --region=$REGION --tag gcr.io/$PROJECT_ID/adocao-gatos:latest

# Deploy
echo "Deploying to Cloud Run..."
gcloud run deploy adocao-gatos \
    --image gcr.io/$PROJECT_ID/adocao-gatos:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --cpu 1 \
    --memory 512Mi \
    --timeout 120 \
    --max-instances 10 \
    --set-env-vars="FLASK_ENV=production,DB_HOST=/cloudsql/$CONNECTION_NAME,DB_USER=postgres,DB_PASSWORD=$DB_PASSWORD,DB_NAME=adocao_gatos,JWT_SECRET_KEY=$JWT_SECRET,ADMIN_EMAIL=admin@example.com,ADMIN_PASSWORD=admin123" \
    --add-cloudsql-instances $CONNECTION_NAME

# Get URL
URL=$(gcloud run services describe adocao-gatos --platform managed --region $REGION --format='value(status.url)')
echo ""
echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo "URL: $URL"
echo "Connection: $CONNECTION_NAME"
echo "Password: $DB_PASSWORD"
echo ""
echo "Test:"
echo "  Health: ${URL}/health"
echo "  API: ${URL}/api/pets"
