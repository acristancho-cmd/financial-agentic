"""
Servicio de dividendos Peru: TradingView + BVL.com.pe
TV : hoy - 4 semanas → hoy + 8 semanas
BVL: sin filtro (lista completa declarada)
Optimizado para Vercel free tier (< 10s): TV y BVL corren en paralelo.
"""
import os
import datetime
import requests as http
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from tradingview_scraper.symbols.cal import CalendarScraper
from tradingview_scraper.symbols.overview import Overview
from app.scrapers.bvl_scraper import scrape_bvl_dividends

SUPABASE_URL          = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY          = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY  = os.getenv("SUPABASE_SERVICE_KEY")
TABLE        = "dividendos_peru"
BATCH        = 50

# Whitelist de tickers permitidos — comparar siempre con .strip().upper()
PERU_TICKER_WHITELIST: frozenset[str] = frozenset({
    "MMM", "AENZAC1", "ALICORC1", "GOOGL", "AMZN", "AXP", "AIHC1", "AAPL",
    "T", "AUNA", "CREDITC1", "INTERBC1", "BAC", "ABX", "BBVAC1", "CARTAVC1",
    "CASAGRC1", "CPACASC1", "CPACASI1", "CDPR", "SNJUANC1", "SNJUANI1",
    "CSCO", "C", "KO", "BVN", "PODERC1", "CORAREI1", "CORAREC1", "CORLINI1",
    "BAP", "NUGT", "DIS", "SEA", "HIDRA2C1", "POMALCC1", "SIDERC1", "ENDISPC1",
    "ENGEPEC1", "ENGIEC1", "FERREYC1", "FIBCCAP", "FIBPRIME", "XLF", "ETFPERUD",
    "GE", "BOTZ", "GS", "XLV", "HBM", "INRETC1", "INTC", "IFS", "IPCHAC1",
    "IPCHBC1", "BTCO", "QQQ", "IBIT", "IBHD", "IBTE", "ILF", "EEM", "EWJ",
    "IYR", "JNJ", "JPM", "GLORIAI1", "LUSURC1", "META", "MSFT", "ATACOBC1",
    "MINSURI1", "EPU", "NFLX", "NEXAPEC1", "NVDA", "ORYGENC1", "PML", "PYPL",
    "ETFPESOV", "EXALMC1", "PFE", "PLUZENC1", "PPX", "BTCCU", "RIO", "SPY",
    "CRM", "SMT", "AGMR", "CVERDEC1", "BROCALC1", "SCCO", "SPCCPI1", "DIA",
    "GLD", "SBUX", "TMUS", "XLK", "TSLA", "PG", "JETS", "GOAU", "UNACEMC1",
    "BACKUSI1", "USO", "HODL", "DFNS", "GDX", "MOAT", "SMH", "NLR", "VEA",
    "VWO", "VZ", "V", "VOLCABC1", "WMT", "ZM",
})

