# Deploy simples para Cloud Run com Cloud SQL
$PROJECT_ID = "project-89f158a9-2682-485e-a79"
$REGION = "us-central1"
$DB_PASSWORD = "AdocaoGatos2024!"
$JWT_SECRET = "jwt-secret-adocao-gatos-2024"

Write-Host "🚀 Deploy para Cloud Run" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Step 1: Configurar gcloud
Write-Host "Step 1: Configurando gcloud..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID --quiet
gcloud config set account raylla.l.silva@gmail.com --quiet
Write-Host "✅ Configuração concluída" -ForegroundColor Green
Write-Host ""

# Step 2: Habilitar APIs
Write-Host "Step 2: Habilitando APIs..." -ForegroundColor Yellow
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Step 3: Criar Cloud SQL
Write-Host "Step 3: Criando instância Cloud SQL..." -ForegroundColor Yellow
Write-Host "⏳ Isso pode levar alguns minutos..." -ForegroundColor Yellow
gcloud sql instances create adocao-db `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$REGION `
    --no-backup `
    --availability-type=ZONAL `
    --quiet 2>&1 | Where-Object { $_ -notmatch "already exists" }
Write-Host "✅ Cloud SQL pronto" -ForegroundColor Green
Write-Host ""

# Step 4: Criar banco de dados
Write-Host "Step 4: Criando banco de dados..." -ForegroundColor Yellow
gcloud sql databases create adocao_gatos --instance=adocao-db --quiet 2>&1 | Where-Object { $_ -notmatch "already exists" }
Write-Host "✅ Banco criado" -ForegroundColor Green
Write-Host ""

# Step 5: Configurar senha
Write-Host "Step 5: Configurando usuário postgres..." -ForegroundColor Yellow
gcloud sql users set-password postgres --instance=adocao-db --password=$DB_PASSWORD --quiet
Write-Host "✅ Usuário configurado" -ForegroundColor Green
Write-Host ""

# Step 6: Obter connection name
Write-Host "Step 6: Obtendo informações de conexão..." -ForegroundColor Yellow
$CONNECTION_NAME = gcloud sql instances describe adocao-db --format='value(connectionName)'
Write-Host "✅ Connection: $CONNECTION_NAME" -ForegroundColor Green
Write-Host ""

# Step 7: Build e push
Write-Host "Step 7: Fazendo build da imagem Docker..." -ForegroundColor Yellow
Write-Host "⏳ Isso pode levar 5-10 minutos..." -ForegroundColor Yellow
Push-Location "c:\Users\Exterminador 2 MIL\Desktop\Adocao"
gcloud builds submit --region=$REGION --tag gcr.io/$PROJECT_ID/adocao-gatos:latest --quiet
Pop-Location
Write-Host "✅ Build concluído" -ForegroundColor Green
Write-Host ""

# Step 8: Deploy no Cloud Run
Write-Host "Step 8: Deployando no Cloud Run..." -ForegroundColor Yellow
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
    --add-cloudsql-instances $CONNECTION_NAME `
    --quiet
Write-Host "✅ Deploy concluído" -ForegroundColor Green
Write-Host ""

# Step 9: Obter URL
Write-Host "Step 9: Obtendo URL da aplicação..." -ForegroundColor Yellow
$URL = gcloud run services describe adocao-gatos --platform managed --region $REGION --format='value(status.url)'
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "🎉 SUCESSO! Sua app está rodando!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL da aplicação:" -ForegroundColor Cyan
Write-Host "$URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Credenciais salvas:" -ForegroundColor Cyan
Write-Host "  Database Connection: $CONNECTION_NAME" -ForegroundColor Yellow
Write-Host "  Database Name: adocao_gatos" -ForegroundColor Yellow
Write-Host "  Database User: postgres" -ForegroundColor Yellow
Write-Host "  Database Password: $DB_PASSWORD" -ForegroundColor Yellow
Write-Host ""
Write-Host "🧪 Testar a aplicação:" -ForegroundColor Cyan
Write-Host "  1. Health check: $($URL)/health" -ForegroundColor Yellow
Write-Host "  2. API: $($URL)/api/pets" -ForegroundColor Yellow
Write-Host "  3. Root: $($URL)/" -ForegroundColor Yellow
Write-Host ""
