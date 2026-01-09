"""
Endpoint para comparación de acciones
"""
from fastapi import APIRouter, Query
from typing import List
from app.services.comparative_service import ComparativeService
from app.utils.ticker_formatter import parse_ticker_list
from app.models.comparative import CompareResponse

router = APIRouter(prefix="/compare", tags=["comparative"])


@router.get("", response_model=CompareResponse)
async def compare_tickers(
    tickers: str = Query(..., description="Múltiples tickers separados por comas (ej: AAPL,TSLA,MSFT)")
):
    """Compara métricas clave entre múltiples acciones"""
    ticker_list = parse_ticker_list(tickers=tickers)
    if not ticker_list:
        return {"tickers": [], "comparison": {}, "error": "No se proporcionaron tickers válidos", "status": "error"}
    
    result = ComparativeService.compare_tickers(ticker_list)
    return result