# Nombres completos por ticker (fuente: whitelist oficial)
NOMBRES_PERU: dict[str, str] = {
    "MMM":      "3M Company",
    "AENZAC1":  "Aenza",
    "ALICORC1": "Alicorp",
    "GOOGL":    "Alphabet Inc.",
    "AMZN":     "Amazon",
    "AXP":      "American Express",
    "AIHC1":    "Andino Investment Holding S.A.A.",
    "AAPL":     "Apple",
    "T":        "AT&T Inc",
    "AUNA":     "Auna S.A.",
    "CREDITC1": "Banco de Crédito del Perú",
    "INTERBC1": "Banco Internacional del Perú",
    "BAC":      "Bank of America Corporation",
    "ABX":      "Barrick",
    "BBVAC1":   "BBVA Perú",
    "CARTAVC1": "Cartavio Sociedad Anónima Abierta",
    "CASAGRC1": "Casa Grande",
    "CPACASC1": "Cementos Pacasmayo",
    "CPACASI1": "Cementos Pacasmayo S.A.A.",
    "CDPR":     "Cerro de Pasco Resources Inc.",
    "SNJUANC1": "Cervecería San Juan S.A.",
    "SNJUANI1": "Cervecería San Juan S.A.",
    "CSCO":     "Cisco Systems",
    "C":        "Citigroup",
    "KO":       "Coca Cola Co.",
    "BVN":      "Compañía de Minas Buenaventura",
    "PODERC1":  "Compañía Minera Poderosa S.A.",
    "CORAREI1": "Corporación Aceros Arequipa",
    "CORAREC1": "Corporación Aceros Arequipa S.A.",
    "CORLINI1": "Corporación Lindley SA",
    "BAP":      "Credicorp Ltd",
    "NUGT":     "Direxion Daily Gold Miners",
    "DIS":      "Disney",
    "SEA":      "U.S. Global Sea to Sky Cargo ETF",
    "HIDRA2C1": "Hidrandina",
    "POMALCC1": "Empresa Agroindustrial Pomalca S.A.A.",
    "SIDERC1":  "Empresa Siderúrgica del Perú",
    "ENDISPC1": "Enel Distribución Perú",
    "ENGEPEC1": "Enel Generación Perú",
    "ENGIEC1":  "Engie Energía Perú",
    "FERREYC1": "Ferreycorp",
    "FIBCCAP":  "Fibra Credicorp",
    "FIBPRIME": "FIBRA Prime",
    "XLF":      "Financial Select Sec SPDR ETF",
    "ETFPERUD": "Fondo Bursátil VanEck el Dorado ETF",
    "GE":       "General Electric Company",
    "BOTZ":     "Global X Robotics & A.I. ETF",
    "GS":       "Goldman Sachs Group Inc.",
    "CSPFIBPR": "Grupo Coril Sociedad Titulizadora S.A.",
    "XLV":      "Health Care Sel Sect SPDR Fund",
    "HBM":      "HudBay Minerals Inc",
    "INRETC1":  "InRetail Perú",
    "INTC":     "Intel Corporation",
    "IFS":      "Intercorp Financial Services Inc",
    "IPCHAC1":  "Inversiones Portuarias Chancay S.A.A.",
    "IPCHBC1":  "Inversiones Portuarias Chancay S.A.A.",
    "BTCO":     "Invesco Galaxy Bitcoin ETF",
    "QQQ":      "Invesco QQQ Trust, Series 1",
    "IBIT":     "iShares Bitcoin Trust",
    "IBHD":     "iShares iBonds 2024 Term High Yield and Income ETF",
    "IBTE":     "iShares iBonds Dec 2024 Term Treasury ETF",
    "ILF":      "iShares Latin America 40 ETF",
    "EEM":      "iShares MSCI Emerging Mkts ETF",
    "EWJ":      "iShares MSCI Japan ETF",
    "IYR":      "iShares US Real Estate ETF",
    "JNJ":      "Johnson & Johnson",
    "JPM":      "JPMorgan Chase & Co.",
    "GLORIAI1": "Leche Gloria S.A.",
    "LUSURC1":  "Luz del Sur",
    "META":     "Meta Platforms",
    "MSFT":     "Microsoft Corporation",
    "ATACOBC1": "Minera Atacocha",
    "MINSURI1": "Minsur",
    "EPU":      "MSCI All Perú Capp ETF",
    "NFLX":     "Netflix, Inc.",
    "NEXAPEC1": "Nexa Resources Perú S.A.A.",
    "NVDA":     "NVIDIA Corporation",
    "ORYGENC1": "Orygen Perú S.A.A",
    "PML":      "Panoro Minerals Ltd.",
    "PYPL":     "PayPal Holdings, Inc.",
    "ETFPESOV": "Perú Soberano VanEck El Dorado ID ETF",
    "EXALMC1":  "Pesquera Exalmar S.A.A.",
    "PFE":      "Pfizer",
    "PLUZENC1": "Pluz Energía Perú S.A.A",
    "PPX":      "PPX Mining Corp.",
    "BTCCU":    "Purpose Bitcoin USD ETF Non-Currency Hedged",
    "RIO":      "Rio2 Limited",
    "SPY":      "S&P 500 ETF Trust",
    "CRM":      "Salesforce",
    "SMT":      "Sierra Metals Inc.",
    "AGMR":     "Silver Mountain Resources Ord Shs",
    "CVERDEC1": "Sociedad Minera Cerro Verde",
    "BROCALC1": "Sociedad Minera el Brocal",
    "SCCO":     "Southern Copper Corporation",
    "SPCCPI1":  "Southern Peru Copper Corporation - Sucursal Del Peru",
    "DIA":      "SPDR Dow Jones ETF Trust",
    "GLD":      "SPDR Gold Trust",
    "SBUX":     "Starbucks Corp",
    "TMUS":     "T-Mobile US Inc.",
    "XLK":      "Technology Select Sec SPDR Fund",
    "TSLA":     "Tesla",
    "PG":       "The Procter & Gamble Company",
    "JETS":     "The U.S. Global Jets",
    "GOAU":     "U.S. Global GO GOLD",
    "UNACEMC1": "Unión Andina de Cementos",
    "BACKUSI1": "Unión de Cervecerías Peruanas",
    "USO":      "United States Oil Fund, LP",
    "HODL":     "VanEck Bitcoin Trust",
    "DFNS":     "VanEck Defense UCITS",
    "GDX":      "VanEck Gold Miners ETF",
    "MOAT":     "VanEck Morningstar Wide Moat ETF",
    "SMH":      "VanEck Semiconductor ETF",
    "NLR":      "VanEck Uranium and Nuclear ETF",
    "VEA":      "Vanguard FTSE Developed Mkts ETF",
    "VWO":      "Vanguard FTSE Emerging Mkts ETF",
    "VZ":       "Verizon Communications Inc.",
    "V":        "Visa Inc.",
    "VOLCABC1": "Volcán Compañía Minera",
    "WMT":      "Walmart Inc.",
    "ZM":       "Zoom Video Communications, Inc",
}


