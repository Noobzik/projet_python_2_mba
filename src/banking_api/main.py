from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI

# Imports des routeurs
from banking_api.api.transactions import router as transactions_router
from banking_api.api.stats import router as stats_router
from banking_api.api.fraud import router as fraud_router
from banking_api.api.customers import router as customers_router
from banking_api.api.system import router as system_router

# Import du chargeur de données (Version "Bridge" compatible)
from banking_api.services.dataset_loader import load_dataset

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Nouveau cycle de vie : Charge les données au démarrage.
    """
    print("🔄 Initialisation du système bancaire ...")
    try:
        # On appelle le chargeur SANS argument (c'est lui qui gère Kaggle)
        load_dataset() 
        print("✅ Système prêt et données chargées.")
    except Exception as e:
        print(f"❌ Erreur critique au démarrage : {e}")
    
    yield  # L'application tourne ici
    
    print("🛑 Arrêt du système.")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Banking Transactions API (Group 2)",
        version="2.1.0",
        description="API for Fraud Detection & Transaction Analysis",
        lifespan=lifespan  # On branche le nouveau moteur ici
    )

    # Enregistrement des routes
    app.include_router(transactions_router, prefix="/api", tags=["transactions"])
    app.include_router(stats_router, prefix="/api", tags=["stats"])
    app.include_router(fraud_router, prefix="/api", tags=["fraud"])
    app.include_router(customers_router, prefix="/api", tags=["customers"])
    app.include_router(system_router, prefix="/api", tags=["system"])

    return app

app = create_app()