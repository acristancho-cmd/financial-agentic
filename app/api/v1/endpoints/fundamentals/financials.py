"""
Endpoint para estados financieros
"""
from fastapi import APIRouter, Path
from app.services.fundamentals_service import FundamentalsService
from app.models.fundamentals import FinancialsResponse

router = APIRouter(tags=["fundamentals"])


@router.get("/{ticker}/financials", response_model=FinancialsResponse)
async def get_financials(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene estados financieros históricos"""
    result = FundamentalsService.get_financials(ticker)
    return result

