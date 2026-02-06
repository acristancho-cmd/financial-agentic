"""
Modelos Pydantic para respuestas de TradingView Scraper
"""
from pydantic import BaseModel
from typing import Optional


# ==================== MODELO 1: RESUMEN GENERAL ====================
class OverviewResponse(BaseModel):
    """Resumen general de la empresa"""
    # Datos básicos
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    exchange: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency_code: Optional[str] = None
    
    # Datos de precio
    close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    change: Optional[float] = None
    change_abs: Optional[float] = None
    volume: Optional[float] = None
    
    # Máximos y mínimos
    high_52_week: Optional[float] = None
    low_52_week: Optional[float] = None
    
    # Estado
    status: str = "success"
    error: Optional[str] = None


# ==================== MODELO 2: INFORMACIÓN FINANCIERA (ESTADO DE RESULTADOS) ====================
class IncomeStatementResponse(BaseModel):
    """Estado de resultados - Información financiera"""
    # Ingresos
    total_revenue: Optional[float] = None
    revenue_per_share_ttm: Optional[float] = None
    total_revenue_fy: Optional[float] = None
    
    # Ganancia bruta
    gross_profit: Optional[float] = None
    gross_profit_fy: Optional[float] = None
    
    # Ingresos operativos
    operating_income: Optional[float] = None
    operating_income_fy: Optional[float] = None
    
    # Ingresos netos
    net_income: Optional[float] = None
    net_income_fy: Optional[float] = None
    
    # EBITDA
    EBITDA: Optional[float] = None
    
    # EPS
    basic_eps_net_income: Optional[float] = None
    earnings_per_share_basic_ttm: Optional[float] = None
    earnings_per_share_diluted_ttm: Optional[float] = None
    
    # Estado
    status: str = "success"
    error: Optional[str] = None


# ==================== MODELO 3: ESTADÍSTICAS ====================
class StatisticsResponse(BaseModel):
    """Estadísticas de mercado y valoración"""
    # Métricas de mercado
    market_cap_basic: Optional[float] = None
    shares_outstanding: Optional[float] = None
    shares_float: Optional[float] = None
    shares_diluted: Optional[float] = None
    
    # Ratios de valoración
    price_earnings_ttm: Optional[float] = None
    price_book_fq: Optional[float] = None
    price_sales_ttm: Optional[float] = None
    price_free_cash_flow_ttm: Optional[float] = None
    enterprise_value_fq: Optional[float] = None
    
    # Métricas de rentabilidad
    earnings_per_share_basic_ttm: Optional[float] = None
    earnings_per_share_diluted_ttm: Optional[float] = None
    return_on_equity_fq: Optional[float] = None
    return_on_assets_fq: Optional[float] = None
    return_on_investment_ttm: Optional[float] = None
    
    # Dividendos
    dividends_yield: Optional[float] = None
    dividends_per_share_fq: Optional[float] = None
    
    # Estado
    status: str = "success"
    error: Optional[str] = None
