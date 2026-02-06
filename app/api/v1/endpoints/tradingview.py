"""
Endpoints para TradingView Scraper
"""
from fastapi import APIRouter, Path
from app.services.tradingview_service import TradingViewService
from app.models.tradingview import OverviewResponse, IncomeStatementResponse, StatisticsResponse

router = APIRouter(tags=["tradingview"])


@router.get("/{symbol}/overview", response_model=OverviewResponse)
async def get_overview(symbol: str = Path(..., description="Símbolo en formato TradingView (ej: NASDAQ:AAPL, BVC:ECOPETROL)")):
    """
    Obtiene resumen general de la empresa
    
    Incluye:
    - Datos básicos (nombre, descripción, sector, industria, país)
    - Datos de precio (open, high, low, close, change, volume)
    - Máximos y mínimos de 52 semanas
    """
    result = TradingViewService.get_overview(symbol)
    return result


@router.get("/{symbol}/income-statement", response_model=IncomeStatementResponse)
async def get_income_statement(symbol: str = Path(..., description="Símbolo en formato TradingView (ej: NASDAQ:AAPL, BVC:ECOPETROL)")):
    """
    Obtiene estado de resultados (información financiera)
    
    Incluye:
    - Ingresos totales (anual y TTM)
    - Ganancia bruta
    - Ingresos operativos
    - Ingresos netos
    - EBITDA
    - BPA básico y diluido
    """
    result = TradingViewService.get_income_statement(symbol)
    return result


@router.get("/{symbol}/statistics", response_model=StatisticsResponse)
async def get_statistics(symbol: str = Path(..., description="Símbolo en formato TradingView (ej: NASDAQ:AAPL, BVC:ECOPETROL)")):
    """
    Obtiene estadísticas de mercado y valoración
    
    Incluye:
    - Métricas de mercado (capitalización, acciones en circulación, flotación)
    - Ratios de valoración (P/E, P/B, P/S, P/FCF)
    - Métricas de rentabilidad (ROE, ROA, ROI)
    - Información de dividendos
    """
    result = TradingViewService.get_statistics(symbol)
    return result
