"""
Endpoint para análisis de rendimiento
"""
from fastapi import APIRouter, Path, Query
from app.services.technical_service import TechnicalService
from app.models.technical import PerformanceResponse

router = APIRouter(prefix="/performance", tags=["technical"])


@router.get("/{ticker}", response_model=PerformanceResponse)
async def get_performance(
    ticker: str = Path(..., description="Ticker de la acción"),
    period: str = Query("1y", description="Período: 1mo, 3mo, 6mo, 1y, 2y, 5y")
):
    """Obtiene análisis de rendimiento histórico"""
    result = TechnicalService.get_performance(ticker, period)
    return result

