from fastapi import APIRouter
from app.services.customers import *
from app.config import connexion_dataset

router = APIRouter(prefix="/api/customers", tags=["Customers"])

# Chargement global du dataset
df = connexion_dataset()


@router.get("/api/customers")
def get_customers():
    
    customers = list_customers(df)
    return {
        "total": len(customers),
        "customers": customers
    }


@router.get("/api/customers/top")
def get_top_customers():
    return top_customers(df, n=10)

