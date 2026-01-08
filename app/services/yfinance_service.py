"""
Servicio para interactuar con yfinance y obtener datos financieros
"""
import yfinance as yf
from typing import Dict, List
from app.config import settings
from app.utils.ticker_formatter import format_ticker


class YFinanceService:
    """Servicio para consultas a yfinance"""
    
    @staticmethod
    def get_dividend_info(ticker: str) -> Dict:
        """
        Obtiene la información de dividendos de un ticker usando yfinance.
        
        Args:
            ticker: Ticker formateado de la acción
        
        Returns:
            Diccionario con información de dividendos o error
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extraer métricas de dividendos
            data = {
                "ticker": ticker,
                "dividend_yield": (info.get("dividendYield", 0) or 0) * 100,
                "payout_ratio": (info.get("payoutRatio", 0) or 0) * 100,
                "dividend_rate": info.get("dividendRate", 0) or 0,
                "last_dividend_value": info.get("lastDividendValue", 0) or 0,
                "currency": info.get("currency", settings.DEFAULT_CURRENCY),
                "status": "success"
            }
            
            return data
        except Exception as e:
            return {
                "ticker": ticker,
                "error": str(e),
                "status": "error"
            }
    
    @staticmethod
    def get_multiple_dividends(tickers: List[str]) -> List[Dict]:
        """
        Obtiene información de dividendos para múltiples tickers.
        
        Args:
            tickers: Lista de tickers sin formatear
        
        Returns:
            Lista de diccionarios con información de dividendos
        """
        results = []
        
        for ticker_raw in tickers:
            if not ticker_raw:
                continue
            
            # Formatear ticker
            ticker_final = format_ticker(ticker_raw)
            
            # Obtener información
            dividend_info = YFinanceService.get_dividend_info(ticker_final)
            
            # Si hay error, crear respuesta de error con estructura completa
            if "error" in dividend_info:
                results.append({
                    "ticker": ticker_final,
                    "dividend_yield": 0,
                    "payout_ratio": 0,
                    "dividend_rate": 0,
                    "last_dividend_value": 0,
                    "currency": "N/A",
                    "status": "error",
                    "error": dividend_info["error"]
                })
            else:
                results.append(dividend_info)
        
        return results

