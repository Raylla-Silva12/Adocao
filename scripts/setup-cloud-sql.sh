#!/bin/bash
# Setup Cloud SQL + Cloud Run Deploy
# Este script cria uma instância Cloud SQL e faz o deploy da app
# Uso: ./scripts/setup-cloud-sql.sh seu-project-id [regiao]

set -e

PROJECT_ID=${1:-seu-project-id}
REGION=${2:-us-central1}
INSTANCE_NAME="adocao-db"
DB_NAME="adocao_gatos"
DB_USER="postgres"
DB_PASSWORD=$(openssl rand -base64 32)  # Gera senha aleatória segura

# Validação
if [ "$PROJECT_ID" = "seu-project-id" ]; then
    echo "❌ Erro: Forneça seu Project ID do Google Cloud"
    echo "Uso: ./scripts/setup-cloud-sql.sh seu-project-id [regiao]"
    echo ""
    echo "Exemplo: ./scripts/setup-cloud-sql.sh meu-projeto us-central1"
    exit 1
fi

echo "🚀 Setup Cloud SQL + Cloud Run"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Project ID: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🗄️  Database: $DB_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configurar projeto
echo "🔧 Configurando projeto gcloud..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "📡 Habilitando APIs do Google Cloud..."
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Criar instância Cloud SQL
echo "🗄️  Criando instância Cloud SQL (isso leva ~5 minutos)..."
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --no-backup \
    --availability-type=ZONAL \
    --enable-bin-log=false 2>/dev/null || echo "⚠️  Instância já existe, pulando criação..."

# Criar banco de dados
echo "📚 Criando banco de dados..."
gcloud sql databases create $DB_NAME \
    --instance=$INSTANCE_NAME 2>/dev/null || echo "⚠️  Banco já existe, pulando..."

# Criar usuário
echo "👤 Configurando usuário do banco..."
gcloud sql users set-password $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format='value(connectionName)')

echo ""
echo "✅ Cloud SQL configurado com sucesso!"
echo ""
echo "📝 Salve estas informações:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Connection Name: $CONNECTION_NAME"
echo "Database:        $DB_NAME"
echo "Username:        $DB_USER"
echo "Password:        $DB_PASSWORD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Deploy no Cloud Run com Cloud SQL
echo "📦 Fazendo deploy no Cloud Run..."
gcloud builds submit --region=$REGION \
    --tag gcr.io/$PROJECT_ID/adocao-gatos:latest

echo "📤 Deployando no Cloud Run..."
gcloud run deploy adocao-gatos \
    --image gcr.io/$PROJECT_ID/adocao-gatos:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --cpu 1 \
    --memory 512Mi \
    --timeout 120 \
    --max-instances 10 \
    --set-env-vars=\
FLASK_ENV=production,\
DB_HOST=/cloudsql/$CONNECTION_NAME,\
DB_USER=$DB_USER,\
DB_PASSWORD=$DB_PASSWORD,\
DB_NAME=$DB_NAME,\
JWT_SECRET_KEY=$(openssl rand -base64 32),\
ADMIN_EMAIL=admin@example.com,\
ADMIN_PASSWORD=admin123,\
CONTACT_EMAIL=larparabigodinhos@gmail.com \
    --add-cloudsql-instances $CONNECTION_NAME

echo ""
echo "✅ Deploy no Cloud Run concluído!"
echo ""
echo "🌐 Sua app está disponível em:"
gcloud run services describe adocao-gatos --platform managed --region $REGION --format='value(status.url)'
echo ""
echo "💡 Dicas:"
echo "  - Acesse /health para verificar o status"
echo "  - Acesse / para ver as informações da API"
echo "  - Guarde as credenciais do banco acima em local seguro"
