"""
Endpoint para análisis de volatilidad
"""
from fastapi import APIRouter, Path, Query
from app.services.technical_service import TechnicalService
from app.models.technical import VolatilityResponse

router = APIRouter(tags=["technical"])


@router.get("/{ticker}/volatility", response_model=VolatilityResponse)
async def get_volatility(
    ticker: str = Path(..., description="Ticker de la acción"),
    period: str = Query("1y", description="Período: 1mo, 3mo, 6mo, 1y, 2y, 5y")
):
    """Obtiene análisis de volatilidad y riesgo"""
    result = TechnicalService.get_volatility(ticker, period)
    return result

