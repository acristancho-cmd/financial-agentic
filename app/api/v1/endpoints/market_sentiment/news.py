"""
Endpoint para noticias
"""
from fastapi import APIRouter, Path
from app.services.market_sentiment_service import MarketSentimentService
from app.models.market_sentiment import NewsResponse

router = APIRouter(tags=["market-sentiment"])


@router.get("/{ticker}/news", response_model=NewsResponse)
async def get_news(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene noticias recientes relacionadas con la acción"""
    result = MarketSentimentService.get_news(ticker)
    return result

