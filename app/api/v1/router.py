"""
Router principal de la API v1
Agrupa todos los endpoints de la versión 1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import dividends
from app.api.v1.endpoints.fundamentals import fundamentals, financials, balance_sheet, cashflow, earnings
from app.api.v1.endpoints.technical import history, indicators, volatility, performance
from app.api.v1.endpoints.market_sentiment import recommendations, news, calendar, holders
from app.api.v1.endpoints.comparative import compare, correlation
from app.api.v1.endpoints.corporate_actions import dividends_history, splits
from app.api.v1.endpoints.summary import summary, key_metrics

api_router = APIRouter(prefix="/api/v1")

# Incluir routers de cada funcionalidad
api_router.include_router(dividends.router)

# Análisis fundamental
api_router.include_router(fundamentals.router, prefix="/stocks")
api_router.include_router(financials.router, prefix="/stocks")
api_router.include_router(balance_sheet.router, prefix="/stocks")
api_router.include_router(cashflow.router, prefix="/stocks")
api_router.include_router(earnings.router, prefix="/stocks")

# Análisis técnico
api_router.include_router(history.router, prefix="/stocks")
api_router.include_router(indicators.router, prefix="/stocks")
api_router.include_router(volatility.router, prefix="/stocks")
api_router.include_router(performance.router, prefix="/stocks")

# Mercado y sentimiento
api_router.include_router(recommendations.router, prefix="/stocks")
api_router.include_router(news.router, prefix="/stocks")
api_router.include_router(calendar.router, prefix="/stocks")
api_router.include_router(holders.router, prefix="/stocks")

# Análisis comparativo
api_router.include_router(compare.router, prefix="/stocks")
api_router.include_router(correlation.router, prefix="/stocks")

# Acciones corporativas
api_router.include_router(dividends_history.router, prefix="/stocks")
api_router.include_router(splits.router, prefix="/stocks")

# Resúmenes
api_router.include_router(summary.router, prefix="/stocks")
api_router.include_router(key_metrics.router, prefix="/stocks")


