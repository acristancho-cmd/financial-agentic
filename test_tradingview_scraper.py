"""
Script de prueba para tradingview-scraper
Prueba todas las funcionalidades disponibles del scraper
"""
# pip install tradingview-scraper pandas
import pandas as pd
from tradingview_scraper.symbols.fundamental_graphs import FundamentalGraphs
from tradingview_scraper.symbols.news import NewsScraper
from tradingview_scraper.symbols.technicals import Indicators
from tradingview_scraper.symbols.ideas import Ideas
from tradingview_scraper.symbols.stream import RealTimeData


def scrape_all_tradingview(symbol="BVC:ECOPETROL"):
    """
    Extrae todos los datos disponibles de TradingView para un símbolo
    
    Args:
        symbol: Símbolo en formato TradingView (ej: "BVC:ECOPETROL", "BVC:CIBCCOLOM")
    
    Returns:
        dict: Diccionario con todos los datos extraídos
    """
    results = {}
    
    print(f"\n🔍 Iniciando scraping para: {symbol}\n")
    
    try:
        # 1. RESUMEN FINANCIERO + FUNDAMENTALS
        print("📊 Extrayendo fundamentals...")
        fundamentals_scraper = FundamentalGraphs()
        fundamentals_result = fundamentals_scraper.get_fundamentals(symbol=symbol)
        if fundamentals_result.get('status') == 'success':
            results['fundamentals'] = fundamentals_result.get('data', {})
            print(f"✅ Fundamentals obtenidos: {len(results['fundamentals']) if isinstance(results['fundamentals'], dict) else 'N/A'} campos")
        else:
            results['fundamentals'] = None
            print(f"⚠️  Fundamentals: {fundamentals_result.get('error', 'Error desconocido')}")
        
    except Exception as e:
        print(f"❌ Error en fundamentals: {e}")
        results['fundamentals'] = None
    
    try:
        # 2. NOTICIAS (headlines + content)
        print("📰 Extrayendo noticias...")
        # Extraer exchange del símbolo (ej: "NASDAQ:AAPL" -> exchange="NASDAQ", symbol="AAPL")
        if ':' in symbol:
            exchange, symbol_name = symbol.split(':', 1)
        else:
            exchange = "BVC"  # Default para acciones estadounidenses
            symbol_name = symbol
        
        news_scraper = NewsScraper()
        news_result = news_scraper.scrape_headlines(symbol=symbol_name, exchange=exchange, sort='latest')
        
        # Manejar diferentes formatos de respuesta
        if isinstance(news_result, dict):
            if news_result.get('status') == 'success' and news_result.get('data'):
                results['news'] = news_result.get('data', [])
                print(f"✅ Noticias obtenidas: {len(results['news'])} artículos")
            else:
                results['news'] = []
                print("⚠️  No se encontraron noticias")
        elif isinstance(news_result, list):
            # Si retorna directamente una lista
            results['news'] = news_result
            print(f"✅ Noticias obtenidas: {len(results['news'])} artículos")
        else:
            results['news'] = []
            print("⚠️  Formato de respuesta de noticias desconocido")
            
    except Exception as e:
        print(f"❌ Error en noticias: {e}")
        import traceback
        traceback.print_exc()
        results['news'] = None
    
    try:
        # 3. DATOS TÉCNICOS (TODOS indicators)
        print("📈 Extrayendo indicadores técnicos...")
        indicators_scraper = Indicators(export_result=True, export_type='json')
        indicators_result = indicators_scraper.scrape(
            symbol=symbol, timeframe="1d", allIndicators=True
        )
        
        # Manejar diferentes formatos de respuesta
        if isinstance(indicators_result, dict):
            if indicators_result.get('status') == 'success':
                results['indicators'] = indicators_result.get('data', {})
                print(f"✅ Indicadores obtenidos: {len(results['indicators']) if isinstance(results['indicators'], dict) else 'N/A'} indicadores")
            else:
                results['indicators'] = None
                error_msg = indicators_result.get('error', indicators_result.get('errmsg', 'Error desconocido'))
                print(f"⚠️  Indicadores: {error_msg}")
        elif isinstance(indicators_result, dict) and 'data' in indicators_result:
            # Formato alternativo
            results['indicators'] = indicators_result.get('data', {})
            print(f"✅ Indicadores obtenidos: {len(results['indicators']) if isinstance(results['indicators'], dict) else 'N/A'} indicadores")
        else:
            results['indicators'] = None
            print(f"⚠️  Formato de respuesta de indicadores desconocido: {type(indicators_result)}")
        
    except Exception as e:
        print(f"❌ Error en indicadores: {e}")
        import traceback
        traceback.print_exc()
        results['indicators'] = None
    
    try:
        # 4. COMUNIDAD (ideas recientes)
        print("💡 Extrayendo ideas de la comunidad...")
        ideas_scraper = Ideas()
        ideas_result = ideas_scraper.scrape(symbol=symbol, startPage=1, endPage=1, sort="popular")
        if isinstance(ideas_result, list) and len(ideas_result) > 0:
            results['ideas'] = ideas_result[:5]  # Limitar a 5 ideas
            print(f"✅ Ideas obtenidas: {len(results['ideas'])} ideas")
        else:
            results['ideas'] = []
            print("⚠️  No se encontraron ideas")
        
    except Exception as e:
        print(f"❌ Error en ideas: {e}")
        results['ideas'] = None
    
    try:
        # 5. REAL-TIME OHLCV
        print("⚡ Extrayendo datos en tiempo real...")
        realtime_scraper = RealTimeData()
        # get_ohlcv requiere el símbolo completo con exchange
        realtime_generator = realtime_scraper.get_ohlcv(exchange_symbol=symbol)
        # Obtener el primer paquete del generador
        try:
            first_packet = next(realtime_generator)
            results['realtime'] = first_packet
            print(f"✅ Datos en tiempo real obtenidos")
            # Cerrar el generador para evitar conexiones abiertas
            realtime_generator.close()
        except StopIteration:
            results['realtime'] = None
            print("⚠️  No se obtuvieron datos en tiempo real")
        
    except Exception as e:
        print(f"❌ Error en datos tiempo real: {e}")
        import traceback
        traceback.print_exc()
        results['realtime'] = None
    
    return results


