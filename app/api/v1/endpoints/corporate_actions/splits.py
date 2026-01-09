"""
Endpoint para splits de acciones
"""
from fastapi import APIRouter, Path
from app.services.corporate_actions_service import CorporateActionsService
from app.models.corporate_actions import SplitsResponse

router = APIRouter(tags=["corporate-actions"])


@router.get("/{ticker}/splits", response_model=SplitsResponse)
async def get_splits(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene historial de splits de acciones"""
    result = CorporateActionsService.get_splits(ticker)
    return result

