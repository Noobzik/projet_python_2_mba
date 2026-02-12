# Script PowerShell de démarrage rapide
# Usage: .\start.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Banking Transactions API - Startup  " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[2-9]") {
    Write-Host "Python version OK: $pythonVersion" -ForegroundColor Green
}
else {
    Write-Host "Python 3.12+ required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Vérifier l'environnement virtuel
Write-Host ""
Write-Host "Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Virtual environment found" -ForegroundColor Green
    Write-Host "  Activating..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}
else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment created and activated" -ForegroundColor Green
}

# Vérifier les dépendances
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$fastapi = pip show fastapi 2>$null
if ($null -eq $fastapi) {
    Write-Host "Dependencies not installed. Installing..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "Dependencies already installed" -ForegroundColor Green
}

# Vérifier les données
Write-Host ""
Write-Host "Checking data files..." -ForegroundColor Yellow
if (Test-Path "data\transactions_data.csv") {
    Write-Host "Data files found" -ForegroundColor Green
}
else {
    Write-Host "Warning: data\transactions_data.csv not found" -ForegroundColor Red
    Write-Host "  Please add your data files to the data\ folder" -ForegroundColor Yellow
}

# Lancer l'application
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Starting Banking Transactions API..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Green
Write-Host "  http://localhost:8000/docs (Swagger UI)" -ForegroundColor White
Write-Host "  http://localhost:8000/redoc (ReDoc)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Démarrer uvicorn
uvicorn banking_api.main:app --reload --host 0.0.0.0 --port 8000
