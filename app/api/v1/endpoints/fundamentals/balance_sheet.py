"""
Endpoint para balance general
"""
from fastapi import APIRouter, Path
from app.services.fundamentals_service import FundamentalsService
from app.models.fundamentals import BalanceSheetResponse

router = APIRouter(tags=["fundamentals"])


@router.get("/{ticker}/balance-sheet", response_model=BalanceSheetResponse)
async def get_balance_sheet(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene balance general histórico"""
    result = FundamentalsService.get_balance_sheet(ticker)
    return result

