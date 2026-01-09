"""
Endpoint para ganancias
"""
from fastapi import APIRouter, Path
from app.services.fundamentals_service import FundamentalsService
from app.models.fundamentals import EarningsResponse

router = APIRouter(prefix="/earnings", tags=["fundamentals"])


@router.get("/{ticker}", response_model=EarningsResponse)
async def get_earnings(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene datos históricos de ganancias"""
    result = FundamentalsService.get_earnings(ticker)
    return result

