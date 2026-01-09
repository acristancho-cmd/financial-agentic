"""
Endpoint para correlación entre acciones
"""
from fastapi import APIRouter, Path, Query
from app.services.comparative_service import ComparativeService
from app.utils.ticker_formatter import parse_ticker_list
from app.models.comparative import CorrelationResponse

router = APIRouter(prefix="/correlation", tags=["comparative"])


@router.get("/{ticker}", response_model=CorrelationResponse)
async def get_correlation(
    ticker: str = Path(..., description="Ticker principal"),
    compare_tickers: str = Query(..., description="Tickers para comparar separados por comas (ej: TSLA,MSFT,GOOGL)"),
    period: str = Query("1y", description="Período para cálculo: 1mo, 3mo, 6mo, 1y, 2y")
):
    """Calcula correlación entre un ticker y otros tickers"""
    ticker_list = parse_ticker_list(tickers=compare_tickers)
    if not ticker_list:
        return {"ticker": ticker, "correlations": {}, "error": "No se proporcionaron tickers válidos", "status": "error"}
    
    result = ComparativeService.get_correlation(ticker, ticker_list, period)
    return result