def _get_nombre_peru(ticker: str) -> str | None:
    """Nombre desde dict estático. Si el ticker termina en 'US', prueba sin el sufijo."""
    t = ticker.strip().upper()
    if t in NOMBRES_PERU:
        return NOMBRES_PERU[t]
    if len(t) > 2 and t.endswith("US") and t[:-2] in NOMBRES_PERU:
        return NOMBRES_PERU[t[:-2]]
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────
def _in_whitelist(ticker: str) -> bool:
    """Verifica si un ticker está en la whitelist.
    BVL/TV agrega sufijo 'US' a acciones listadas en EEUU (GOOGLUS -> GOOGL).
    Se comprueba el ticker directo y, si termina en 'US', también sin el sufijo.
    """
    t = ticker.strip().upper()
    if t in PERU_TICKER_WHITELIST:
        return True
    if len(t) > 2 and t.endswith("US") and t[:-2] in PERU_TICKER_WHITELIST:
        return True
    return False


def _ts_to_date(ts) -> str | None:
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")


def _to_pen(amount, currency, tc) -> float | None:
    if amount is None:
        return None
    return round(amount * tc, 6) if currency == "USD" else round(amount, 6)


def get_tc_usdpen() -> float:
    return round(yf.Ticker("USDPEN=X").fast_info["last_price"], 4)


