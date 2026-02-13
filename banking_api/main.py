"""Point d'entrée principal de l'application FastAPI.
Ce module initialise l'application FastAPI et enregistre toutes les routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from banking_api.routes import (
    transactions_router,
    stats_router,
    fraud_router,
    customers_router,
    system_router
)
from banking_api.utils.data_loader import DataLoader
from banking_api.config import API_TITLE, API_DESCRIPTION, API_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestionnaire de cycle de vie pour les événements de démarrage et d'arrêt.

    Parameters
    ----------
    app : FastAPI
        Instance de l'application FastAPI

    Yields
    ------
    None
        Contrôle du flux pendant la durée de vie de l'application
    """
    data_loader = DataLoader()
    try:
        data_loader.load_data()
        print("Dataset chargé avec succès")
    except Exception as e:
        print(f"Avertissement : impossible de charger le dataset : {e}")

    yield

    print("Arrêt de l'application")


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router)
app.include_router(stats_router)
app.include_router(fraud_router)
app.include_router(customers_router)
app.include_router(system_router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Endpoint racine fournissant les informations de l'API.

    Returns
    -------
    dict[str, str]
        Message d'accueil et liens vers la documentation
    """
    return {
        "message": "Banking Transactions API",
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


def run() -> None:
    """Lancer l'application avec uvicorn.

    Cette fonction est utilisée comme point d'entrée de script console.
    """
    import uvicorn
    uvicorn.run("banking_api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
