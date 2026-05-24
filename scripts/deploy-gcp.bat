@echo off
REM Script para fazer deploy no Google Cloud Run (Windows)
# Uso: .\scripts\deploy-gcp.bat seu-project-id [regiao]

setlocal enabledelayedexpansion

set PROJECT_ID=%1
if "!PROJECT_ID!"=="" set PROJECT_ID=seu-project-id

set REGION=%2
if "!REGION!"=="" set REGION=us-central1

set SERVICE_NAME=adocao-gatos
set IMAGE_NAME=adocao-gatos

echo.
echo 🚀 Deploy para Google Cloud Run
echo Project ID: !PROJECT_ID!
echo Region: !REGION!
echo Service: !SERVICE_NAME!
echo.

REM Autenticação
echo 🔐 Autenticando...
call gcloud auth login
call gcloud config set project !PROJECT_ID!

REM Build da imagem
echo 🔨 Fazendo build da imagem Docker...
call gcloud builds submit --tag gcr.io/!PROJECT_ID!/!IMAGE_NAME!:latest

REM Deploy no Cloud Run
echo 📤 Fazendo deploy no Cloud Run...
call gcloud run deploy !SERVICE_NAME! ^
  --image gcr.io/!PROJECT_ID!/!IMAGE_NAME!:latest ^
  --platform managed ^
  --region !REGION! ^
  --allow-unauthenticated ^
  --cpu 1 ^
  --memory 512Mi ^
  --timeout 120 ^
  --max-instances 10 ^
  --set-env-vars=FLASK_ENV=production,DB_HOST=/cloudsql/!PROJECT_ID!:!REGION!:adocao-db,DB_USER=postgres,DB_PASSWORD=SUA_SENHA,DB_NAME=adocao_gatos,JWT_SECRET_KEY=SUA_CHAVE_SECRETA,ADMIN_EMAIL=admin@example.com,ADMIN_PASSWORD=admin123 ^
  --add-cloudsql-instances !PROJECT_ID!:!REGION!:adocao-db

echo.
echo ✅ Deploy concluído com sucesso!
echo Service URL:
call gcloud run services describe !SERVICE_NAME! --region !REGION! --format "value(status.url)"
