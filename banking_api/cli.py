import uvicorn


def main() -> None:
    """Point d'entrée CLI pour lancer l'API."""
    uvicorn.run(
        "banking_api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
