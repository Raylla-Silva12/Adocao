#!/bin/bash
set -e

PROJECT_ID="project-89f158a9-2682-485e-a79"
REGION="us-central1"
DB_PASSWORD="AdocaoGatos2024!"
JWT_SECRET="jwt-secret-adocao-gatos-2024"

echo "Aguardando Cloud SQL ficar pronto..."
while true; do
  STATE=$(gcloud sql instances describe adocao-db --format='value(state)' --project=$PROJECT_ID)
  echo "Estado: $STATE"
  if [ "$STATE" = "RUNNABLE" ]; then
    echo "Cloud SQL pronto!"
    break
  fi
  echo "Aguardando..."
  sleep 10
done

echo "Configurando usuário..."
gcloud sql users set-password postgres --instance=adocao-db --password=$DB_PASSWORD --project=$PROJECT_ID

echo "Criando banco de dados..."
gcloud sql databases create adocao_gatos --instance=adocao-db --project=$PROJECT_ID 2>/dev/null || true

CONNECTION_NAME=$(gcloud sql instances describe adocao-db --format='value(connectionName)' --project=$PROJECT_ID)
echo "Connection: $CONNECTION_NAME"

echo "Building Docker image..."
cd /c/Users/Exterminador\ 2\ MIL/Desktop/Adocao
gcloud builds submit --region=$REGION --tag gcr.io/$PROJECT_ID/adocao-gatos:latest --project=$PROJECT_ID

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
    --add-cloudsql-instances $CONNECTION_NAME \
    --project=$PROJECT_ID

URL=$(gcloud run services describe adocao-gatos --platform managed --region $REGION --format='value(status.url)' --project=$PROJECT_ID)
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
