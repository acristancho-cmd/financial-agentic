"""
Servicio para análisis de mercado y sentimiento
"""
import yfinance as yf
from typing import Dict, List
from app.utils.ticker_formatter import format_ticker


class MarketSentimentService:
    """Servicio para análisis de mercado y sentimiento"""
    
    @staticmethod
    def get_recommendations(ticker: str) -> Dict:
        """Obtiene recomendaciones de analistas"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            recommendations = stock.recommendations
            info = stock.info
            
            recs_list = []
            if recommendations is not None and not recommendations.empty:
                recs_list = recommendations.reset_index().to_dict('records')
                for rec in recs_list:
                    if 'Date' in rec:
                        rec['Date'] = str(rec['Date'])
            
            return {
                "ticker": ticker_formatted,
                "recommendations": recs_list,
                "current_rating": info.get("recommendationKey"),
                "target_price": info.get("targetMeanPrice"),
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_news(ticker: str) -> Dict:
        """Obtiene noticias"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            news = stock.news
            
            news_list = []
            if news:
                for item in news:
                    news_list.append({
                        "title": item.get("title", ""),
                        "publisher": item.get("publisher", ""),
                        "link": item.get("link", ""),
                        "providerPublishTime": item.get("providerPublishTime"),
                        "type": item.get("type", "")
                    })
            
            return {
                "ticker": ticker_formatted,
                "news": news_list,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_calendar(ticker: str) -> Dict:
        """Obtiene calendario de eventos"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            calendar = stock.calendar
            
            earnings_dates = None
            if calendar is not None and not calendar.empty:
                earnings_dates = calendar.reset_index().to_dict('records')
                for ed in earnings_dates:
                    if 'Earnings Date' in ed:
                        ed['Earnings Date'] = str(ed['Earnings Date'])
            
            # Obtener acciones corporativas
            actions = stock.actions
            dividend_dates = []
            splits = []
            
            if actions is not None and not actions.empty:
                for idx, row in actions.iterrows():
                    if row.get('Dividends', 0) > 0:
                        dividend_dates.append({
                            "date": str(idx),
                            "dividend": float(row['Dividends'])
                        })
                    if row.get('Stock Splits', 0) > 0:
                        splits.append({
                            "date": str(idx),
                            "split": str(row['Stock Splits'])
                        })
            
            return {
                "ticker": ticker_formatted,
                "earnings_dates": earnings_dates,
                "dividend_dates": dividend_dates,
                "splits": splits,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}
    
    @staticmethod
    def get_holders(ticker: str) -> Dict:
        """Obtiene información de accionistas"""
        try:
            ticker_formatted = format_ticker(ticker)
            stock = yf.Ticker(ticker_formatted)
            major_holders = stock.major_holders
            institutional_holders = stock.institutional_holders
            
            major_list = []
            if major_holders is not None and not major_holders.empty:
                major_list = major_holders.to_dict('records')
            
            inst_list = []
            if institutional_holders is not None and not institutional_holders.empty:
                inst_list = institutional_holders.reset_index().to_dict('records')
            
            return {
                "ticker": ticker_formatted,
                "major_holders": major_list,
                "institutional_holders": inst_list,
                "status": "success"
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "status": "error"}

