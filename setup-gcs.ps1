# Configura Google Cloud Storage para fotos dos pets (deploy existente no Cloud Run)
param(
    [string]$ProjectId = "project-89f158a9-2682-485e-a79",
    [string]$Region = "us-central1",
    [string]$ServiceName = "adocao-gatos"
)

$GCS_BUCKET = "$ProjectId-adocao-pets"

Write-Host ""
Write-Host "Configurando GCS para fotos dos pets" -ForegroundColor Cyan
Write-Host "Project: $ProjectId" -ForegroundColor Cyan
Write-Host "Bucket:  $GCS_BUCKET" -ForegroundColor Cyan
Write-Host ""

gcloud config set project $ProjectId --quiet
gcloud services enable storage.googleapis.com --quiet

gcloud storage buckets describe "gs://$GCS_BUCKET" 2>$null
if ($LASTEXITCODE -ne 0) {
    gcloud storage buckets create "gs://$GCS_BUCKET" --location=$REGION --uniform-bucket-level-access
}

gcloud storage buckets add-iam-policy-binding "gs://$GCS_BUCKET" `
    --member=allUsers `
    --role=roles/storage.objectViewer `
    --quiet

$PROJECT_NUMBER = gcloud projects describe $ProjectId --format="value(projectNumber)"
$SA = "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://$GCS_BUCKET" `
    --member="serviceAccount:$SA" `
    --role=roles/storage.objectAdmin `
    --quiet

gcloud run services update $ServiceName `
    --region $Region `
    --update-env-vars="GCS_BUCKET=$GCS_BUCKET"

Write-Host ""
Write-Host "GCS configurado com sucesso." -ForegroundColor Green
Write-Host "Faca um novo deploy da aplicacao e reenvie as fotos dos pets." -ForegroundColor Yellow
Write-Host ""
