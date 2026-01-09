"""
Endpoint para flujo de efectivo
"""
from fastapi import APIRouter, Path
from app.services.fundamentals_service import FundamentalsService
from app.models.fundamentals import CashflowResponse

router = APIRouter(prefix="/cashflow", tags=["fundamentals"])


@router.get("/{ticker}", response_model=CashflowResponse)
async def get_cashflow(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene flujo de efectivo histórico"""
    result = FundamentalsService.get_cashflow(ticker)
    return result

