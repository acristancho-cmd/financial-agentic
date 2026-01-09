"""
Endpoint para datos históricos
"""
from fastapi import APIRouter, Path, Query
from app.services.technical_service import TechnicalService
from app.models.technical import HistoryResponse

router = APIRouter(prefix="/history", tags=["technical"])


@router.get("/{ticker}", response_model=HistoryResponse)
async def get_history(
    ticker: str = Path(..., description="Ticker de la acción"),
    period: str = Query("1y", description="Período: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """Obtiene datos históricos OHLCV"""
    result = TechnicalService.get_history(ticker, period, interval)
    return result

