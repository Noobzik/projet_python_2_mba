from fastapi import APIRouter
from app.services.customers import *
from app.config import connexion_dataset

router = APIRouter(prefix="/api/customers", tags=["Customers"])

# Chargement global du dataset
df = connexion_dataset()

@router.get("/api/transactions/stats")
def get_stats_by_type():
    return stats_by_type(df)


@router.get("/api/transactions/distribution")
def get_amount_distribution():

    return amount_distribution(df)
