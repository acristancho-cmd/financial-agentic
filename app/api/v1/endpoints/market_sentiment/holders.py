"""
Endpoint para accionistas
"""
from fastapi import APIRouter, Path
from app.services.market_sentiment_service import MarketSentimentService
from app.models.market_sentiment import HoldersResponse

router = APIRouter(prefix="/holders", tags=["market-sentiment"])


@router.get("/{ticker}", response_model=HoldersResponse)
async def get_holders(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene información de accionistas principales e institucionales"""
    result = MarketSentimentService.get_holders(ticker)
    return result

