"""
Servicio para obtener datos de TradingView usando tradingview-scraper
"""
from typing import Dict, Any, Optional
from tradingview_scraper.symbols.overview import Overview
from tradingview_scraper.symbols.fundamental_graphs import FundamentalGraphs
from app.models.tradingview import OverviewResponse, IncomeStatementResponse, StatisticsResponse


class TradingViewService:
    """Servicio para obtener datos de TradingView"""
    
    @staticmethod
    def get_overview(symbol: str) -> OverviewResponse:
        """
        Obtiene resumen general de la empresa
        
        Args:
            symbol: Símbolo en formato TradingView (ej: "NASDAQ:AAPL", "BVC:ECOPETROL")
        
        Returns:
            OverviewResponse con datos del resumen general
        """
        try:
            overview_scraper = Overview()
            result = overview_scraper.get_symbol_overview(symbol=symbol)
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                return OverviewResponse(
                    name=data.get('name'),
                    description=data.get('description'),
                    type=data.get('type'),
                    exchange=data.get('exchange'),
                    country=data.get('country'),
                    sector=data.get('sector'),
                    industry=data.get('industry'),
                    currency_code=data.get('currency_code'),
                    close=data.get('close'),
                    open=data.get('open'),
                    high=data.get('high'),
                    low=data.get('low'),
                    change=data.get('change'),
                    change_abs=data.get('change_abs'),
                    volume=data.get('volume'),
                    high_52_week=data.get('high_52_week'),
                    low_52_week=data.get('low_52_week'),
                    status="success"
                )
            else:
                error_msg = result.get('error', result.get('errmsg', 'Error desconocido'))
                return OverviewResponse(status="error", error=str(error_msg))
                
        except Exception as e:
            return OverviewResponse(status="error", error=str(e))
    
    @staticmethod
    def get_income_statement(symbol: str) -> IncomeStatementResponse:
        """
        Obtiene estado de resultados (información financiera)
        
        Args:
            symbol: Símbolo en formato TradingView (ej: "NASDAQ:AAPL", "BVC:ECOPETROL")
        
        Returns:
            IncomeStatementResponse con datos del estado de resultados
        """
        try:
            fundamentals_scraper = FundamentalGraphs()
            result = fundamentals_scraper.get_income_statement(symbol=symbol)
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                return IncomeStatementResponse(
                    total_revenue=data.get('total_revenue'),
                    revenue_per_share_ttm=data.get('revenue_per_share_ttm'),
                    total_revenue_fy=data.get('total_revenue_fy'),
                    gross_profit=data.get('gross_profit'),
                    gross_profit_fy=data.get('gross_profit_fy'),
                    operating_income=data.get('operating_income'),
                    operating_income_fy=data.get('operating_income_fy'),
                    net_income=data.get('net_income'),
                    net_income_fy=data.get('net_income_fy'),
                    EBITDA=data.get('EBITDA'),
                    basic_eps_net_income=data.get('basic_eps_net_income'),
                    earnings_per_share_basic_ttm=data.get('earnings_per_share_basic_ttm'),
                    earnings_per_share_diluted_ttm=data.get('earnings_per_share_diluted_ttm'),
                    status="success"
                )
            else:
                error_msg = result.get('error', result.get('errmsg', 'Error desconocido'))
                return IncomeStatementResponse(status="error", error=str(error_msg))
                
        except Exception as e:
            return IncomeStatementResponse(status="error", error=str(e))
    
    @staticmethod
    def get_statistics(symbol: str) -> StatisticsResponse:
        """
        Obtiene estadísticas de mercado y valoración
        
        Args:
            symbol: Símbolo en formato TradingView (ej: "NASDAQ:AAPL", "BVC:ECOPETROL")
        
        Returns:
            StatisticsResponse con estadísticas
        """
        try:
            overview_scraper = Overview()
            result = overview_scraper.get_statistics(symbol=symbol)
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                return StatisticsResponse(
                    market_cap_basic=data.get('market_cap_basic'),
                    shares_outstanding=data.get('shares_outstanding'),
                    shares_float=data.get('shares_float'),
                    shares_diluted=data.get('shares_diluted'),
                    price_earnings_ttm=data.get('price_earnings_ttm'),
                    price_book_fq=data.get('price_book_fq'),
                    price_sales_ttm=data.get('price_sales_ttm'),
                    price_free_cash_flow_ttm=data.get('price_free_cash_flow_ttm'),
                    enterprise_value_fq=data.get('enterprise_value_fq'),
                    earnings_per_share_basic_ttm=data.get('earnings_per_share_basic_ttm'),
                    earnings_per_share_diluted_ttm=data.get('earnings_per_share_diluted_ttm'),
                    return_on_equity_fq=data.get('return_on_equity_fq'),
                    return_on_assets_fq=data.get('return_on_assets_fq'),
                    return_on_investment_ttm=data.get('return_on_investment_ttm'),
                    dividends_yield=data.get('dividends_yield'),
                    dividends_per_share_fq=data.get('dividends_per_share_fq'),
                    status="success"
                )
            else:
                error_msg = result.get('error', result.get('errmsg', 'Error desconocido'))
                return StatisticsResponse(status="error", error=str(error_msg))
                
        except Exception as e:
            return StatisticsResponse(status="error", error=str(e))
