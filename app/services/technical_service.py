"""
Servicio para análisis técnico
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.utils.ticker_formatter import format_ticker


class TechnicalService:
    """Servicio para análisis técnico"""
    
    @staticmethod
    def get_history(ticker: str, period: str = "1y", interval: str = "1d") -> Dict:
        """Obtiene datos históricos"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                return {"ticker": ticker_formatted, "history": [], "status": "success"}
            
            # Convertir a lista de diccionarios
            hist_dict = hist.reset_index().to_dict('records')
            # Convertir Timestamp a string
            for record in hist_dict:
                if 'Date' in record:
                    record['Date'] = str(record['Date'])
            
            return {
                "ticker": ticker_formatted,
                "history": hist_dict,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calcula MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd.iloc[-1] if not macd.empty else None, signal_line.iloc[-1] if not signal_line.empty else None, histogram.iloc[-1] if not histogram.empty else None
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Calcula Bandas de Bollinger"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper.iloc[-1] if not upper.empty else None, sma.iloc[-1] if not sma.empty else None, lower.iloc[-1] if not lower.empty else None
    
    @staticmethod
    def get_technical_indicators(ticker: str, period: str = "6mo") -> Dict:
        """Obtiene indicadores técnicos"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            hist = stock.history(period=period)
            
            if hist.empty or len(hist) < 50:
                return {"ticker": ticker_formatted, "error": "Datos insuficientes", "status": "error"}
            
            close = hist['Close']
            
            # Calcular indicadores
            rsi = TechnicalService.calculate_rsi(close)
            macd, macd_signal, macd_hist = TechnicalService.calculate_macd(close)
            bb_upper, bb_middle, bb_lower = TechnicalService.calculate_bollinger_bands(close)
            
            # Medias móviles
            sma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
            sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
            sma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
            ema_12 = close.ewm(span=12).mean().iloc[-1] if len(close) >= 12 else None
            ema_26 = close.ewm(span=26).mean().iloc[-1] if len(close) >= 26 else None
            
            # ADX simplificado
            high = hist['High']
            low = hist['Low']
            plus_dm = high.diff()
            minus_dm = -low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(14).mean().iloc[-1] if len(dx) >= 14 else None
            
            # Estocástico
            low_14 = low.rolling(14).min()
            high_14 = high.rolling(14).max()
            k_percent = 100 * ((close - low_14) / (high_14 - low_14))
            d_percent = k_percent.rolling(3).mean()
            stoch_k = k_percent.iloc[-1] if not k_percent.empty else None
            stoch_d = d_percent.iloc[-1] if not d_percent.empty else None
            
            return {
                "ticker": ticker_formatted,
                "rsi": float(rsi) if rsi is not None and not np.isnan(rsi) else None,
                "macd": float(macd) if macd is not None and not np.isnan(macd) else None,
                "macd_signal": float(macd_signal) if macd_signal is not None and not np.isnan(macd_signal) else None,
                "macd_histogram": float(macd_hist) if macd_hist is not None and not np.isnan(macd_hist) else None,
                "bollinger_upper": float(bb_upper) if bb_upper is not None and not np.isnan(bb_upper) else None,
                "bollinger_middle": float(bb_middle) if bb_middle is not None and not np.isnan(bb_middle) else None,
                "bollinger_lower": float(bb_lower) if bb_lower is not None and not np.isnan(bb_lower) else None,
                "sma_20": float(sma_20) if sma_20 is not None and not np.isnan(sma_20) else None,
                "sma_50": float(sma_50) if sma_50 is not None and not np.isnan(sma_50) else None,
                "sma_200": float(sma_200) if sma_200 is not None and not np.isnan(sma_200) else None,
                "ema_12": float(ema_12) if ema_12 is not None and not np.isnan(ema_12) else None,
                "ema_26": float(ema_26) if ema_26 is not None and not np.isnan(ema_26) else None,
                "adx": float(adx) if adx is not None and not np.isnan(adx) else None,
                "stochastic_k": float(stoch_k) if stoch_k is not None and not np.isnan(stoch_k) else None,
                "stochastic_d": float(stoch_d) if stoch_d is not None and not np.isnan(stoch_d) else None,
                "current_price": float(close.iloc[-1]) if not close.empty else None,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_volatility(ticker: str, period: str = "1y") -> Dict:
        """Obtiene análisis de volatilidad"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            hist = stock.history(period=period)
            info = stock.info
            
            if hist.empty:
                return {"ticker": ticker_formatted, "error": "Datos insuficientes", "status": "error"}
            
            close = hist['Close']
            returns = close.pct_change().dropna()
            
            # Volatilidad anualizada
            volatility = returns.std() * np.sqrt(252) * 100
            
            # Beta
            beta = info.get("beta", None)
            
            # Volatilidad diaria
            daily_vol = returns.std() * 100
            
            # Máximo drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Sharpe Ratio (asumiendo risk-free rate de 0)
            sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else None
            
            return {
                "ticker": ticker_formatted,
                "volatility": float(volatility) if not np.isnan(volatility) else None,
                "beta": float(beta) if beta is not None else None,
                "daily_volatility": float(daily_vol) if not np.isnan(daily_vol) else None,
                "max_drawdown": float(max_drawdown) if not np.isnan(max_drawdown) else None,
                "sharpe_ratio": float(sharpe) if sharpe is not None and not np.isnan(sharpe) else None,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_performance(ticker: str, period: str = "1y") -> Dict:
        """Obtiene análisis de rendimiento"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"ticker": ticker_formatted, "error": "Datos insuficientes", "status": "error"}
            
            close = hist['Close']
            returns = close.pct_change().dropna()
            
            # Retornos
            daily_return = returns.iloc[-1] * 100 if len(returns) > 0 else None
            
            # Retorno semanal (últimos 5 días)
            weekly_return = ((close.iloc[-1] / close.iloc[-5]) - 1) * 100 if len(close) >= 5 else None
            
            # Retorno mensual (últimos 20 días)
            monthly_return = ((close.iloc[-1] / close.iloc[-20]) - 1) * 100 if len(close) >= 20 else None
            
            # YTD (año a la fecha)
            ytd_return = ((close.iloc[-1] / close.iloc[0]) - 1) * 100 if len(close) > 0 else None
            
            # Retorno anualizado
            days = len(hist)
            annual_return = ((close.iloc[-1] / close.iloc[0]) ** (252 / days) - 1) * 100 if days > 0 else None
            
            # Máximo drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Sharpe Ratio
            sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else None
            
            # Volatilidad
            volatility = returns.std() * np.sqrt(252) * 100
            
            return {
                "ticker": ticker_formatted,
                "daily_return": float(daily_return) if daily_return is not None and not np.isnan(daily_return) else None,
                "weekly_return": float(weekly_return) if weekly_return is not None and not np.isnan(weekly_return) else None,
                "monthly_return": float(monthly_return) if monthly_return is not None and not np.isnan(monthly_return) else None,
                "ytd_return": float(ytd_return) if ytd_return is not None and not np.isnan(ytd_return) else None,
                "annual_return": float(annual_return) if annual_return is not None and not np.isnan(annual_return) else None,
                "max_drawdown": float(max_drawdown) if not np.isnan(max_drawdown) else None,
                "sharpe_ratio": float(sharpe) if sharpe is not None and not np.isnan(sharpe) else None,
                "volatility": float(volatility) if not np.isnan(volatility) else None,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

