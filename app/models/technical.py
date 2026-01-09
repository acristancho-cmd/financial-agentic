"""
Modelos para análisis técnico
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class HistoryResponse(BaseModel):
    """Modelo de respuesta para datos históricos"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    history: List[Dict] = Field(..., description="Datos históricos OHLCV")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class TechnicalIndicatorsResponse(BaseModel):
    """Modelo de respuesta para indicadores técnicos"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    rsi: Optional[float] = Field(None, description="RSI (Relative Strength Index)")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="Señal MACD")
    macd_histogram: Optional[float] = Field(None, description="Histograma MACD")
    bollinger_upper: Optional[float] = Field(None, description="Banda superior de Bollinger")
    bollinger_middle: Optional[float] = Field(None, description="Banda media de Bollinger")
    bollinger_lower: Optional[float] = Field(None, description="Banda inferior de Bollinger")
    sma_20: Optional[float] = Field(None, description="Media móvil simple 20 días")
    sma_50: Optional[float] = Field(None, description="Media móvil simple 50 días")
    sma_200: Optional[float] = Field(None, description="Media móvil simple 200 días")
    ema_12: Optional[float] = Field(None, description="Media móvil exponencial 12 días")
    ema_26: Optional[float] = Field(None, description="Media móvil exponencial 26 días")
    adx: Optional[float] = Field(None, description="ADX (Average Directional Index)")
    stochastic_k: Optional[float] = Field(None, description="Estocástico %K")
    stochastic_d: Optional[float] = Field(None, description="Estocástico %D")
    current_price: Optional[float] = Field(None, description="Precio actual")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class VolatilityResponse(BaseModel):
    """Modelo de respuesta para análisis de volatilidad"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    volatility: Optional[float] = Field(None, description="Volatilidad anualizada (%)")
    beta: Optional[float] = Field(None, description="Beta")
    daily_volatility: Optional[float] = Field(None, description="Volatilidad diaria (%)")
    max_drawdown: Optional[float] = Field(None, description="Máximo drawdown (%)")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe Ratio")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class PerformanceResponse(BaseModel):
    """Modelo de respuesta para análisis de rendimiento"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    daily_return: Optional[float] = Field(None, description="Retorno diario (%)")
    weekly_return: Optional[float] = Field(None, description="Retorno semanal (%)")
    monthly_return: Optional[float] = Field(None, description="Retorno mensual (%)")
    ytd_return: Optional[float] = Field(None, description="Retorno año a la fecha (%)")
    annual_return: Optional[float] = Field(None, description="Retorno anual (%)")
    max_drawdown: Optional[float] = Field(None, description="Máximo drawdown (%)")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe Ratio")
    volatility: Optional[float] = Field(None, description="Volatilidad (%)")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")

