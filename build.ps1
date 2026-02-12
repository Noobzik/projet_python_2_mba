# Script PowerShell pour construire le package
# Usage: .\build.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Banking Transactions API - Build    " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
    Write-Host "  Run .\start.ps1 first to set up the environment" -ForegroundColor Yellow
    exit 1
}

# Vérifier les outils de build
Write-Host ""
Write-Host "Checking build tools..." -ForegroundColor Yellow
$buildInstalled = pip show build 2>$null
if ($null -eq $buildInstalled) {
    Write-Host "Installing build tools..." -ForegroundColor Yellow
    pip install build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install build tools" -ForegroundColor Red
        exit 1
    }
    Write-Host "Build tools installed" -ForegroundColor Green
} else {
    Write-Host "Build tools already installed" -ForegroundColor Green
}

# Nettoyer les anciens builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "Removed old dist/ directory" -ForegroundColor Green
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "Removed old build/ directory" -ForegroundColor Green
}
if (Test-Path "*.egg-info") {
    Remove-Item -Recurse -Force "*.egg-info"
    Write-Host "Removed old *.egg-info directories" -ForegroundColor Green
}

# Construire le package
Write-Host ""
Write-Host "Building package..." -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Gray
python -m build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Build completed successfully" -ForegroundColor Green

# Vérifier les fichiers générés
Write-Host ""
Write-Host "Generated files:" -ForegroundColor Yellow
if (Test-Path "dist") {
    Get-ChildItem "dist" | ForEach-Object {
        Write-Host "  $($_.Name)" -ForegroundColor White
    }
} else {
    Write-Host "  No dist/ directory found" -ForegroundColor Red
}

# Résumé
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Build Summary                        " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Package built successfully" -ForegroundColor Green
Write-Host ""
Write-Host "To install the package locally:" -ForegroundColor Yellow
Write-Host "  pip install -e ." -ForegroundColor White
Write-Host ""
Write-Host "To install from built distribution:" -ForegroundColor Yellow
Write-Host "  pip install dist/*.whl" -ForegroundColor White
Write-Host ""
Write-Host "To upload to PyPI (if configured):" -ForegroundColor Yellow
Write-Host "  twine upload dist/*" -ForegroundColor White
Write-Host ""

exit 0