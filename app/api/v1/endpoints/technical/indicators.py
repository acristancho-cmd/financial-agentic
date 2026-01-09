"""
Endpoint para indicadores técnicos
"""
from fastapi import APIRouter, Path, Query
from app.services.technical_service import TechnicalService
from app.models.technical import TechnicalIndicatorsResponse

router = APIRouter(tags=["technical"])


@router.get("/{ticker}/technical-indicators", response_model=TechnicalIndicatorsResponse)
async def get_technical_indicators(
    ticker: str = Path(..., description="Ticker de la acción"),
    period: str = Query("6mo", description="Período para cálculo: 1mo, 3mo, 6mo, 1y, 2y")
):
    """Obtiene indicadores técnicos (RSI, MACD, Bollinger Bands, etc.)"""
    result = TechnicalService.get_technical_indicators(ticker, period)
    return result

