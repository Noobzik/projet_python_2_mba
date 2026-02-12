# Script PowerShell pour vérifier la qualité du code
# Usage: .\check_quality.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Code Quality Checks                 " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
if (Test-Path "venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
    exit 1
}

$allPassed = $true

# Flake8
Write-Host "1. Checking PEP8 compliance (flake8)..." -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Gray
flake8 banking_api/ tests/

if ($LASTEXITCODE -eq 0) {
    Write-Host "Flake8: PASSED (no PEP8 violations)" -ForegroundColor Green
} else {
    Write-Host "✗ Flake8: FAILED" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

# MyPy
Write-Host "2. Checking type hints (mypy)..." -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Gray
mypy banking_api/

if ($LASTEXITCODE -eq 0) {
    Write-Host "MyPy: PASSED (type hints OK)" -ForegroundColor Green
} else {
    Write-Host "✗ MyPy: FAILED" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""


# Summary
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Quality Check Summary               " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if ($allPassed) {
    Write-Host 'All quality checks passed!' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Your code is ready for submission!' -ForegroundColor Green
    exit 0
}
else {
    Write-Host 'Some quality checks failed' -ForegroundColor Red
    Write-Host ''
    Write-Host 'Please fix the issues above before submission' -ForegroundColor Yellow
    exit 1
}
