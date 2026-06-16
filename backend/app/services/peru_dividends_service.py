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
            "nombre"         : ev.get("name") or ev.get("description"),
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


# ── Info BVL via TradingView Overview (precio + nombre) ───────────────────────
def _get_bvl_info(symbols: list[str]) -> dict[str, dict]:
    """Retorna {symbol: {price, nombre}} para símbolos BVL via TradingView Overview."""
    if not symbols:
        return {}

    overview = Overview()

    def _fetch(sym: str):
        try:
            result = overview.get_symbol_overview(symbol=f"BVL:{sym}")
            if result.get("status") == "success":
                data   = result["data"]
                price  = data.get("close")
                nombre = data.get("description") or sym
                return sym, {"price": float(price) if price else None, "nombre": nombre}
        except Exception:
            pass
        return sym, {"price": None, "nombre": sym}

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
            "nombre"         : symbol,          # se sobreescribe abajo con nombre real
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

    # Obtener nombre real y precio desde TradingView Overview
    symbols_uniq = list({r["symbol"] for r in rows})
    info = _get_bvl_info(symbols_uniq)
    for r in rows:
        data = info.get(r["symbol"], {})
        r["nombre"] = data.get("nombre") or r["symbol"]
        precio = data.get("price")
        if precio and precio > 0 and r["monto_pen"] and r["tipo"] == "efectivo":
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
