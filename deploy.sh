#!/bin/bash
# Script para fazer deploy no Google Cloud Run
# Uso: ./deploy.sh seu-project-id

set -e

PROJECT_ID=${1:-seu-project-id}
REGION=${2:-us-central1}
SERVICE_NAME="adocao-gatos"
IMAGE_NAME="adocao-gatos"

echo "🚀 Deploy para Google Cloud Run"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Autenticação
echo "🔐 Autenticando..."
gcloud auth login
gcloud config set project $PROJECT_ID

# Build da imagem
echo "🔨 Fazendo build da imagem Docker..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

# Deploy no Cloud Run
echo "📤 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --timeout 120 \
  --max-instances 10 \
  --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/$PROJECT_ID:$REGION:adocao-db,\
DB_USER=postgres,\
DB_PASSWORD=SUA_SENHA,\
DB_NAME=adocao_gatos,\
JWT_SECRET_KEY=SUA_CHAVE_SECRETA,\
ADMIN_EMAIL=admin@example.com,\
ADMIN_PASSWORD=admin123 \
  --add-cloudsql-instances $PROJECT_ID:$REGION:adocao-db

# URLs do serviço
echo ""
echo "✅ Deploy concluído com sucesso!"
echo "Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
