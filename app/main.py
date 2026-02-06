"""
Punto de entrada principal de la aplicación FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS (permitir todas las origenes en desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API
app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "endpoints": {
            "overview": "/api/v1/stocks/{symbol}/overview - Resumen general de la empresa",
            "income_statement": "/api/v1/stocks/{symbol}/income-statement - Estado de resultados",
            "statistics": "/api/v1/stocks/{symbol}/statistics - Estadísticas de mercado y valoración",
            "docs": "/docs - Documentación interactiva (Swagger UI)",
            "redoc": "/redoc - Documentación alternativa (ReDoc)",
            "health": "/health - Health check"
        },
        "note": "Los símbolos deben incluir el prefijo del exchange (ej: NASDAQ:AAPL, BVC:ECOPETROL)"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint de salud para verificar que la API está funcionando"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


