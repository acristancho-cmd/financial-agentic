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
from app.utils.circuit_breaker import circuit_breaker


class YFinanceClient:
    """Cliente mejorado para yfinance con manejo de errores y rate limiting"""
    
    _session = None
    
    @classmethod
    def get_session(cls):
        """Obtiene o crea una sesión con headers personalizados"""
        if cls._session is None:
            cls._session = requests.Session()
            
            # Headers personalizados más realistas para evitar bloqueos
            cls._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
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
        # Verificar circuit breaker
        if not circuit_breaker.can_proceed():
            wait_time = circuit_breaker.get_wait_time()
            if wait_time > 0:
                raise Exception(f"Circuit breaker abierto. Yahoo Finance está bloqueando. Espera {int(wait_time)} segundos antes de intentar de nuevo.")
        
        # Esperar si es necesario para respetar rate limiting
        rate_limiter.wait_if_needed()
        
        # Delay adicional antes de crear el ticker (más conservador en producción)
        # Delay aleatorio entre 2-4 segundos para parecer más humano
        time.sleep(2.0 + random.uniform(0, 2.0))
        
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

