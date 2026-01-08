"""
Modelos y schemas relacionados con dividendos
"""
from pydantic import BaseModel, Field
from typing import Optional


class DividendResponse(BaseModel):
    """Modelo de respuesta para información de dividendos"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    dividend_yield: float = Field(..., description="Rendimiento de dividendos en porcentaje")
    payout_ratio: float = Field(..., description="Ratio de pago de dividendos en porcentaje")
    dividend_rate: float = Field(..., description="Tasa de dividendos anual")
    last_dividend_value: float = Field(..., description="Valor del último dividendo pagado")
    currency: str = Field(..., description="Moneda de la acción")
    status: str = Field(..., description="Estado de la consulta: 'success' o 'error'")
    error: Optional[str] = Field(None, description="Mensaje de error si status es 'error'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "dividend_yield": 0.5,
                "payout_ratio": 15.2,
                "dividend_rate": 0.96,
                "last_dividend_value": 0.24,
                "currency": "USD",
                "status": "success"
            }
        }


class DividendErrorResponse(BaseModel):
    """Modelo de respuesta para errores en consultas de dividendos"""
    
    ticker: str = Field(..., description="Ticker que generó el error")
    error: str = Field(..., description="Mensaje de error")
    status: str = Field(default="error", description="Estado de la consulta")

