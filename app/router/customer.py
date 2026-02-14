from fastapi import APIRouter, Query
from typing import List
from app.services.customers import *
from app.config import connexion_dataset

df=connexion_dataset()

router_customers = APIRouter(
    tags=["Customers"]
)

@router_customers.get("/api/customers")
def list_customers_route():
    # Appelle la fonction de service 
    return list_customers(df)

@router_customers.get("/api/customers/top")
def get_top_customers(n: int = Query(10)):
    return top_customers(df, n=n)

