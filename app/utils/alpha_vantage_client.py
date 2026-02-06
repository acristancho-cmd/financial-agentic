"""
Cliente para Alpha Vantage como fallback cuando Yahoo Finance falla
"""
import requests
import time
from typing import Dict, Optional
from app.config import settings


class AlphaVantageClient:
    """Cliente para Alpha Vantage API"""
    
    # API Key pública de demo (limitada, pero funciona para MVP)
    # En producción deberías usar tu propia API key gratuita de https://www.alphavantage.co/support/#api-key
    DEFAULT_API_KEY = "demo"
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    @classmethod
    def get_overview(cls, symbol: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene overview/fundamentals de una acción
        
        Args:
            symbol: Símbolo del ticker (sin sufijo .CL)
            api_key: API key de Alpha Vantage (usa demo si no se proporciona)
        
        Returns:
            Diccionario con datos o None si falla
        """
        if api_key is None:
            api_key = cls.DEFAULT_API_KEY
        
        # Remover sufijo .CL si existe para Alpha Vantage
        clean_symbol = symbol.replace(".CL", "").replace(".CL", "")
        
        params = {
            "function": "OVERVIEW",
            "symbol": clean_symbol,
            "apikey": api_key
        }
        
        try:
            response = requests.get(cls.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Alpha Vantage retorna error en el JSON si falla
            if "Error Message" in data or "Note" in data:
                return None
            
            return data
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
            return None
    
    @classmethod
    def get_quote(cls, symbol: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene quote en tiempo real
        
        Args:
            symbol: Símbolo del ticker
            api_key: API key de Alpha Vantage
        
        Returns:
            Diccionario con datos o None si falla
        """
        if api_key is None:
            api_key = cls.DEFAULT_API_KEY
        
        clean_symbol = symbol.replace(".CL", "")
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": clean_symbol,
            "apikey": api_key
        }
        
        try:
            response = requests.get(cls.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                return None
            
            return data.get("Global Quote", {})
        except Exception as e:
            print(f"Alpha Vantage quote error: {e}")
            return None

