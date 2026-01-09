"""
Endpoint para resumen completo
"""
from fastapi import APIRouter, Path
from app.services.summary_service import SummaryService
from app.models.summary import SummaryResponse

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/{ticker}", response_model=SummaryResponse)
async def get_summary(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene resumen completo de la acción"""
    result = SummaryService.get_summary(ticker)
    return result

