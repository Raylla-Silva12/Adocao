# Setup Cloud SQL + Cloud Run Deploy (PowerShell)
# Uso: .\setup-cloud-sql.ps1 seu-project-id sua-regiao

param(
    [string]$ProjectId = "seu-project-id",
    [string]$Region = "us-central1"
)

$InstanceName = "adocao-db"
$DbName = "adocao_gatos"
$DbUser = "postgres"

# Validação
if ($ProjectId -eq "seu-project-id") {
    Write-Host "❌ Erro: Forneça seu Project ID do Google Cloud" -ForegroundColor Red
    Write-Host "Uso: .\setup-cloud-sql.ps1 seu-project-id [regiao]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Exemplo: .\setup-cloud-sql.ps1 meu-projeto-gcp us-central1" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "🚀 Setup Cloud SQL + Cloud Run" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📍 Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "🌍 Region: $Region" -ForegroundColor Cyan
Write-Host "🗄️  Database: $DbName" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Gerar senha aleatória
$DbPassword = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
$JwtSecret = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# Configurar projeto
Write-Host "🔧 Configurando projeto gcloud..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Habilitar APIs
Write-Host "📡 Habilitando APIs do Google Cloud..." -ForegroundColor Yellow
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Criar instância Cloud SQL
Write-Host "🗄️  Criando instância Cloud SQL (isso leva ~5 minutos)..." -ForegroundColor Yellow
$instanceCheck = gcloud sql instances describe $InstanceName 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️  Instância já existe, pulando criação..." -ForegroundColor Yellow
} else {
    gcloud sql instances create $InstanceName `
        --database-version=POSTGRES_15 `
        --tier=db-f1-micro `
        --region=$Region `
        --no-backup `
        --availability-type=ZONAL `
        --enable-bin-log=false
}

# Criar banco de dados
Write-Host "📚 Criando banco de dados..." -ForegroundColor Yellow
$dbCheck = gcloud sql databases describe $DbName --instance=$InstanceName 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️  Banco já existe, pulando..." -ForegroundColor Yellow
} else {
    gcloud sql databases create $DbName --instance=$InstanceName
}

# Configurar usuário
Write-Host "👤 Configurando usuário do banco..." -ForegroundColor Yellow
gcloud sql users set-password $DbUser `
    --instance=$InstanceName `
    --password=$DbPassword

# Obter connection name
Write-Host "🔍 Obtendo informações de conexão..." -ForegroundColor Yellow
$ConnectionName = gcloud sql instances describe $InstanceName --format='value(connectionName)'

Write-Host ""
Write-Host "✅ Cloud SQL configurado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Salve estas informações:" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "Connection Name: $ConnectionName" -ForegroundColor Cyan
Write-Host "Database:        $DbName" -ForegroundColor Cyan
Write-Host "Username:        $DbUser" -ForegroundColor Cyan
Write-Host "Password:        $DbPassword" -ForegroundColor Cyan
Write-Host "JWT Secret:      $JwtSecret" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

# Build e deploy (tag unica + sem cache do Docker)
$BuildTag = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Host "📦 Fazendo build da imagem Docker (tag: $BuildTag)..." -ForegroundColor Yellow
gcloud builds submit --config cloudbuild.yaml `
    --substitutions=SHORT_SHA=$BuildTag

Write-Host ""
Write-Host "📤 Deployando no Cloud Run..." -ForegroundColor Yellow
gcloud run deploy adocao-gatos `
    --image gcr.io/$ProjectId/adocao-gatos:$BuildTag `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --cpu 1 `
    --memory 512Mi `
    --timeout 120 `
    --max-instances 10 `
    --set-env-vars="FLASK_ENV=production,DB_HOST=/cloudsql/$ConnectionName,DB_USER=$DbUser,DB_PASSWORD=$DbPassword,DB_NAME=$DbName,JWT_SECRET_KEY=$JwtSecret,ADMIN_EMAIL=admin@example.com,ADMIN_PASSWORD=admin123,CONTACT_EMAIL=larparabigodinhos@gmail.com" `
    --add-cloudsql-instances $ConnectionName

Write-Host ""
Write-Host "✅ Deploy no Cloud Run concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Sua app está disponível em:" -ForegroundColor Cyan
gcloud run services describe adocao-gatos --platform managed --region $Region --format='value(status.url)'
Write-Host ""
Write-Host "💡 Próximas ações:" -ForegroundColor Cyan
Write-Host "  1. Acesse a URL acima no navegador" -ForegroundColor Cyan
Write-Host "  2. Teste /health para verificar o banco" -ForegroundColor Cyan
Write-Host "  3. Use /api/pets para listar pets (vazio no início)" -ForegroundColor Cyan
Write-Host ""
