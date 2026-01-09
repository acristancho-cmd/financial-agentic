"""
Modelos para análisis de mercado y sentimiento
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class RecommendationResponse(BaseModel):
    """Modelo de respuesta para recomendaciones de analistas"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    recommendations: Optional[List[Dict]] = Field(None, description="Recomendaciones históricas")
    current_rating: Optional[str] = Field(None, description="Rating actual")
    target_price: Optional[float] = Field(None, description="Precio objetivo")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class NewsResponse(BaseModel):
    """Modelo de respuesta para noticias"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    news: List[Dict] = Field(default_factory=list, description="Lista de noticias")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class CalendarResponse(BaseModel):
    """Modelo de respuesta para calendario de eventos"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    earnings_dates: Optional[List] = Field(None, description="Fechas de reportes de ganancias")
    dividend_dates: Optional[List] = Field(None, description="Fechas de dividendos")
    splits: Optional[List] = Field(None, description="Splits programados")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class HoldersResponse(BaseModel):
    """Modelo de respuesta para accionistas"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    major_holders: Optional[List[Dict]] = Field(None, description="Accionistas principales")
    institutional_holders: Optional[List[Dict]] = Field(None, description="Accionistas institucionales")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")

