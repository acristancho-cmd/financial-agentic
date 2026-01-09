"""
Endpoint para consultas de dividendos
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.services.yfinance_service import YFinanceService
from app.utils.ticker_formatter import parse_ticker_list
from app.models.dividend import DividendResponse

router = APIRouter(prefix="/dividends", tags=["dividends"])


@router.get(
    "",
    response_model=List[DividendResponse],
    summary="Consulta información de dividendos",
    description="""
    Consulta información de dividendos para uno o múltiples tickers.
    
    Puedes usar:
    - `ticker`: Para consultar un solo ticker (ej: ?ticker=AAPL)
    - `tickers`: Para consultar múltiples tickers separados por comas (ej: ?tickers=AAPL,TSLA,ECOPETROL)
    - También puedes combinar ambos parámetros
    
    Si no se proporciona ningún parámetro, retorna error 400.
    """,
    responses={
        200: {
            "description": "Lista de información de dividendos",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "ticker": "AAPL",
                            "dividend_yield": 0.5,
                            "payout_ratio": 15.2,
                            "dividend_rate": 0.96,
                            "last_dividend_value": 0.24,
                            "currency": "USD",
                            "status": "success"
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Error de validación - No se proporcionaron tickers"
        }
    }
)
async def get_dividends(
    ticker: Optional[str] = Query(None, description="Un solo ticker a consultar"),
    tickers: Optional[str] = Query(None, description="Múltiples tickers separados por comas (ej: AAPL,TSLA,ECOPETROL)")
):
    """
    Consulta información de dividendos para uno o múltiples tickers.
    """
    # Validar que se proporcione al menos un ticker
    if not ticker and not tickers:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un ticker usando 'ticker' o 'tickers'"
        )
    
    # Parsear y combinar tickers
    ticker_list = parse_ticker_list(ticker=ticker, tickers=tickers)
    
    if not ticker_list:
        raise HTTPException(
            status_code=400,
            detail="No se proporcionaron tickers válidos"
        )
    
    # Obtener información de dividendos
    results = YFinanceService.get_multiple_dividends(ticker_list)
    
    return results