def print_results(results):
    """Imprime los resultados de forma organizada"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE RESULTADOS")
    print("="*60)
    
    # Fundamentals
    if results.get('fundamentals') and results['fundamentals'] is not None:
        print("\n📊 FUNDAMENTALS:")
        print("-" * 60)
        if isinstance(results['fundamentals'], dict) and len(results['fundamentals']) > 0:
            # Mostrar solo algunos campos clave
            key_fields = ['symbol', 'total_revenue', 'net_income', 'market_cap_basic', 
                         'price_earnings_ttm', 'dividends_yield', 'return_on_equity_fq']
            for field in key_fields:
                if field in results['fundamentals']:
                    value = results['fundamentals'][field]
                    print(f"  • {field}: {value}")
        else:
            print("  No hay datos disponibles")
    
    # News
    if results.get('news') is not None:
        news_count = len(results['news']) if isinstance(results['news'], list) else 0
        print(f"\n📰 NOTICIAS ({news_count} artículos):")
        print("-" * 60)
        if isinstance(results['news'], list) and len(results['news']) > 0:
            for i, article in enumerate(results['news'][:3], 1):  # Mostrar solo las primeras 3
                if isinstance(article, dict):
                    title = article.get('title', 'Sin título')
                    print(f"{i}. {title}")
                else:
                    print(f"{i}. {article}")
        else:
            print("  No hay noticias disponibles")
    
    # Indicators
    if results.get('indicators') and results['indicators'] is not None:
        print("\n📈 INDICADORES TÉCNICOS:")
        print("-" * 60)
        if isinstance(results['indicators'], dict) and len(results['indicators']) > 0:
            print(f"Total de indicadores: {len(results['indicators'])}")
            for key, value in list(results['indicators'].items())[:10]:  # Mostrar primeros 10
                print(f"  • {key}: {value}")
        else:
            print("  No hay indicadores disponibles")
    
    # Ideas
    if results.get('ideas') is not None:
        ideas_count = len(results['ideas']) if isinstance(results['ideas'], list) else 0
        print(f"\n💡 IDEAS DE LA COMUNIDAD ({ideas_count} ideas):")
        print("-" * 60)
        if isinstance(results['ideas'], list) and len(results['ideas']) > 0:
            for i, idea in enumerate(results['ideas'][:3], 1):  # Mostrar solo las primeras 3
                if isinstance(idea, dict):
                    title = idea.get('title', 'Sin título')
                    author = idea.get('author', 'Desconocido')
                    print(f"{i}. {title} (por {author})")
                else:
                    print(f"{i}. {idea}")
        else:
            print("  No hay ideas disponibles")
    
    # Realtime
    if results.get('realtime') and results['realtime'] is not None:
        print("\n⚡ DATOS EN TIEMPO REAL:")
        print("-" * 60)
        if isinstance(results['realtime'], dict):
            # Mostrar información relevante del paquete
            msg_type = results['realtime'].get('m', 'N/A')
            print(f"  Tipo de mensaje: {msg_type}")
            if 'p' in results['realtime']:
                params = results['realtime'].get('p', [])
                if isinstance(params, list) and len(params) > 1:
                    data = params[1] if isinstance(params[1], dict) else params[1]
                    if isinstance(data, dict):
                        print(f"  Datos disponibles: Sí")
                        # Mostrar algunos campos si están disponibles
                        if 'sds_1' in data:
                            print(f"  Serie de datos: Disponible")
                    else:
                        print(f"  Datos: {str(data)[:100]}")
        else:
            print(f"  {results['realtime']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Ejemplos de uso
    print("🚀 TESTING TRADINGVIEW SCRAPER")
    print("="*60)
    
    # Prueba 1: Apple (NASDAQ)
    print("\n📌 PRUEBA 1: Apple Inc. (BVC:ECOPETROL)")
    symbol_apple = "BVC:ECOPETROL"
    results_apple = scrape_all_tradingview(symbol_apple)
    print_results(results_apple)
    
    # Prueba 2: Acción colombiana (opcional, descomentar para probar)
    # print("\n📌 PRUEBA 2: Acción colombiana")
    # symbol_colombia = "BVC:CIBCCOLOM"
    # results_colombia = scrape_all_tradingview(symbol_colombia)
    # print_results(results_colombia)
    
    print("\n✅ Pruebas completadas!")
