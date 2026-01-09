"""
Endpoint para análisis fundamental completo
"""
from fastapi import APIRouter, Path
from app.services.fundamentals_service import FundamentalsService
from app.models.fundamentals import FundamentalsResponse

router = APIRouter(prefix="/fundamentals", tags=["fundamentals"])


@router.get("/{ticker}", response_model=FundamentalsResponse)
async def get_fundamentals(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene análisis fundamental completo de una acción"""
    result = FundamentalsService.get_fundamentals(ticker)
    return result