# ── Fetch TradingView ─────────────────────────────────────────────────────────
def fetch_tv(tc: float) -> list[dict]:
    now   = datetime.datetime.now(tz=datetime.timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ts_from = int((today - datetime.timedelta(weeks=4)).timestamp())
    ts_to   = int((today + datetime.timedelta(weeks=8, seconds=86399)).timestamp())

    raw = CalendarScraper().scrape_dividends(
        timestamp_from=ts_from,
        timestamp_to=ts_to,
        markets=["peru"],
    )

    seen: dict[tuple, dict] = {}
    for ev in raw:
        ex_date = _ts_to_date(ev.get("dividend_ex_date_upcoming")) or \
                  _ts_to_date(ev.get("dividend_ex_date_recent"))
        if not ex_date:
            continue
        full_sym = ev.get("full_symbol", "")
        ticker   = full_sym.split(":")[-1]
        if not _in_whitelist(ticker):
            continue
        key = (full_sym, ex_date)
        if key in seen:
            continue
        amount   = ev.get("dividend_amount_upcoming") or ev.get("dividend_amount_recent")
        currency = ev.get("fundamental_currency_code", "USD")
        seen[key] = {
            "symbol"         : full_sym,
            "nombre"         : _get_nombre_peru(ticker) or ev.get("name") or ev.get("description"),
            "fuente"         : "TV",
            "fecha_corte"    : ex_date,
            "fecha_pago"     : _ts_to_date(ev.get("dividend_payment_date_upcoming")) or
                               _ts_to_date(ev.get("dividend_payment_date_recent")),
            "monto_original" : amount,
            "moneda_original": currency,
            "tc_usdpen"      : tc if currency == "USD" else None,
            "monto_pen"      : _to_pen(amount, currency, tc),
            "tipo"           : "efectivo",
            "en_partes"      : False,
            "concepto"       : None,
            "yield_tv_pct"   : ev.get("dividends_yield"),
        }
    return list(seen.values())


# ── Precios BVL via TradingView Overview ──────────────────────────────────────
def _get_bvl_prices(symbols: list[str]) -> dict[str, float | None]:
    """Precio de cierre para símbolos BVL via TradingView Overview (solo para yield)."""
    if not symbols:
        return {}

    overview = Overview()

    def _fetch(sym: str):
        try:
            result = overview.get_symbol_overview(symbol=f"BVL:{sym}")
            if result.get("status") == "success":
                price = result["data"].get("close")
                if price:
                    return sym, float(price)
        except Exception:
            pass
        return sym, None

    with ThreadPoolExecutor(max_workers=8) as ex:
        return dict(ex.map(_fetch, symbols))


# ── Fetch BVL ─────────────────────────────────────────────────────────────────
def fetch_bvl(tc: float) -> list[dict]:
    rows = []
    for ev in scrape_bvl_dividends():
        if not ev.get("fecha_corte"):
            continue
        symbol = ev.get("symbol", "")
        if not _in_whitelist(symbol):
            continue
        amount   = ev.get("amount")
        currency = ev.get("currency")
        tipo     = ev.get("tipo", "desconocido")
        monto_pen = _to_pen(amount, currency, tc) if tipo == "efectivo" else None
        rows.append({
            "symbol"         : symbol,
            "nombre"         : NOMBRES_PERU.get(symbol, symbol),
            "fuente"         : "BVL",
            "fecha_corte"    : ev.get("fecha_corte"),
            "fecha_registro" : ev.get("fecha_registro"),
            "fecha_pago"     : ev.get("fecha_entrega"),
            "fecha_acuerdo"  : ev.get("fecha_acuerdo"),
            "monto_original" : amount,
            "moneda_original": currency,
            "tc_usdpen"      : tc if currency == "USD" else None,
            "monto_pen"      : monto_pen,
            "tipo"           : tipo,
            "en_partes"      : ev.get("fecha_entrega_parcial", False),
            "concepto"       : ev.get("concepto"),
            "yield_tv_pct"   : None,
        })

    # Deduplicar por (symbol, fecha_corte): sumar montos, concatenar conceptos
    merged: dict[tuple, dict] = {}
    for r in rows:
        key = (r["symbol"], r["fecha_corte"])
        if key not in merged:
            merged[key] = r.copy()
        else:
            existing = merged[key]
            if r["monto_original"] is not None and existing["monto_original"] is not None:
                existing["monto_original"] = round(existing["monto_original"] + r["monto_original"], 8)
            if r["monto_pen"] is not None and existing["monto_pen"] is not None:
                existing["monto_pen"] = round(existing["monto_pen"] + r["monto_pen"], 6)
            if r["concepto"] and existing["concepto"]:
                existing["concepto"] = existing["concepto"] + " + " + r["concepto"]
    rows = list(merged.values())

    # Calcular yield: (monto_pen / precio_actual_pen) * 100
    candidatos = [r["symbol"] for r in rows if r["tipo"] == "efectivo" and r["monto_pen"]]
    if candidatos:
        precios = _get_bvl_prices(candidatos)
        for r in rows:
            precio = precios.get(r["symbol"])
            if precio and precio > 0 and r["monto_pen"]:
                r["yield_tv_pct"] = round(r["monto_pen"] / precio * 100, 6)

    return rows


# ── Preview (TV + BVL en paralelo) ────────────────────────────────────────────
def get_preview() -> dict:
    # 1. TC primero (~2s)
    tc = get_tc_usdpen()

    # 2. TV + BVL en paralelo (~4s) → total ~6s, dentro del límite de 10s de Vercel
    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_tv  = executor.submit(fetch_tv, tc)
        fut_bvl = executor.submit(fetch_bvl, tc)
        tv_rows  = fut_tv.result()
        bvl_error = None
        try:
            bvl_rows = fut_bvl.result()
        except Exception as e:
            bvl_rows  = []
            bvl_error = str(e)

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    tv_syms  = {r["symbol"].split(":")[-1] for r in tv_rows}
    bvl_syms = {r["symbol"] for r in bvl_rows}

    return {
        "fecha_preview"  : now.strftime("%Y-%m-%d %H:%M UTC"),
        "tc_usdpen"      : tc,
        "ventana_tv"     : {
            "desde": (now - datetime.timedelta(weeks=4)).strftime("%Y-%m-%d"),
            "hasta": (now + datetime.timedelta(weeks=8)).strftime("%Y-%m-%d"),
        },
        "ventana_bvl"    : "completa",
        "resumen"        : {
            "tv_total"        : len(tv_rows),
            "bvl_total"       : len(bvl_rows),
            "total_combinado" : len(tv_rows) + len(bvl_rows),
            "en_ambas_fuentes": sorted(tv_syms & bvl_syms),
        },
        "bvl_error"      : bvl_error,
        "tradingview"    : tv_rows,
        "bvl"            : bvl_rows,
    }


# ── Sync a Supabase ───────────────────────────────────────────────────────────
def _supabase_headers():
    key = SUPABASE_SERVICE_KEY or SUPABASE_KEY
    return {
        "apikey"       : key,
        "Authorization": f"Bearer {key}",
        "Content-Type" : "application/json",
        "Prefer"       : "resolution=merge-duplicates,return=minimal",
    }


def sync_to_supabase(tv_rows: list[dict], bvl_rows: list[dict]) -> dict:
    if not SUPABASE_URL or not (SUPABASE_SERVICE_KEY or SUPABASE_KEY):
        raise RuntimeError("Faltan credenciales Supabase en .env")

    url     = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    results = {"tv": 0, "bvl": 0, "errores": []}

    for fuente, rows in [("tv", tv_rows), ("bvl", bvl_rows)]:
        for i in range(0, len(rows), BATCH):
            batch = rows[i:i + BATCH]
            r = http.post(url, json=batch, headers=_supabase_headers(), timeout=30)
            if r.status_code in (200, 201, 204):
                results[fuente] += len(batch)
            else:
                results["errores"].append(
                    f"{fuente} batch {i//BATCH+1}: {r.status_code} {r.text[:100]}"
                )
    return results
