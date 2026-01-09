"""
Endpoint para métricas clave
"""
from fastapi import APIRouter, Path
from app.services.summary_service import SummaryService
from app.models.summary import KeyMetricsResponse

router = APIRouter(tags=["summary"])


@router.get("/{ticker}/key-metrics", response_model=KeyMetricsResponse)
async def get_key_metrics(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene métricas clave organizadas por categoría"""
    result = SummaryService.get_key_metrics(ticker)
    return result

