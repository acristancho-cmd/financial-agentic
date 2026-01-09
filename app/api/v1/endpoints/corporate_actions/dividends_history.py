"""
Endpoint para historial de dividendos
"""
from fastapi import APIRouter, Path
from app.services.corporate_actions_service import CorporateActionsService
from app.models.corporate_actions import DividendsHistoryResponse

router = APIRouter(tags=["corporate-actions"])


@router.get("/{ticker}/dividends-history", response_model=DividendsHistoryResponse)
async def get_dividends_history(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene historial completo de dividendos pagados"""
    result = CorporateActionsService.get_dividends_history(ticker)
    return result

