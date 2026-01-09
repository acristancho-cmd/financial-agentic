"""
Servicio para análisis fundamental
"""
import yfinance as yf
from typing import Dict, Optional
from app.utils.ticker_formatter import format_ticker


class FundamentalsService:
    """Servicio para análisis fundamental"""
    
    @staticmethod
    def safe_get(info: dict, key: str, default=None):
        """Obtiene valor de forma segura"""
        value = info.get(key)
        return value if value is not None else default
    
    @staticmethod
    def get_fundamentals(ticker: str) -> Dict:
        """Obtiene análisis fundamental completo"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            info = stock.info
            
            return {
                "ticker": ticker_formatted,
                "market_cap": FundamentalsService.safe_get(info, "marketCap"),
                "enterprise_value": FundamentalsService.safe_get(info, "enterpriseValue"),
                "pe_ratio": FundamentalsService.safe_get(info, "trailingPE"),
                "forward_pe": FundamentalsService.safe_get(info, "forwardPE"),
                "peg_ratio": FundamentalsService.safe_get(info, "pegRatio"),
                "price_to_book": FundamentalsService.safe_get(info, "priceToBook"),
                "price_to_sales": FundamentalsService.safe_get(info, "priceToSalesTrailing12Months"),
                "ev_to_revenue": FundamentalsService.safe_get(info, "enterpriseToRevenue"),
                "ev_to_ebitda": FundamentalsService.safe_get(info, "enterpriseToEbitda"),
                "return_on_equity": FundamentalsService.safe_get(info, "returnOnEquity"),
                "return_on_assets": FundamentalsService.safe_get(info, "returnOnAssets"),
                "return_on_invested_capital": FundamentalsService.safe_get(info, "returnOnInvestedCapital"),
                "profit_margins": (FundamentalsService.safe_get(info, "profitMargins") or 0) * 100,
                "operating_margins": (FundamentalsService.safe_get(info, "operatingMargins") or 0) * 100,
                "gross_margins": (FundamentalsService.safe_get(info, "grossMargins") or 0) * 100,
                "revenue_growth": (FundamentalsService.safe_get(info, "revenueGrowth") or 0) * 100,
                "earnings_growth": (FundamentalsService.safe_get(info, "earningsGrowth") or 0) * 100,
                "earnings_quarterly_growth": (FundamentalsService.safe_get(info, "earningsQuarterlyGrowth") or 0) * 100,
                "revenue_quarterly_growth": (FundamentalsService.safe_get(info, "revenueQuarterlyGrowth") or 0) * 100,
                "asset_turnover": FundamentalsService.safe_get(info, "assetTurnover"),
                "inventory_turnover": FundamentalsService.safe_get(info, "inventoryTurnover"),
                "debt_to_equity": FundamentalsService.safe_get(info, "debtToEquity"),
                "current_ratio": FundamentalsService.safe_get(info, "currentRatio"),
                "quick_ratio": FundamentalsService.safe_get(info, "quickRatio"),
                "total_debt": FundamentalsService.safe_get(info, "totalDebt"),
                "total_cash": FundamentalsService.safe_get(info, "totalCash"),
                "beta": FundamentalsService.safe_get(info, "beta"),
                "currency": info.get("currency", "USD"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_financials(ticker: str) -> Dict:
        """Obtiene estados financieros"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            financials = stock.financials
            
            return {
                "ticker": ticker_formatted,
                "financials": financials.to_dict() if financials is not None and not financials.empty else {},
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_balance_sheet(ticker: str) -> Dict:
        """Obtiene balance general"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            balance_sheet = stock.balance_sheet
            
            return {
                "ticker": ticker_formatted,
                "balance_sheet": balance_sheet.to_dict() if balance_sheet is not None and not balance_sheet.empty else {},
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_cashflow(ticker: str) -> Dict:
        """Obtiene flujo de efectivo"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            cashflow = stock.cashflow
            
            return {
                "ticker": ticker_formatted,
                "cashflow": cashflow.to_dict() if cashflow is not None and not cashflow.empty else {},
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_earnings(ticker: str) -> Dict:
        """Obtiene datos de ganancias"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            earnings = stock.earnings
            earnings_dates = stock.earnings_dates
            
            return {
                "ticker": ticker_formatted,
                "earnings": earnings.to_dict() if earnings is not None and not earnings.empty else {},
                "earnings_dates": earnings_dates.to_dict() if earnings_dates is not None and not earnings_dates.empty else None,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

