"""
Modelos para resúmenes y overview
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class SummaryResponse(BaseModel):
    """Modelo de respuesta para resumen completo"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    company_name: Optional[str] = Field(None, description="Nombre de la empresa")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industria")
    current_price: Optional[float] = Field(None, description="Precio actual")
    market_cap: Optional[float] = Field(None, description="Capitalización de mercado")
    key_metrics: Dict = Field(default_factory=dict, description="Métricas clave")
    financial_highlights: Dict = Field(default_factory=dict, description="Resumen financiero")
    recommendations: Optional[str] = Field(None, description="Recomendación actual")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class KeyMetricsResponse(BaseModel):
    """Modelo de respuesta para métricas clave"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    valuation_metrics: Dict = Field(default_factory=dict, description="Métricas de valoración")
    profitability_metrics: Dict = Field(default_factory=dict, description="Métricas de rentabilidad")
    growth_metrics: Dict = Field(default_factory=dict, description="Métricas de crecimiento")
    efficiency_metrics: Dict = Field(default_factory=dict, description="Métricas de eficiencia")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")

