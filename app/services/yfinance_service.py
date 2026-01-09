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
            
            # Función auxiliar para obtener valores seguros
            def safe_get(key, default=0):
                value = info.get(key)
                return value if value is not None else default
            
            # Extraer métricas de dividendos básicas
            dividend_yield_raw = safe_get("dividendYield", 0)
            dividend_yield = f"{dividend_yield_raw}%" if dividend_yield_raw else "0%"
            
            # Métricas de salud financiera del dividendo
            data = {
                "ticker": ticker,
                # Métricas básicas de dividendos
                "dividend_yield": dividend_yield,
                "payout_ratio": (safe_get("payoutRatio", 0) or 0) * 100,
                "dividend_rate": safe_get("dividendRate", 0),
                "last_dividend_value": safe_get("lastDividendValue", 0),
                "currency": info.get("currency", settings.DEFAULT_CURRENCY),
                
                # Métricas históricas y proyectadas de dividendos
                "trailing_annual_dividend_rate": safe_get("trailingAnnualDividendRate", 0),
                "trailing_annual_dividend_yield": safe_get("trailingAnnualDividendYield", 0),
                "five_year_avg_dividend_yield": safe_get("fiveYearAvgDividendYield", 0),
                "forward_dividend_yield": safe_get("forwardDividendYield", 0),
                "forward_dividend_rate": safe_get("forwardDividendRate", 0),
                
                # Métricas de salud financiera (capacidad de pagar dividendos)
                "free_cashflow": safe_get("freeCashflow", 0),
                "operating_cashflow": safe_get("operatingCashflow", 0),
                "current_ratio": safe_get("currentRatio", 0),
                "debt_to_equity": safe_get("debtToEquity", 0),
                "return_on_equity": safe_get("returnOnEquity", 0),
                "profit_margins": (safe_get("profitMargins", 0) or 0) * 100,
                "earnings_growth": (safe_get("earningsGrowth", 0) or 0) * 100,
                
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
                    "dividend_yield": "0%",
                    "payout_ratio": 0,
                    "dividend_rate": 0,
                    "last_dividend_value": 0,
                    "currency": "N/A",
                    "trailing_annual_dividend_rate": 0,
                    "trailing_annual_dividend_yield": 0,
                    "five_year_avg_dividend_yield": 0,
                    "forward_dividend_yield": 0,
                    "forward_dividend_rate": 0,
                    "free_cashflow": 0,
                    "operating_cashflow": 0,
                    "current_ratio": 0,
                    "debt_to_equity": 0,
                    "return_on_equity": 0,
                    "profit_margins": 0,
                    "earnings_growth": 0,
                    "status": "error",
                    "error": dividend_info["error"]
                })
            else:
                results.append(dividend_info)
        
        return results

