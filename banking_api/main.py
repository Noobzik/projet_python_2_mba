"""
Application principale FastAPI pour Banking Transactions API.

Ce module initialise et configure l'application FastAPI avec toutes
les routes et middlewares nécessaires.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from banking_api.routes import (
    customers,
    fraud,
    statistics,
    system,
    transactions,
)
from banking_api.services.data_loader import data_loader


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """
    Gère le cycle de vie de l'application.

    Parameters
    ----------
    app : FastAPI
        Instance de l'application FastAPI

    Yields
    ------
    None
        Contrôle pendant l'exécution de l'application
    """
    # Startup: Chargement des données
    print("🚀 Démarrage de l'API Banking Transactions...")
    try:
        data_loader.load_data()
        print("✅ Données chargées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données: {e}")

    yield

    # Shutdown
    print("🛑 Arrêt de l'API Banking Transactions...")


# Création de l'application FastAPI
app: FastAPI = FastAPI(
    title="Banking Transactions API",
    description="API REST pour l'exposition des données de transactions bancaires",
    version="1.0.0",
    contact={
        "name": "ESG MBA Team",
        "email": "team@esg-mba.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Gestionnaire d'erreurs global.

    Parameters
    ----------
    request : Request
        Requête HTTP
    exc : Exception
        Exception levée

    Returns
    -------
    JSONResponse
        Réponse d'erreur JSON
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


# Endpoint racine
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Endpoint racine de l'API.

    Returns
    -------
    Dict[str, str]
        Message de bienvenue
    """
    return {
        "message": "Banking Transactions API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


# Enregistrement des routes
app.include_router(transactions.router)
app.include_router(statistics.router)
app.include_router(fraud.router)
app.include_router(customers.router)
app.include_router(system.router)


def start() -> None:
    """
    Point d'entrée pour démarrer l'application.

    Cette fonction est appelée par la commande console_scripts
    définie dans setup.py.
    """
    uvicorn.run(
        "banking_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    start()
