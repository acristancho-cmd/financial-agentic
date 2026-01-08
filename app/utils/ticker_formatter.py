"""
Utilidades para formatear y validar tickers
"""
from typing import List
from app.config import settings


def format_ticker(ticker_raw: str, country_suffix: str = None) -> str:
    """
    Formatea el ticker agregando sufijo de país si es necesario.
    
    Args:
        ticker_raw: Ticker sin formatear
        country_suffix: Sufijo del país a agregar (por defecto usa settings.DEFAULT_COUNTRY_SUFFIX)
    
    Returns:
        Ticker formateado con sufijo si es necesario
    
    Examples:
        >>> format_ticker("ECOPETROL")
        'ECOPETROL.CL'
        >>> format_ticker("AAPL")
        'AAPL'
        >>> format_ticker("TSLA.US")
        'TSLA.US'
    """
    if country_suffix is None:
        country_suffix = settings.DEFAULT_COUNTRY_SUFFIX
    
    ticker_upper = ticker_raw.upper().strip()
    
    # Si ya tiene un punto (sufijo) o es muy largo, no modificar
    if "." in ticker_upper or len(ticker_upper) > settings.MAX_TICKER_LENGTH_WITHOUT_SUFFIX:
        return ticker_upper
    
    # Agregar sufijo del país
    return f"{ticker_upper}{country_suffix}"


def parse_ticker_list(ticker: str = None, tickers: str = None) -> List[str]:
    """
    Parsea y combina tickers de diferentes parámetros en una lista única.
    
    Args:
        ticker: Un solo ticker
        tickers: Múltiples tickers separados por comas
    
    Returns:
        Lista de tickers sin formatear
    
    Examples:
        >>> parse_ticker_list(ticker="AAPL")
        ['AAPL']
        >>> parse_ticker_list(tickers="AAPL,TSLA,ECOPETROL")
        ['AAPL', 'TSLA', 'ECOPETROL']
        >>> parse_ticker_list(ticker="AAPL", tickers="TSLA,ECOPETROL")
        ['AAPL', 'TSLA', 'ECOPETROL']
    """
    ticker_list = []
    
    if ticker:
        ticker_list.append(ticker.strip())
    
    if tickers:
        # Separar por comas y limpiar espacios
        ticker_list.extend([t.strip() for t in tickers.split(",") if t.strip()])
    
    # Eliminar duplicados manteniendo el orden
    seen = set()
    unique_tickers = []
    for t in ticker_list:
        if t and t not in seen:
            seen.add(t)
            unique_tickers.append(t)
    
    return unique_tickers

