"""
Modelos para acciones corporativas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class DividendsHistoryResponse(BaseModel):
    """Modelo de respuesta para historial de dividendos"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    dividends: List[Dict] = Field(default_factory=list, description="Historial de dividendos")
    total_dividends: Optional[float] = Field(None, description="Total de dividendos pagados")
    average_dividend: Optional[float] = Field(None, description="Promedio de dividendos")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class SplitsResponse(BaseModel):
    """Modelo de respuesta para splits de acciones"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    splits: List[Dict] = Field(default_factory=list, description="Historial de splits")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")

