"""
Modelos para análisis comparativo y correlación
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class CompareResponse(BaseModel):
    """Modelo de respuesta para comparación de acciones"""
    
    tickers: List[str] = Field(..., description="Lista de tickers comparados")
    comparison: Dict = Field(..., description="Comparación de métricas clave")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class CorrelationResponse(BaseModel):
    """Modelo de respuesta para correlación entre acciones"""
    
    ticker: str = Field(..., description="Ticker principal")
    correlations: Dict[str, float] = Field(..., description="Correlaciones con otros tickers")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")

