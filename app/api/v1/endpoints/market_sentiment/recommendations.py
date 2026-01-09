"""
Endpoint para recomendaciones de analistas
"""
from fastapi import APIRouter, Path
from app.services.market_sentiment_service import MarketSentimentService
from app.models.market_sentiment import RecommendationResponse

router = APIRouter(prefix="/recommendations", tags=["market-sentiment"])


@router.get("/{ticker}", response_model=RecommendationResponse)
async def get_recommendations(ticker: str = Path(..., description="Ticker de la acción")):
    """Obtiene recomendaciones de analistas"""
    result = MarketSentimentService.get_recommendations(ticker)
    return result

