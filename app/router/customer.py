from fastapi import APIRouter, Query
from typing import List
# Importation du DataFrame et des fonctions depuis ton service
from app.services.customers import *
from app.config import connexion_dataset

df=connexion_dataset()
# On laisse le prefix vide ici pour respecter tes noms de routes complets
router_customers = APIRouter(
    tags=["Customers"]
)

@router_customers.get("/api/customers")
def list_customers_route():
    # Appelle la fonction de service au lieu de retourner "suis la"
    return list_customers(df)

@router_customers.get("/api/customers/top")
def get_top_customers(n: int = Query(10)):
    return top_customers(df, n=n)

@router_customers.get("/transactions/stats-by-type")
def get_stats_by_type():
    return stats_by_type(df)

@router_customers.get("/transactions/amount-distribution")
def get_amount_distribution():
    return amount_distribution(df)