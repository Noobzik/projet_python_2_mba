# Script PowerShell pour exécuter tous les tests
# Usage: .\run_tests.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Banking Transactions API - Tests    " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
if (Test-Path "venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
    Write-Host "  Run .\start.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Tests pytest
Write-Host "Running pytest - unit tests..." -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Gray
pytest --cov=banking_api --cov-report=term-missing --cov-report=html -v

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Pytest tests failed" -ForegroundColor Red
    $pytestFailed = $true
} else {
    Write-Host ""
    Write-Host "✓ Pytest tests passed" -ForegroundColor Green
    $pytestFailed = $false
}

# Tests unittest
Write-Host ""
Write-Host "Running unittest - feature tests..." -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Gray
python -m unittest discover tests/features -v

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Unittest tests failed" -ForegroundColor Red
    $unittestFailed = $true
} else {
    Write-Host ""
    Write-Host "✓ Unittest tests passed" -ForegroundColor Green
    $unittestFailed = $false
}

# Résumé
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Test Summary                        " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if (-not $pytestFailed) {
    Write-Host "✓ Pytest: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Pytest: FAILED" -ForegroundColor Red
}

if (-not $unittestFailed) {
    Write-Host "✓ Unittest: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Unittest: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Yellow
Write-Host "Run 'start htmlcov/index.html' to view" -ForegroundColor Yellow
Write-Host ""

# Code de sortie
if ($pytestFailed -or $unittestFailed) {
    exit 1
} else {
    exit 0
}
