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
            "dividends": "/api/v1/dividends - Consulta información de dividendos",
            "fundamentals": "/api/v1/stocks/{ticker}/fundamentals - Análisis fundamental completo",
            "financials": "/api/v1/stocks/{ticker}/financials - Estados financieros",
            "balance_sheet": "/api/v1/stocks/{ticker}/balance-sheet - Balance general",
            "cashflow": "/api/v1/stocks/{ticker}/cashflow - Flujo de efectivo",
            "earnings": "/api/v1/stocks/{ticker}/earnings - Datos de ganancias",
            "history": "/api/v1/stocks/{ticker}/history - Datos históricos OHLCV",
            "technical_indicators": "/api/v1/stocks/{ticker}/technical-indicators - Indicadores técnicos",
            "volatility": "/api/v1/stocks/{ticker}/volatility - Análisis de volatilidad",
            "performance": "/api/v1/stocks/{ticker}/performance - Análisis de rendimiento",
            "recommendations": "/api/v1/stocks/{ticker}/recommendations - Recomendaciones de analistas",
            "news": "/api/v1/stocks/{ticker}/news - Noticias recientes",
            "calendar": "/api/v1/stocks/{ticker}/calendar - Calendario de eventos",
            "holders": "/api/v1/stocks/{ticker}/holders - Accionistas",
            "compare": "/api/v1/stocks/compare?tickers=... - Comparar múltiples acciones",
            "correlation": "/api/v1/stocks/correlation/{ticker}?compare_tickers=... - Correlación entre acciones",
            "dividends_history": "/api/v1/stocks/{ticker}/dividends-history - Historial de dividendos",
            "splits": "/api/v1/stocks/{ticker}/splits - Historial de splits",
            "summary": "/api/v1/stocks/{ticker}/summary - Resumen completo",
            "key_metrics": "/api/v1/stocks/{ticker}/key-metrics - Métricas clave",
            "docs": "/docs - Documentación interactiva (Swagger UI)",
            "redoc": "/redoc - Documentación alternativa (ReDoc)",
            "health": "/health - Health check"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint de salud para verificar que la API está funcionando"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


