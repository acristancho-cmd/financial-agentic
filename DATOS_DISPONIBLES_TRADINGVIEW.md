# 📊 Datos Disponibles de TradingView Scraper

## Índice de Contenidos
1. [Resumen General](#resumen-general)
2. [Información Financiera](#información-financiera)
3. [Estadísticas](#estadísticas)
4. [Noticias](#noticias)
5. [Documentos Financieros](#documentos-financieros)
6. [Comunidad](#comunidad)
7. [Datos Técnicos](#datos-técnicos)
8. [Calendario de Eventos](#calendario-de-eventos)
9. [Datos en Tiempo Real](#datos-en-tiempo-real)
10. [Análisis Comparativo](#análisis-comparativo)

---

## 📋 Resumen General

### Clase: `Overview.get_symbol_overview()`

**Datos Básicos de la Empresa:**
- `name` - Nombre del símbolo
- `description` - Descripción de la empresa
- `type` - Tipo de instrumento (stock, crypto, forex, etc.)
- `exchange` - Bolsa donde cotiza
- `country` - País de origen
- `sector` - Sector económico
- `industry` - Industria específica
- `currency_code` - Código de moneda

**Datos de Precio:**
- `close` - Precio de cierre actual
- `open` - Precio de apertura
- `high` - Precio máximo del día
- `low` - Precio mínimo del día
- `change` - Cambio porcentual del día
- `change_abs` - Cambio absoluto del día
- `volume` - Volumen negociado

**Máximos y Mínimos:**
- `high_52_week` - Máximo de 52 semanas
- `low_52_week` - Mínimo de 52 semanas

**Perfil de la Empresa:**
- `get_profile()` - Información completa del perfil
  - Nombre completo
  - Descripción detallada
  - Exchange
  - Sector e Industria
  - País
  - Tipo de instrumento

---

## 💰 Información Financiera

### Clase: `FundamentalGraphs.get_fundamentals()`

#### **Estado de Resultados (Income Statement):**
- `total_revenue` - Ingresos totales
- `revenue_per_share_ttm` - Ingresos por acción (TTM)
- `total_revenue_fy` - Ingresos totales año fiscal
- `gross_profit` - Ganancia bruta
- `gross_profit_fy` - Ganancia bruta año fiscal
- `operating_income` - Ingresos operativos
- `operating_income_fy` - Ingresos operativos año fiscal
- `net_income` - Ingresos netos
- `net_income_fy` - Ingresos netos año fiscal
- `EBITDA` - EBITDA
- `basic_eps_net_income` - EPS básico de ingresos netos
- `earnings_per_share_basic_ttm` - BPA básico (TTM)
- `earnings_per_share_diluted_ttm` - BPA diluido (TTM)

#### **Balance General (Balance Sheet):**
- `total_assets` - Activos totales
- `total_assets_fy` - Activos totales año fiscal
- `cash_n_short_term_invest` - Efectivo e inversiones a corto plazo
- `cash_n_short_term_invest_fy` - Efectivo e inversiones año fiscal
- `total_debt` - Deuda total
- `total_debt_fy` - Deuda total año fiscal
- `stockholders_equity` - Patrimonio de accionistas
- `stockholders_equity_fy` - Patrimonio año fiscal
- `book_value_per_share_fq` - Valor en libros por acción

#### **Flujo de Efectivo (Cash Flow):**
- `cash_f_operating_activities` - Flujo de efectivo actividades operativas
- `cash_f_operating_activities_fy` - Flujo operativo año fiscal
- `cash_f_investing_activities` - Flujo de efectivo actividades de inversión
- `cash_f_investing_activities_fy` - Flujo de inversión año fiscal
- `cash_f_financing_activities` - Flujo de efectivo actividades de financiamiento
- `cash_f_financing_activities_fy` - Flujo de financiamiento año fiscal
- `free_cash_flow` - Flujo de efectivo libre

#### **Márgenes:**
- `gross_margin` - Margen bruto
- `gross_margin_percent_ttm` - Margen bruto porcentual (TTM)
- `operating_margin` - Margen operativo
- `operating_margin_ttm` - Margen operativo (TTM)
- `pretax_margin_percent_ttm` - Margen antes de impuestos (TTM)
- `net_margin` - Margen neto
- `net_margin_percent_ttm` - Margen neto porcentual (TTM)
- `EBITDA_margin` - Margen EBITDA

#### **Rentabilidad:**
- `return_on_equity` - Retorno sobre patrimonio (ROE)
- `return_on_equity_fq` - ROE trimestral
- `return_on_assets` - Retorno sobre activos (ROA)
- `return_on_assets_fq` - ROA trimestral
- `return_on_investment_ttm` - Retorno sobre inversión (ROI) TTM

#### **Liquidez:**
- `current_ratio` - Ratio corriente
- `current_ratio_fq` - Ratio corriente trimestral
- `quick_ratio` - Ratio rápido
- `quick_ratio_fq` - Ratio rápido trimestral

#### **Apalancamiento:**
- `debt_to_equity` - Deuda/Patrimonio
- `debt_to_equity_fq` - Deuda/Patrimonio trimestral
- `debt_to_assets` - Deuda/Activos

#### **Valoración:**
- `market_cap_basic` - Capitalización de mercado básica
- `market_cap_calc` - Capitalización de mercado calculada
- `market_cap_diluted_calc` - Capitalización diluida calculada
- `enterprise_value_fq` - Valor empresarial trimestral
- `price_earnings_ttm` - Ratio Precio/Beneficio (P/E) TTM
- `price_book_fq` - Ratio Precio/Valor en libros (P/B)
- `price_sales_ttm` - Ratio Precio/Ventas (P/S) TTM
- `price_free_cash_flow_ttm` - Ratio Precio/FCF TTM

#### **Dividendos:**
- `dividends_yield` - Rendimiento del dividendo
- `dividends_per_share_fq` - Dividendos por acción trimestral
- `dividend_payout_ratio_ttm` - Ratio de pago de dividendos TTM

#### **Métodos Específicos Disponibles:**
- `get_income_statement()` - Estado de resultados completo
- `get_balance_sheet()` - Balance general completo
- `get_cash_flow()` - Flujo de efectivo completo
- `get_profitability()` - Métricas de rentabilidad
- `get_margins()` - Márgenes
- `get_liquidity()` - Ratios de liquidez
- `get_leverage()` - Ratios de apalancamiento
- `get_valuation()` - Métricas de valoración
- `get_dividends()` - Información de dividendos

---

## 📊 Estadísticas

### Clase: `Overview.get_statistics()`

**Métricas de Mercado:**
- `market_cap_basic` - Capitalización de mercado básica
- `shares_outstanding` - Acciones en circulación
- `shares_float` - Flotación de acciones
- `shares_diluted` - Acciones diluidas

**Ratios de Valoración:**
- `price_earnings_ttm` - P/E Ratio (TTM)
- `price_book_fq` - P/B Ratio
- `price_sales_ttm` - P/S Ratio
- `price_free_cash_flow_ttm` - P/FCF Ratio
- `enterprise_value_fq` - Valor empresarial

**Métricas de Rentabilidad:**
- `earnings_per_share_basic_ttm` - BPA básico (TTM)
- `earnings_per_share_diluted_ttm` - BPA diluido (TTM)
- `return_on_equity_fq` - ROE
- `return_on_assets_fq` - ROA
- `return_on_investment_ttm` - ROI

**Dividendos:**
- `dividends_yield` - Rendimiento del dividendo
- `dividends_per_share_fq` - Dividendos por acción
- `dividend_payout_ratio_ttm` - Ratio de pago

**Riesgo:**
- `beta_1_year` - Beta (1 año)
- `volatility_daily` - Volatilidad diaria
- `volatility_weekly` - Volatilidad semanal
- `volatility_monthly` - Volatilidad mensual

---

## 📰 Noticias

### Clase: `NewsScraper.scrape_headlines()`

**Datos de Cada Noticia:**
- `id` - ID único de la noticia
- `title` - Título de la noticia
- `provider` - Proveedor de noticias (reuters, bloomberg, etc.)
- `source` - Fuente de la noticia
- `sourceLogoId` - ID del logo de la fuente
- `published` - Timestamp de publicación
- `urgency` - Nivel de urgencia
- `permission` - Permisos de acceso
- `relatedSymbols` - Símbolos relacionados
  - `symbol` - Símbolo relacionado
  - `currency-logoid` - ID del logo de moneda
  - `base-currency-logoid` - ID del logo de moneda base
- `storyPath` - Ruta de la historia completa

**Filtros Disponibles:**
- `symbol` - Filtrar por símbolo específico
- `exchange` - Filtrar por exchange
- `provider` - Filtrar por proveedor (newsbtc, reuters, etc.)
- `area` - Filtrar por área geográfica (world, america, etc.)
- `section` - Filtrar por sección (all, stocks, crypto, etc.)
- `sort` - Ordenar por (latest, popular)

### Clase: `NewsScraper.scrape_news_content()`

**Contenido Completo de la Noticia:**
- `breadcrumbs` - Ruta de navegación
- `title` - Título completo
- `published_datetime` - Fecha y hora de publicación
- `related_symbols` - Símbolos relacionados con detalles
  - `name` - Nombre del símbolo
  - `logo` - URL del logo
- `body` - Cuerpo completo del artículo (HTML/texto)
- `tags` - Etiquetas de la noticia

---

## 📄 Documentos Financieros

### Estado de Resultados Completo
**Método:** `FundamentalGraphs.get_income_statement()`

- Ingresos totales (anual y TTM)
- Costo de bienes vendidos
- Ganancia bruta
- Gastos operativos
- Ingresos operativos
- Ingresos antes de impuestos
- Ingresos netos
- EPS básico y diluido
- Número de acciones (básicas y diluidas)

### Balance General Completo
**Método:** `FundamentalGraphs.get_balance_sheet()`

- Activos totales
- Activos corrientes
- Efectivo e inversiones a corto plazo
- Cuentas por cobrar
- Inventario
- Activos no corrientes
- Propiedad, planta y equipo
- Deuda total
- Deuda corriente
- Deuda a largo plazo
- Pasivos totales
- Patrimonio de accionistas
- Valor en libros por acción

### Flujo de Efectivo Completo
**Método:** `FundamentalGraphs.get_cash_flow()`

- Flujo de efectivo de operaciones
- Flujo de efectivo de inversión
- Flujo de efectivo de financiamiento
- Cambio neto en efectivo
- Efectivo al inicio del período
- Efectivo al final del período
- Flujo de efectivo libre

---

## 👥 Comunidad

### Clase: `Ideas.scrape()`

**Datos de Cada Idea:**
- `title` - Título de la idea
- `description` - Descripción completa
- `preview_image` - Imagen de vista previa (URL)
- `chart_url` - URL del gráfico
- `comments_count` - Número de comentarios
- `views_count` - Número de vistas
- `author` - Autor de la idea
- `likes_count` - Número de likes
- `boosts_count` - Número de boosts
- `timestamp` - Timestamp de publicación
- `is_updated` - Si fue actualizada
- `strategy` - Estrategia de trading

**Parámetros de Búsqueda:**
- `symbol` - Símbolo a buscar
- `startPage` - Página inicial
- `endPage` - Página final
- `sort` - Ordenar por (popular, recent)

### Clase: `Minds.get_minds()`

**Discusiones de la Comunidad:**
- `uid` - ID único de la discusión
- `text` - Texto de la discusión
- `url` - URL de la discusión
- `author` - Información del autor
  - `username` - Nombre de usuario
  - `profile_url` - URL del perfil
  - `is_broker` - Si es broker
- `created` - Fecha de creación
- `symbols` - Símbolos mencionados
- `total_likes` - Total de likes
- `total_comments` - Total de comentarios
- `modified` - Si fue modificada
- `hidden` - Si está oculta

**Opciones de Ordenamiento:**
- `recent` - Más recientes
- `popular` - Más populares
- `trending` - En tendencia

---

## 📈 Datos Técnicos

### Clase: `Indicators.scrape()`

**Indicadores de Momentum:**
- `RSI` - Relative Strength Index
- `RSI[1]` - RSI período anterior
- `Stoch.K` - Estocástico %K
- `Stoch.D` - Estocástico %D
- `Stoch.K[1]` - Estocástico %K período anterior
- `Stoch.D[1]` - Estocástico %D período anterior
- `CCI20` - Commodity Channel Index (20)
- `CCI20[1]` - CCI20 período anterior
- `Mom` - Momentum
- `Mom[1]` - Momentum período anterior
- `MACD.macd` - MACD línea principal
- `MACD.signal` - MACD señal
- `Stoch.RSI.K` - Estocástico RSI %K
- `Rec.Stoch.RSI` - Recomendación Estocástico RSI
- `AO` - Awesome Oscillator
- `AO[1]` - AO período anterior
- `AO[2]` - AO 2 períodos anteriores
- `UO` - Ultimate Oscillator
- `Rec.UO` - Recomendación Ultimate Oscillator

**Indicadores de Tendencia:**
- `ADX` - Average Directional Index
- `ADX+DI` - ADX + DI
- `ADX-DI` - ADX - DI
- `ADX+DI[1]` - ADX + DI período anterior
- `ADX-DI[1]` - ADX - DI período anterior
- `EMA10` - Media móvil exponencial 10 períodos
- `EMA20` - Media móvil exponencial 20 períodos
- `EMA30` - Media móvil exponencial 30 períodos
- `EMA50` - Media móvil exponencial 50 períodos
- `EMA100` - Media móvil exponencial 100 períodos
- `EMA200` - Media móvil exponencial 200 períodos
- `SMA10` - Media móvil simple 10 períodos
- `SMA20` - Media móvil simple 20 períodos
- `SMA30` - Media móvil simple 30 períodos
- `SMA50` - Media móvil simple 50 períodos
- `SMA100` - Media móvil simple 100 períodos
- `SMA200` - Media móvil simple 200 períodos
- `Ichimoku.BLine` - Línea base de Ichimoku
- `Rec.Ichimoku` - Recomendación Ichimoku
- `VWMA` - Volume Weighted Moving Average
- `Rec.VWMA` - Recomendación VWMA
- `HullMA9` - Hull Moving Average 9
- `Rec.HullMA9` - Recomendación HullMA9

**Indicadores de Volatilidad:**
- `BBPower` - Bollinger Bands Power
- `Rec.BBPower` - Recomendación Bollinger Bands Power
- `W.R` - Williams %R
- `Rec.WR` - Recomendación Williams %R

**Puntos Pivote:**
- `Pivot.M.Classic.S3` - Punto pivote clásico S3
- `Pivot.M.Classic.S2` - Punto pivote clásico S2
- `Pivot.M.Classic.S1` - Punto pivote clásico S1
- `Pivot.M.Classic.Middle` - Punto pivote clásico medio
- `Pivot.M.Classic.R1` - Punto pivote clásico R1
- `Pivot.M.Classic.R2` - Punto pivote clásico R2
- `Pivot.M.Classic.R3` - Punto pivote clásico R3
- `Pivot.M.Fibonacci.S3` - Punto pivote Fibonacci S3
- `Pivot.M.Fibonacci.S2` - Punto pivote Fibonacci S2
- `Pivot.M.Fibonacci.S1` - Punto pivote Fibonacci S1
- `Pivot.M.Fibonacci.Middle` - Punto pivote Fibonacci medio
- `Pivot.M.Fibonacci.R1` - Punto pivote Fibonacci R1
- `Pivot.M.Fibonacci.R2` - Punto pivote Fibonacci R2
- `Pivot.M.Fibonacci.R3` - Punto pivote Fibonacci R3
- `Pivot.M.Camarilla.S3` - Punto pivote Camarilla S3
- `Pivot.M.Camarilla.S2` - Punto pivote Camarilla S2
- `Pivot.M.Camarilla.S1` - Punto pivote Camarilla S1
- `Pivot.M.Camarilla.Middle` - Punto pivote Camarilla medio
- `Pivot.M.Camarilla.R1` - Punto pivote Camarilla R1
- `Pivot.M.Camarilla.R2` - Punto pivote Camarilla R2
- `Pivot.M.Camarilla.R3` - Punto pivote Camarilla R3
- `Pivot.M.Woodie.S3` - Punto pivote Woodie S3
- `Pivot.M.Woodie.S2` - Punto pivote Woodie S2
- `Pivot.M.Woodie.S1` - Punto pivote Woodie S1
- `Pivot.M.Woodie.Middle` - Punto pivote Woodie medio
- `Pivot.M.Woodie.R1` - Punto pivote Woodie R1
- `Pivot.M.Woodie.R2` - Punto pivote Woodie R2
- `Pivot.M.Woodie.R3` - Punto pivote Woodie R3
- `Pivot.M.Demark.S1` - Punto pivote DeMark S1
- `Pivot.M.Demark.Middle` - Punto pivote DeMark medio
- `Pivot.M.Demark.R1` - Punto pivote DeMark R1

**Recomendaciones:**
- `Recommend.All` - Recomendación general
- `Recommend.MA` - Recomendación basada en medias móviles
- `Recommend.Other` - Otras recomendaciones

**Parámetros:**
- `timeframe` - Marco temporal (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
- `allIndicators` - Obtener todos los indicadores (True/False)
- `indicators` - Lista específica de indicadores

### Clase: `Overview.get_technicals()`

**Indicadores Técnicos Principales:**
- `RSI` - Relative Strength Index
- `MACD.macd` - MACD línea principal
- `MACD.signal` - MACD señal
- `ADX` - Average Directional Index
- `CCI` - Commodity Channel Index
- `Stoch.K` - Estocástico %K
- `Stoch.D` - Estocástico %D
- `Recommend.All` - Recomendación general
- `Volatility.D` - Volatilidad diaria
- `Volatility.W` - Volatilidad semanal
- `Volatility.M` - Volatilidad mensual
- `beta_1_year` - Beta (1 año)

---

## 📅 Calendario de Eventos

### Clase: `CalendarScraper.scrape_earnings()`

**Eventos de Ganancias:**
- `logoid` - ID del logo
- `name` - Nombre de la empresa
- `earnings_per_share_fq` - EPS trimestral
- `timestamp` - Fecha del evento
- `market` - Mercado (america, europe, asia, etc.)

**Filtros Disponibles:**
- Rango de fechas (timestamp inicio, timestamp fin)
- Mercados específicos (america, uk, india, australia, canada, etc.)
- Campos personalizados (`values`)

### Clase: `CalendarScraper.scrape_dividends()`

**Eventos de Dividendos:**
- `logoid` - ID del logo
- `name` - Nombre de la empresa
- `dividends_yield` - Rendimiento del dividendo
- `timestamp` - Fecha del evento
- `market` - Mercado

**Filtros Disponibles:**
- Rango de fechas
- Mercados específicos
- Campos personalizados

---

## ⚡ Datos en Tiempo Real

### Clase: `RealTimeData.get_ohlcv()`

**Datos OHLCV:**
- `timestamp` - Timestamp del período
- `open` - Precio de apertura
- `high` - Precio máximo
- `low` - Precio mínimo
- `close` - Precio de cierre
- `volume` - Volumen

**Parámetros:**
- `exchange_symbol` - Símbolo completo (ej: "NASDAQ:AAPL")
- Retorna un generador que emite datos en tiempo real

### Clase: `RealTimeData.get_latest_trade_info()`

**Información de Última Transacción:**
- `volume` - Volumen
- `lp_time` - Hora del último precio
- `lp` - Último precio
- `ch` - Cambio absoluto
- `chp` - Cambio porcentual

**Parámetros:**
- `exchange_symbol` - Lista de símbolos (ej: ["NASDAQ:AAPL", "NYSE:TSLA"])

### Clase: `Streamer.stream()`

**Streaming Completo (OHLCV + Indicadores):**
- Datos OHLCV históricos
- Indicadores técnicos históricos
- Datos en tiempo real continuos

**Parámetros:**
- `exchange` - Exchange (NASDAQ, NYSE, etc.)
- `symbol` - Símbolo
- `timeframe` - Marco temporal
- `numb_price_candles` - Número de velas históricas
- `indicator_id` - ID del indicador (ej: "STD;RSI")
- `indicator_version` - Versión del indicador
- `websocket_jwt_token` - Token JWT de TradingView (requerido para indicadores)

---

## 🔄 Análisis Comparativo

### Clase: `FundamentalGraphs.compare_fundamentals()`

**Comparación Multi-Símbolo:**
- Compara múltiples símbolos simultáneamente
- Campos personalizables
- Retorna datos estructurados por campo y símbolo

**Campos Comparables:**
- Cualquier campo disponible en `get_fundamentals()`
- Ejemplos: `total_revenue`, `net_income`, `EBITDA`, `market_cap_basic`, `price_earnings_ttm`, etc.

**Parámetros:**
- `symbols` - Lista de símbolos (ej: ['NASDAQ:AAPL', 'NASDAQ:MSFT'])
- `fields` - Lista de campos a comparar

---

## 📊 Resumen de Métodos Disponibles

### Overview
- `get_symbol_overview()` - Vista general completa
- `get_profile()` - Perfil de la empresa
- `get_statistics()` - Estadísticas de mercado
- `get_financials()` - Datos financieros
- `get_performance()` - Métricas de rendimiento
- `get_technicals()` - Indicadores técnicos

### FundamentalGraphs
- `get_fundamentals()` - Datos fundamentales completos
- `get_income_statement()` - Estado de resultados
- `get_balance_sheet()` - Balance general
- `get_cash_flow()` - Flujo de efectivo
- `get_profitability()` - Métricas de rentabilidad
- `get_margins()` - Márgenes
- `get_liquidity()` - Ratios de liquidez
- `get_leverage()` - Ratios de apalancamiento
- `get_valuation()` - Métricas de valoración
- `get_dividends()` - Información de dividendos
- `compare_fundamentals()` - Comparación multi-símbolo

### NewsScraper
- `scrape_headlines()` - Encabezados de noticias
- `scrape_news_content()` - Contenido completo de noticias

### Ideas
- `scrape()` - Ideas de trading de la comunidad

### Minds
- `get_minds()` - Discusiones de la comunidad
- `get_all_minds()` - Todas las discusiones (con paginación)

### Indicators
- `scrape()` - Indicadores técnicos

### CalendarScraper
- `scrape_earnings()` - Eventos de ganancias
- `scrape_dividends()` - Eventos de dividendos

### RealTimeData
- `get_ohlcv()` - Datos OHLCV en tiempo real
- `get_latest_trade_info()` - Información de última transacción

### Streamer
- `stream()` - Streaming completo con indicadores

---

## 📝 Notas Importantes

1. **Formato de Símbolos:** Todos los símbolos deben incluir el prefijo del exchange (ej: "NASDAQ:AAPL", "NYSE:TSLA", "BVC:ECOPETROL")

2. **Mercados Soportados:**
   - Stocks: America, UK, India, Australia, Canada, Germany, etc.
   - Crypto: Todos los exchanges principales
   - Forex: Todos los pares principales
   - Otros: Bonds, Futures, CFD

3. **Limitaciones:**
   - Algunos datos pueden no estar disponibles para todos los símbolos
   - Los datos históricos pueden tener limitaciones de tiempo
   - Requiere conexión a internet activa

4. **Exportación:**
   - Todos los scrapers soportan exportación a JSON y CSV
   - Usar `export_result=True` y `export_type='json'` o `'csv'`

5. **Rate Limiting:**
   - TradingView puede aplicar límites de velocidad
   - Se recomienda usar delays entre solicitudes

---

## 🎯 Casos de Uso Recomendados

1. **Análisis Fundamental Completo:** Usar `FundamentalGraphs` para análisis profundo
2. **Análisis Técnico:** Usar `Indicators` y `Overview.get_technicals()`
3. **Sentimiento del Mercado:** Usar `NewsScraper` y `Minds`
4. **Monitoreo en Tiempo Real:** Usar `RealTimeData` y `Streamer`
5. **Comparación de Empresas:** Usar `compare_fundamentals()`
6. **Calendario de Eventos:** Usar `CalendarScraper` para fechas importantes

---

**Última actualización:** Febrero 2026
**Versión de tradingview-scraper:** 0.4.19+
