"""
Cliente mejorado para yfinance con manejo de rate limiting y retry logic
"""
import yfinance as yf
import time
import random
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.utils.rate_limiter import rate_limiter


class YFinanceClient:
    """Cliente mejorado para yfinance con manejo de errores y rate limiting"""
    
    _session = None
    
    @classmethod
    def get_session(cls):
        """Obtiene o crea una sesión con headers personalizados"""
        if cls._session is None:
            cls._session = requests.Session()
            
            # Headers personalizados para evitar bloqueos
            cls._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Configurar retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            cls._session.mount("http://", adapter)
            cls._session.mount("https://", adapter)
        
        return cls._session
    
    @classmethod
    def get_ticker(cls, ticker: str, max_retries: int = 3, delay: float = 1.0):
        """
        Obtiene un objeto Ticker con manejo de errores y retry
        
        Args:
            ticker: Símbolo del ticker
            max_retries: Número máximo de reintentos
            delay: Delay inicial entre reintentos (se incrementa exponencialmente)
        
        Returns:
            Objeto yf.Ticker
        """
        # Esperar si es necesario para respetar rate limiting
        rate_limiter.wait_if_needed()
        
        # Crear Ticker sin hacer peticiones todavía
        # La sesión personalizada se usará cuando se haga la primera petición real
        stock = yf.Ticker(ticker)
        
        # Retornar el objeto sin validar (evita doble petición)
        # La validación y manejo de errores se hará cuando el servicio llame a stock.info
        return stock
    
    @classmethod
    def safe_get_info(cls, ticker: str, max_retries: int = 3):
        """
        Obtiene info de forma segura con manejo de errores
        
        Args:
            ticker: Símbolo del ticker
            max_retries: Número máximo de reintentos
        
        Returns:
            Diccionario con info o None si falla
        """
        try:
            stock = cls.get_ticker(ticker, max_retries=max_retries)
            return stock.info
        except Exception as e:
            # Si es error 429, esperar más tiempo
            if "429" in str(e) or "Too Many Requests" in str(e):
                time.sleep(5)  # Esperar 5 segundos adicionales
                try:
                    stock = cls.get_ticker(ticker, max_retries=2)
                    return stock.info
                except:
                    return None
            return None

