"""
Servicio para resúmenes y overview
"""
import yfinance as yf
from typing import Dict
from app.utils.ticker_formatter import format_ticker
from app.services.fundamentals_service import FundamentalsService


class SummaryService:
    """Servicio para resúmenes"""
    
    @staticmethod
    def get_summary(ticker: str) -> Dict:
        """Obtiene resumen completo"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            info = stock.info
            hist = stock.history(period="1d")
            
            current_price = float(hist['Close'].iloc[-1]) if not hist.empty else None
            
            # Obtener métricas clave
            fundamentals = FundamentalsService.get_fundamentals(ticker)
            
            key_metrics = {
                "market_cap": fundamentals.get("market_cap"),
                "pe_ratio": fundamentals.get("pe_ratio"),
                "price_to_book": fundamentals.get("price_to_book"),
                "return_on_equity": fundamentals.get("return_on_equity"),
                "profit_margins": fundamentals.get("profit_margins"),
                "revenue_growth": fundamentals.get("revenue_growth"),
                "earnings_growth": fundamentals.get("earnings_growth"),
                "debt_to_equity": fundamentals.get("debt_to_equity"),
                "current_ratio": fundamentals.get("current_ratio"),
                "beta": fundamentals.get("beta")
            }
            
            financial_highlights = {
                "total_revenue": info.get("totalRevenue"),
                "gross_profit": info.get("grossProfits"),
                "operating_income": info.get("operatingIncome"),
                "net_income": info.get("netIncomeToCommon"),
                "total_assets": info.get("totalAssets"),
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash"),
                "free_cashflow": info.get("freeCashflow")
            }
            
            return {
                "ticker": ticker_formatted,
                "company_name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "current_price": current_price,
                "market_cap": fundamentals.get("market_cap"),
                "key_metrics": key_metrics,
                "financial_highlights": financial_highlights,
                "recommendations": info.get("recommendationKey"),
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_key_metrics(ticker: str) -> Dict:
        """Obtiene métricas clave organizadas por categoría"""
        try:
            fundamentals = FundamentalsService.get_fundamentals(ticker)
            
            if fundamentals.get("status") != "success":
                return fundamentals
            
            valuation_metrics = {
                "market_cap": fundamentals.get("market_cap"),
                "enterprise_value": fundamentals.get("enterprise_value"),
                "pe_ratio": fundamentals.get("pe_ratio"),
                "forward_pe": fundamentals.get("forward_pe"),
                "peg_ratio": fundamentals.get("peg_ratio"),
                "price_to_book": fundamentals.get("price_to_book"),
                "price_to_sales": fundamentals.get("price_to_sales"),
                "ev_to_revenue": fundamentals.get("ev_to_revenue"),
                "ev_to_ebitda": fundamentals.get("ev_to_ebitda")
            }
            
            profitability_metrics = {
                "return_on_equity": fundamentals.get("return_on_equity"),
                "return_on_assets": fundamentals.get("return_on_assets"),
                "return_on_invested_capital": fundamentals.get("return_on_invested_capital"),
                "profit_margins": fundamentals.get("profit_margins"),
                "operating_margins": fundamentals.get("operating_margins"),
                "gross_margins": fundamentals.get("gross_margins")
            }
            
            growth_metrics = {
                "revenue_growth": fundamentals.get("revenue_growth"),
                "earnings_growth": fundamentals.get("earnings_growth"),
                "earnings_quarterly_growth": fundamentals.get("earnings_quarterly_growth"),
                "revenue_quarterly_growth": fundamentals.get("revenue_quarterly_growth")
            }
            
            efficiency_metrics = {
                "asset_turnover": fundamentals.get("asset_turnover"),
                "inventory_turnover": fundamentals.get("inventory_turnover"),
                "current_ratio": fundamentals.get("current_ratio"),
                "quick_ratio": fundamentals.get("quick_ratio")
            }
            
            return {
                "ticker": fundamentals.get("ticker"),
                "valuation_metrics": valuation_metrics,
                "profitability_metrics": profitability_metrics,
                "growth_metrics": growth_metrics,
                "efficiency_metrics": efficiency_metrics,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

