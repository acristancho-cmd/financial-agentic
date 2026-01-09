"""
Endpoint para calendario de eventos
"""
from fastapi import APIRouter, Path
from app.services.market_sentiment_service import MarketSentimentService
from app.models.market_sentiment import CalendarResponse

router = APIRouter(prefix="/calendar", tags=["market-sentiment"])


@router.get("/{ticker}", response_model=CalendarResponse)
async def get_calendar(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene calendario de eventos (earnings, dividendos, splits)"""
    result = MarketSentimentService.get_calendar(ticker)
    return result

