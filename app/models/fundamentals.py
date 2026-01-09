"""
Modelos para análisis fundamental
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class FundamentalsResponse(BaseModel):
    """Modelo de respuesta para análisis fundamental completo"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    
    # Valoración
    market_cap: Optional[float] = Field(None, description="Capitalización de mercado")
    enterprise_value: Optional[float] = Field(None, description="Valor empresarial")
    pe_ratio: Optional[float] = Field(None, description="Ratio Precio/Ganancias (P/E)")
    forward_pe: Optional[float] = Field(None, description="P/E Forward")
    peg_ratio: Optional[float] = Field(None, description="Ratio PEG")
    price_to_book: Optional[float] = Field(None, description="Ratio Precio/Valor en libros (P/B)")
    price_to_sales: Optional[float] = Field(None, description="Ratio Precio/Ventas (P/S)")
    ev_to_revenue: Optional[float] = Field(None, description="EV/Revenue")
    ev_to_ebitda: Optional[float] = Field(None, description="EV/EBITDA")
    
    # Rentabilidad
    return_on_equity: Optional[float] = Field(None, description="Retorno sobre el capital (ROE)")
    return_on_assets: Optional[float] = Field(None, description="Retorno sobre activos (ROA)")
    return_on_invested_capital: Optional[float] = Field(None, description="ROIC")
    profit_margins: Optional[float] = Field(None, description="Márgenes de ganancia (%)")
    operating_margins: Optional[float] = Field(None, description="Márgenes operativos (%)")
    gross_margins: Optional[float] = Field(None, description="Márgenes brutos (%)")
    
    # Crecimiento
    revenue_growth: Optional[float] = Field(None, description="Crecimiento de ingresos (%)")
    earnings_growth: Optional[float] = Field(None, description="Crecimiento de ganancias (%)")
    earnings_quarterly_growth: Optional[float] = Field(None, description="Crecimiento trimestral de ganancias (%)")
    revenue_quarterly_growth: Optional[float] = Field(None, description="Crecimiento trimestral de ingresos (%)")
    
    # Eficiencia
    asset_turnover: Optional[float] = Field(None, description="Rotación de activos")
    inventory_turnover: Optional[float] = Field(None, description="Rotación de inventario")
    
    # Deuda y Liquidez
    debt_to_equity: Optional[float] = Field(None, description="Deuda a capital")
    current_ratio: Optional[float] = Field(None, description="Ratio corriente")
    quick_ratio: Optional[float] = Field(None, description="Ratio rápido")
    total_debt: Optional[float] = Field(None, description="Deuda total")
    total_cash: Optional[float] = Field(None, description="Efectivo total")
    
    # Otros
    beta: Optional[float] = Field(None, description="Beta")
    currency: Optional[str] = Field(None, description="Moneda")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industria")
    
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error si status es 'error'")


class FinancialsResponse(BaseModel):
    """Modelo de respuesta para estados financieros"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    financials: Dict = Field(..., description="Estados financieros históricos")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class BalanceSheetResponse(BaseModel):
    """Modelo de respuesta para balance general"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    balance_sheet: Dict = Field(..., description="Balance general histórico")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class CashflowResponse(BaseModel):
    """Modelo de respuesta para flujo de efectivo"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    cashflow: Dict = Field(..., description="Flujo de efectivo histórico")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")


class EarningsResponse(BaseModel):
    """Modelo de respuesta para ganancias"""
    
    ticker: str = Field(..., description="Ticker de la acción")
    earnings: Dict = Field(..., description="Datos de ganancias históricas")
    earnings_dates: Optional[List] = Field(None, description="Fechas de reportes de ganancias")
    status: str = Field(..., description="Estado de la consulta")
    error: Optional[str] = Field(None, description="Mensaje de error")

