"""
Main FastAPI application for Banking Transactions API.

This module initializes the FastAPI application and registers all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api import transactions, stats, fraud, customers, system
from app.utils.loader import load_transactions

# Create FastAPI application
app = FastAPI(
    title="Banking Transactions API",
    version="1.0.0",
    description="API REST pour l'exposition des données de transactions bancaires",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event() -> None:
    """
    Load data on application startup.

    Returns
    -------
    None
    """
    print("🚀 Starting Banking Transactions API...")
    try:
        load_transactions()
        print("✅ API ready!")
    except Exception as e:
        print(f"⚠️  Warning: Could not load data: {e}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Clean up on application shutdown.

    Returns
    -------
    None
    """
    print("👋 Shutting down Banking Transactions API...")


# Include routers
app.include_router(transactions.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(fraud.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(system.router, prefix="/api")


# Root endpoint
@app.get("/", response_class=HTMLResponse, tags=["Root"])
def read_root() -> str:
    """
    Root endpoint with API information.

    Returns
    -------
    str
        HTML page with API information and links
    """
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Banking Transactions API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                .info {
                    background-color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .links {
                    margin-top: 30px;
                }
                .link-button {
                    display: inline-block;
                    padding: 12px 24px;
                    margin: 10px 10px 10px 0;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                .link-button:hover {
                    background-color: #2980b9;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin-top: 20px;
                }
                .stat-box {
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                }
                .stat-number {
                    font-size: 32px;
                    font-weight: bold;
                }
                .stat-label {
                    font-size: 14px;
                    margin-top: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏦 Banking Transactions API</h1>
                
                <div class="info">
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Description:</strong> API REST pour l'analyse des transactions bancaires</p>
                    <p><strong>Framework:</strong> FastAPI</p>
                </div>

                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">20</div>
                        <div class="stat-label">Routes API</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">5</div>
                        <div class="stat-label">Catégories</div>
                    </div>
                </div>

                <div class="links">
                    <h2>📚 Documentation</h2>
                    <a href="/docs" class="link-button">📖 Swagger UI</a>
                    <a href="/redoc" class="link-button">📘 ReDoc</a>
                </div>

                <div class="links">
                    <h2>🔍 Endpoints Principaux</h2>
                    <ul>
                        <li><strong>Transactions:</strong> /api/transactions (8 routes)</li>
                        <li><strong>Statistiques:</strong> /api/stats (4 routes)</li>
                        <li><strong>Fraude:</strong> /api/fraud (3 routes)</li>
                        <li><strong>Clients:</strong> /api/customers (3 routes)</li>
                        <li><strong>Système:</strong> /api/system (2 routes)</li>
                    </ul>
                </div>

                <div class="info" style="margin-top: 30px;">
                    <p>💡 <strong>Astuce:</strong> Utilisez Swagger UI pour tester interactivement toutes les routes !</p>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content