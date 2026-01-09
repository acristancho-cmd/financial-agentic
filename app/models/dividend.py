"""
Modelos y schemas relacionados con dividendos
"""
from pydantic import BaseModel, Field
from typing import Optional


class DividendResponse(BaseModel):
    """Modelo de respuesta para información de dividendos y salud financiera"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    
    # Métricas básicas de dividendos
    dividend_yield: str = Field(..., description="Rendimiento de dividendos (ej: '5.19%')")
    payout_ratio: float = Field(..., description="Ratio de pago de dividendos en porcentaje")
    dividend_rate: float = Field(..., description="Tasa de dividendos anual")
    last_dividend_value: float = Field(..., description="Valor del último dividendo pagado")
    currency: str = Field(..., description="Moneda de la acción")
    
    # Métricas históricas y proyectadas de dividendos
    trailing_annual_dividend_rate: float = Field(..., description="Tasa anual de dividendos trailing (últimos 12 meses)")
    trailing_annual_dividend_yield: float = Field(..., description="Rendimiento anual de dividendos trailing")
    five_year_avg_dividend_yield: float = Field(..., description="Promedio de rendimiento de dividendos de 5 años")
    forward_dividend_yield: float = Field(..., description="Rendimiento de dividendos proyectado")
    forward_dividend_rate: float = Field(..., description="Tasa de dividendos proyectada")
    
    # Métricas de salud financiera (capacidad de pagar dividendos)
    free_cashflow: float = Field(..., description="Flujo de caja libre (capacidad de pagar dividendos)")
    operating_cashflow: float = Field(..., description="Flujo de caja operativo")
    current_ratio: float = Field(..., description="Ratio de liquidez corriente")
    debt_to_equity: float = Field(..., description="Ratio de deuda a capital")
    return_on_equity: float = Field(..., description="Retorno sobre el capital (ROE)")
    profit_margins: float = Field(..., description="Márgenes de ganancia en porcentaje")
    earnings_growth: float = Field(..., description="Crecimiento de ganancias en porcentaje")
    
    status: str = Field(..., description="Estado de la consulta: 'success' o 'error'")
    error: Optional[str] = Field(None, description="Mensaje de error si status es 'error'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "dividend_yield": "0.5%",
                "payout_ratio": 15.2,
                "dividend_rate": 0.96,
                "last_dividend_value": 0.24,
                "currency": "USD",
                "trailing_annual_dividend_rate": 0.96,
                "trailing_annual_dividend_yield": 0.5,
                "five_year_avg_dividend_yield": 1.2,
                "forward_dividend_yield": 0.52,
                "forward_dividend_rate": 1.0,
                "free_cashflow": 99584000000,
                "operating_cashflow": 110543000000,
                "current_ratio": 1.05,
                "debt_to_equity": 172.5,
                "return_on_equity": 172.5,
                "profit_margins": 25.3,
                "earnings_growth": 13.9,
                "status": "success"
            }
        }


class DividendErrorResponse(BaseModel):
    """Modelo de respuesta para errores en consultas de dividendos"""
    
    ticker: str = Field(..., description="Ticker que generó el error")
    error: str = Field(..., description="Mensaje de error")
    status: str = Field(default="error", description="Estado de la consulta")


