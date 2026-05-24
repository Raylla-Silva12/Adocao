#!/bin/bash
# Deploy simples para Google Cloud Run (sem provisionar Cloud SQL)
# Uso: ./scripts/deploy-gcp.sh seu-project-id [regiao]

set -e

PROJECT_ID=${1:-seu-project-id}
REGION=${2:-us-central1}
SERVICE_NAME="adocao-gatos"

if [ "$PROJECT_ID" = "seu-project-id" ]; then
    echo "Erro: forneca seu Project ID do Google Cloud"
    echo "Uso: ./scripts/deploy-gcp.sh seu-project-id [regiao]"
    echo ""
    echo "Exemplo: ./scripts/deploy-gcp.sh meu-projeto us-central1"
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

# Tag unica evita Cloud Run reutilizar imagem antiga com :latest
BUILD_TAG=$(date +%Y%m%d-%H%M%S)

# Build e push via Cloud Build (sem cache para incluir templates/static novos)
echo "🔨 Enviando para Cloud Build (tag: $BUILD_TAG)..."
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=SHORT_SHA=$BUILD_TAG

# Deploy no Cloud Run
echo "📤 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$BUILD_TAG \
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
