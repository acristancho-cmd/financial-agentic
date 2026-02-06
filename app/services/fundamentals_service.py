"""
Servicio para análisis fundamental
"""
import yfinance as yf
import time
import random
from typing import Dict, Optional
from app.utils.ticker_formatter import format_ticker
from app.utils.yfinance_client import YFinanceClient
from app.utils.cache import cache
from app.utils.alpha_vantage_client import AlphaVantageClient
from app.utils.alpha_vantage_client import AlphaVantageClient


class FundamentalsService:
    """Servicio para análisis fundamental"""
    
    @staticmethod
    def safe_get(info: dict, key: str, default=None):
        """Obtiene valor de forma segura"""
        value = info.get(key)
        return value if value is not None else default
    
    @staticmethod
    def _convert_alpha_vantage_to_fundamentals(av_data: Dict, ticker_formatted: str) -> Dict:
        """Convierte datos de Alpha Vantage al formato de fundamentals"""
        def safe_float(value, default=None):
            try:
                if value and value != "None" and value != "N/A" and str(value).strip():
                    return float(value)
            except:
                pass
            return default
        
        def safe_percent(value, default=None):
            try:
                if value and value != "None" and value != "N/A" and str(value).strip():
                    # Alpha Vantage puede venir como "15.5%" o "15.5"
                    val_str = str(value).replace("%", "").strip()
                    if val_str:
                        return float(val_str)
            except:
                pass
            return default
        
        return {
            "ticker": ticker_formatted,
            "market_cap": safe_float(av_data.get("MarketCapitalization")),
            "enterprise_value": safe_float(av_data.get("EnterpriseValue")),
            "pe_ratio": safe_float(av_data.get("PERatio")),
            "forward_pe": safe_float(av_data.get("ForwardPE")),
            "peg_ratio": safe_float(av_data.get("PEGRatio")),
            "price_to_book": safe_float(av_data.get("PriceToBookRatio")),
            "price_to_sales": safe_float(av_data.get("PriceToSalesRatioTTM")),
            "ev_to_revenue": safe_float(av_data.get("EnterpriseValueToRevenue")),
            "ev_to_ebitda": safe_float(av_data.get("EnterpriseValueToEBITDA")),
            "return_on_equity": safe_percent(av_data.get("ReturnOnEquityTTM")),
            "return_on_assets": safe_percent(av_data.get("ReturnOnAssetsTTM")),
            "return_on_invested_capital": safe_percent(av_data.get("ReturnOnInvestedCapital")),
            "profit_margins": safe_percent(av_data.get("ProfitMargin")),
            "operating_margins": safe_percent(av_data.get("OperatingMarginTTM")),
            "gross_margins": safe_percent(av_data.get("GrossProfitTTM")),
            "revenue_growth": safe_percent(av_data.get("QuarterlyRevenueGrowthYOY")),
            "earnings_growth": safe_percent(av_data.get("QuarterlyEarningsGrowthYOY")),
            "earnings_quarterly_growth": safe_percent(av_data.get("QuarterlyEarningsGrowthYOY")),
            "revenue_quarterly_growth": safe_percent(av_data.get("QuarterlyRevenueGrowthYOY")),
            "asset_turnover": safe_float(av_data.get("AssetTurnover")),
            "inventory_turnover": safe_float(av_data.get("InventoryTurnover")),
            "debt_to_equity": safe_float(av_data.get("DebtToEquity")),
            "current_ratio": safe_float(av_data.get("CurrentRatio")),
            "quick_ratio": safe_float(av_data.get("QuickRatio")),
            "total_debt": safe_float(av_data.get("TotalDebt")),
            "total_cash": safe_float(av_data.get("TotalCash")),
            "beta": safe_float(av_data.get("Beta")),
            "currency": av_data.get("Currency", "USD"),
            "sector": av_data.get("Sector"),
            "industry": av_data.get("Industry"),
            "status": "success"
        }
    
    @staticmethod
    def get_fundamentals(ticker: str) -> Dict:
        """Obtiene análisis fundamental completo con fallback a Alpha Vantage"""
        ticker_formatted = format_ticker(ticker)
        cache_key = f"fundamentals:{ticker_formatted}"
        
        # Intentar obtener del caché primero
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # PRIMERO: Intentar con Alpha Vantage (más confiable, API oficial)
        try:
            av_data = AlphaVantageClient.get_overview(ticker_formatted)
            if av_data and av_data.get("Symbol"):
                result = FundamentalsService._convert_alpha_vantage_to_fundamentals(av_data, ticker_formatted)
                cache.set(cache_key, result, ttl=300)
                return result
        except Exception as e:
            print(f"Alpha Vantage falló: {e}")
        
        # SEGUNDO: Si Alpha Vantage falla, intentar con Yahoo Finance (fallback)
        max_retries = 1  # Solo 1 intento ya que Alpha Vantage es el principal
        delay = 5.0
        
        for attempt in range(max_retries):
            try:
                # Delay antes de hacer la petición (más tiempo en producción)
                if attempt > 0:
                    # Backoff exponencial más largo: 10s, 20s
                    wait_time = delay * (2 ** attempt) + random.uniform(2.0, 5.0)
                    time.sleep(wait_time)
                else:
                    # Delay inicial más largo para evitar bloqueos inmediatos
                    time.sleep(3.0 + random.uniform(1.0, 2.0))
                
                # Usar cliente mejorado con manejo de rate limiting
                stock = YFinanceClient.get_ticker(ticker_formatted)
                
                # Delay adicional antes de hacer la petición real
                time.sleep(1.0 + random.uniform(0.5, 1.5))
                
                # Hacer la petición real (solo UNA vez)
                info = stock.info
                
                # Si llegamos aquí, fue exitoso - registrar éxito en circuit breaker
                from app.utils.circuit_breaker import circuit_breaker
                circuit_breaker.record_success()
                
                result = {
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
                
                # Guardar en caché (5 minutos)
                cache.set(cache_key, result, ttl=300)
                return result
            except Exception as e:
                error_str = str(e)
                
                # Registrar fallo en circuit breaker
                from app.utils.circuit_breaker import circuit_breaker
                circuit_breaker.record_failure()
                
                if "429" in error_str or "Too Many Requests" in error_str or "Rate limit" in error_str:
                    if attempt < max_retries - 1:
                        # Esperar mucho más tiempo para errores 429 (15-30 segundos)
                        wait_time = 15.0 + (attempt * 10.0) + random.uniform(3.0, 7.0)
                        time.sleep(wait_time)
                        continue
                    else:
                        wait_time = circuit_breaker.get_wait_time()
                        error_msg = f"Yahoo Finance está bloqueando temporalmente esta IP. "
                        if wait_time > 0:
                            error_msg += f"Espera {int(wait_time)} segundos antes de intentar de nuevo."
                        else:
                            error_msg += "Por favor espera 3-5 minutos antes de intentar de nuevo."
                        return {"ticker": ticker_formatted if 'ticker_formatted' in locals() else ticker, "error": error_msg, "status": "error"}
                elif "Circuit breaker" in error_str:
                    # El circuit breaker está abierto
                    return {"ticker": ticker_formatted if 'ticker_formatted' in locals() else ticker, "error": error_str, "status": "error"}
                else:
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt) + random.uniform(2.0, 4.0)
                        time.sleep(wait_time)
                        continue
                    else:
                        return {"ticker": ticker_formatted if 'ticker_formatted' in locals() else ticker, "error": str(e), "status": "error"}
        
        return {"ticker": ticker, "error": "No se pudo obtener datos después de múltiples intentos", "status": "error"}
    
    @staticmethod
    def get_financials(ticker: str) -> Dict:
        """Obtiene estados financieros"""
        ticker_formatted = format_ticker(ticker)
        cache_key = f"financials:{ticker_formatted}"
        
        # Intentar obtener del caché
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            stock = YFinanceClient.get_ticker(ticker_formatted)
            financials = stock.financials
            
            result = {
                "ticker": ticker_formatted,
                "financials": financials.to_dict() if financials is not None and not financials.empty else {},
                "status": "success"
            }
            
            # Guardar en caché (15 minutos - datos históricos cambian menos)
            cache.set(cache_key, result, ttl=900)
            return result
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_balance_sheet(ticker: str) -> Dict:
        """Obtiene balance general"""
        ticker_formatted = format_ticker(ticker)
        cache_key = f"balance_sheet:{ticker_formatted}"
        
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            stock = YFinanceClient.get_ticker(ticker_formatted)
            balance_sheet = stock.balance_sheet
            
            result = {
                "ticker": ticker_formatted,
                "balance_sheet": balance_sheet.to_dict() if balance_sheet is not None and not balance_sheet.empty else {},
                "status": "success"
            }
            
            cache.set(cache_key, result, ttl=900)  # 15 minutos
            return result
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_cashflow(ticker: str) -> Dict:
        """Obtiene flujo de efectivo"""
        ticker_formatted = format_ticker(ticker)
        cache_key = f"cashflow:{ticker_formatted}"
        
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            stock = YFinanceClient.get_ticker(ticker_formatted)
            cashflow = stock.cashflow
            
            result = {
                "ticker": ticker_formatted,
                "cashflow": cashflow.to_dict() if cashflow is not None and not cashflow.empty else {},
                "status": "success"
            }
            
            cache.set(cache_key, result, ttl=900)  # 15 minutos
            return result
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_earnings(ticker: str) -> Dict:
        """Obtiene datos de ganancias"""
        ticker_formatted = format_ticker(ticker)
        cache_key = f"earnings:{ticker_formatted}"
        
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            stock = YFinanceClient.get_ticker(ticker_formatted)
            earnings = stock.earnings
            earnings_dates = stock.earnings_dates
            
            result = {
                "ticker": ticker_formatted,
                "earnings": earnings.to_dict() if earnings is not None and not earnings.empty else {},
                "earnings_dates": earnings_dates.to_dict() if earnings_dates is not None and not earnings_dates.empty else None,
                "status": "success"
            }
            
            cache.set(cache_key, result, ttl=600)  # 10 minutos
            return result
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

