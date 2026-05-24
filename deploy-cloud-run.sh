#!/bin/bash
# Deploy simples para Google Cloud Run
# Uso: ./deploy-cloud-run.sh seu-project-id

set -e

PROJECT_ID=${1:-seu-project-id}
REGION=${2:-us-central1}
SERVICE_NAME="adocao-gatos"

if [ "$PROJECT_ID" = "seu-project-id" ]; then
    echo "❌ Erro: Forneça seu Project ID do Google Cloud"
    echo "Uso: ./deploy-cloud-run.sh seu-project-id [regiao]"
    echo ""
    echo "Exemplo: ./deploy-cloud-run.sh meu-projeto us-central1"
    exit 1
fi

echo "🚀 Deploy para Google Cloud Run"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Project ID: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "📦 Service: $SERVICE_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Autenticação e configuração
echo "🔐 Configurando gcloud..."
gcloud config set project $PROJECT_ID

# Build e push via Cloud Build
echo "🔨 Enviando para Cloud Build (isso vai levar alguns minutos)..."
gcloud builds submit --region=$REGION \
    --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy no Cloud Run
echo "📤 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --cpu 1 \
    --memory 512Mi \
    --timeout 120 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production

echo ""
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "🌐 Sua app está disponível em:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)'
echo ""
echo "💡 Dica: Acesse /health para verificar se a app está rodando"
