from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings

# Import des routeurs
from app.api import system
from app.api import transactions
from app.api import stats
from app.api import fraud
from app.api import customers

# --- GESTION DU CYCLE DE VIE (Remplaçant de @app.on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Exécuté au démarrage : Charge les données en mémoire.
    Exécuté à l'arrêt : Nettoie les ressources (si besoin).
    """
    print(" Démarrage de l'API : Initialisation des services...")
    # Force le téléchargement/chargement des données immédiatement
    settings.get_df()
    print("✅ API prête à recevoir des requêtes.")
    
    yield  # L'application tourne ici
    
    print(" Arrêt de l'API.")

# Configuration de l'API
app = FastAPI(
    title="Banking Transactions API",
    description="""
    API REST professionnelle pour l'analyse de transactions bancaires et la détection de fraude.
    
    ## Fonctionnalités
      **Transactions** : Recherche et filtrage sur 13M de lignes.
      **Statistiques** : Analyse macro-économique et KPI.
      **Fraude** : Détection des anomalies et scoring.
      **Clients** : Profilage 360° et habitudes de consommation.
    """,
    version="1.0.0",
    contact={
        "name": "Équipe MBA Tech",
        "email": "legodway@gmail.com",
    },
    lifespan=lifespan  # On injecte le nouveau système ici
)

# --- MIDDLEWARE (Sécurité & Accès) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTEURS (Organisation des URLs) ---
app.include_router(system.router, prefix="/api/system", tags=["Administration"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistiques"])
app.include_router(fraud.router, prefix="/api/fraud", tags=["Détection Fraude"])
app.include_router(customers.router, prefix="/api/customers", tags=["Clients"])

# --- ROUTE RACINE ---
@app.get("/", tags=["Accueil"])
async def root() -> dict[str, str]:
    """
    Healthcheck de l'API.
    """
    return {
        "message": "Banking Transactions API is Live 🟢",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc"
    }