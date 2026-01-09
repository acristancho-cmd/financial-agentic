"""
Servicio para acciones corporativas
"""
import yfinance as yf
from typing import Dict, List
from app.utils.ticker_formatter import format_ticker


class CorporateActionsService:
    """Servicio para acciones corporativas"""
    
    @staticmethod
    def get_dividends_history(ticker: str) -> Dict:
        """Obtiene historial de dividendos"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            dividends = stock.dividends
            
            dividends_list = []
            total_dividends = 0.0
            
            if dividends is not None and not dividends.empty:
                for date, value in dividends.items():
                    dividends_list.append({
                        "date": str(date),
                        "dividend": float(value)
                    })
                    total_dividends += float(value)
            
            average_dividend = total_dividends / len(dividends_list) if dividends_list else None
            
            return {
                "ticker": ticker_formatted,
                "dividends": dividends_list,
                "total_dividends": float(total_dividends) if total_dividends > 0 else None,
                "average_dividend": float(average_dividend) if average_dividend else None,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_splits(ticker: str) -> Dict:
        """Obtiene historial de splits"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            splits = stock.splits
            
            splits_list = []
            
            if splits is not None and not splits.empty:
                for date, value in splits.items():
                    splits_list.append({
                        "date": str(date),
                        "split": str(value)
                    })
            
            return {
                "ticker": ticker_formatted,
                "splits": splits_list,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

