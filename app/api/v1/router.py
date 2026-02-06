"""
Router principal de la API v1
Solo incluye los 3 endpoints de TradingView
"""
from fastapi import APIRouter
from app.api.v1.endpoints import tradingview

api_router = APIRouter(prefix="/api/v1")

# Incluir router de TradingView
api_router.include_router(tradingview.router, prefix="/stocks")
