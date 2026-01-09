"""
Servicio para análisis comparativo y correlación
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List
from app.utils.ticker_formatter import format_ticker, parse_ticker_list
from app.services.fundamentals_service import FundamentalsService
from app.utils.yfinance_client import YFinanceClient


class ComparativeService:
    """Servicio para análisis comparativo"""
    
    @staticmethod
    def compare_tickers(tickers: List[str]) -> Dict:
        """Compara múltiples tickers"""
        try:
            tickers_formatted = [format_ticker(t) for t in tickers]
            comparison = {}
            
            for ticker in tickers_formatted:
                fundamentals = FundamentalsService.get_fundamentals(ticker)
                if fundamentals.get("status") == "success":
                    comparison[ticker] = {
                        "market_cap": fundamentals.get("market_cap"),
                        "pe_ratio": fundamentals.get("pe_ratio"),
                        "price_to_book": fundamentals.get("price_to_book"),
                        "return_on_equity": fundamentals.get("return_on_equity"),
                        "profit_margins": fundamentals.get("profit_margins"),
                        "revenue_growth": fundamentals.get("revenue_growth"),
                        "debt_to_equity": fundamentals.get("debt_to_equity"),
                        "current_ratio": fundamentals.get("current_ratio"),
                        "beta": fundamentals.get("beta")
                    }
                else:
                    comparison[ticker] = {"error": fundamentals.get("error")}
            
            return {
                "tickers": tickers_formatted,
                "comparison": comparison,
                "status": "success"
            }
        except Exception as e:
            return {"tickers": tickers, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_correlation(ticker: str, compare_tickers: List[str], period: str = "1y") -> Dict:
        """Calcula correlación entre tickers"""
        try:
            ticker_formatted = format_ticker(ticker)
            compare_formatted = [format_ticker(t) for t in compare_tickers]
            
            # Obtener datos históricos del ticker principal
            stock_main = YFinanceClient.get_ticker(ticker_formatted)
            hist_main = stock_main.history(period=period)
            
            if hist_main.empty:
                return {"ticker": ticker_formatted, "error": "Datos insuficientes para ticker principal", "status": "error"}
            
            returns_main = hist_main['Close'].pct_change().dropna()
            correlations = {}
            
            # Calcular correlación con cada ticker de comparación
            for compare_ticker in compare_formatted:
                try:
                    stock_compare = YFinanceClient.get_ticker(compare_ticker)
                    hist_compare = stock_compare.history(period=period)
                    
                    if not hist_compare.empty:
                        returns_compare = hist_compare['Close'].pct_change().dropna()
                        
                        # Alinear índices
                        common_index = returns_main.index.intersection(returns_compare.index)
                        if len(common_index) > 1:
                            corr = returns_main.loc[common_index].corr(returns_compare.loc[common_index])
                            correlations[compare_ticker] = float(corr) if not np.isnan(corr) else None
                        else:
                            correlations[compare_ticker] = None
                    else:
                        correlations[compare_ticker] = None
                except:
                    correlations[compare_ticker] = None
            
            return {
                "ticker": ticker_formatted,
                "correlations": correlations,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

