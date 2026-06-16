"""
Servicio de dividendos Colombia: solo TradingView (BVC).
TV cubre todas las acciones BVC — no se necesita scraper adicional.
Moneda base: COP. Dividendos USD se convierten con TC USDCOP=X.
"""
import os
import datetime
import requests as http
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from tradingview_scraper.symbols.cal import CalendarScraper
from tradingview_scraper.symbols.overview import Overview

SUPABASE_URL         = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY         = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TABLE                = "dividendos_colombia"
BATCH                = 50

# Whitelist de tickers permitidos para Colombia (BVC).
# BRK.B se normaliza a BRKB (sin punto) para coincidir con lo que devuelve TV.
# BVC agrega sufijo "CO" a algunos activos internacionales (MSFTCO, TSLACO...).
COLOMBIA_TICKER_WHITELIST: frozenset[str] = frozenset({
    "AGUASACO", "ALICORC1CO", "GOOGL", "AMZN", "AAPL", "PFAVAL",
    "BHI", "BOGOTA", "CHILECO", "BCICO", "BAC", "BRKB",
    "BVC", "CNEC", "CAPCO", "CELSIA", "CEMARGOS", "PFCEMARGOS",
    "CPACASC1CO", "CENCOSUDCO", "CENCOMALCO", "C", "COLBUNCO",
    "CCUCO", "BVNCO", "VAPORESCO", "CONCONCRET", "EIMI", "CSPX",
    "CORFICOLCF", "PFCORFICOL", "BAPCO", "PFDAVVNDA", "PFDAVIGRP",
    "SPXS", "AMDVASCCO", "ECOPETROL", "ANDINABCO", "ENTELCO",
    "CMPCCO", "COPECCO", "ENELAMCO", "ENELCHILCO", "ECLCO",
    "ENKA", "ETB", "ICHN", "EXITO", "FALABELLCO", "FERREYC1CO",
    "F", "GEHC", "GE", "COPX", "LIT", "GXTESCOL", "URA",
    "GRUPOARGOS", "PFGRUPOARG", "GRUPOAVAL", "GRUBOLIVAR",
    "CIBEST", "PFCIBEST", "GEB", "NUTRESA", "GRUPOSURA", "PFGRUPOSURA",
    "HCOLSEL", "HIVECO", "ICOLPCAP", "INRETC1CO", "IFSCO", "IAMCO",
    "IPCHBC1CO", "EQAC", "SGLD", "ISA", "IUIT", "IB01", "LQDA",
    "SDIA", "CBU7", "RBOT", "IBIT", "IJPA", "IWVL", "INRA",
    "D26ACO", "ID27CO", "D28ACO", "ID29CO", "ID30CO",
    "EMGA", "ISAC", "4BRZ", "IDSE", "SUAS", "I500CO",
    "IUES", "IUFS", "IUHC", "CFMITNIPCO", "ITAUCLCO", "JPEA",
    "JNJ", "JPM", "LTMCO", "META", "MSFTCO", "MINEROS",
    "NKE", "NUAMCO", "NU", "NVDA", "PARAUCOCO", "PEI", "PBR",
    "PFE", "MALLPLAZCO", "PROMIGAS", "QUINENCOCO", "RIPLEYCO",
    "BSANTANDCO", "SMUCO", "CVERDEC1CO", "PORT", "SQMBCO",
    "SCCOCO", "SUM", "TERPEL", "TSLACO", "KOCO", "JETS", "TIN",
    "GOAUCO", "UBER", "SDHA", "GDXCO", "SMHCO", "VOO",
    "CONCHATOCO", "VOLCABC1CO",
    "PFGRUPSURA",   # alias TV de PFGRUPOSURA (Grupo Sura preferencial)
    "ICOLCAP",      # alias TV de ICOLPCAP (ETF iColcap)
})


# ── Helpers ───────────────────────────────────────────────────────────────────
def _in_whitelist(ticker: str) -> bool:
    """Verifica si un ticker está en la whitelist de Colombia.
    Normaliza puntos (BRK.B -> BRKB) y maneja el sufijo CO que BVC agrega
    a algunos activos internacionales (GOOGLCO -> GOOGL como red de seguridad).
    """
    t = ticker.strip().upper().replace(".", "")
    if t in COLOMBIA_TICKER_WHITELIST:
        return True
    if len(t) > 2 and t.endswith("CO") and t[:-2] in COLOMBIA_TICKER_WHITELIST:
        return True
    return False


def _ts_to_date(ts) -> str | None:
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")


def _to_cop(amount, currency, tc) -> float | None:
    if amount is None:
        return None
    return round(amount * tc, 2) if currency == "USD" else round(amount, 2)


def get_tc_usdcop() -> float:
    return round(yf.Ticker("USDCOP=X").fast_info["last_price"], 2)


# ── Precios BVC via TradingView Overview ──────────────────────────────────────
def _get_bvc_prices(symbols: list[str]) -> dict[str, float | None]:
    """Precio actual en COP para stocks BVC sin yield en TV."""
    if not symbols:
        return {}

    overview = Overview()

    def _fetch(sym: str):
        try:
            result = overview.get_symbol_overview(symbol=f"BVC:{sym}")
            if result.get("status") == "success":
                price = result["data"].get("close")
                if price:
                    return sym, float(price)
        except Exception:
            pass
        return sym, None

    with ThreadPoolExecutor(max_workers=8) as ex:
        return dict(ex.map(_fetch, symbols))


# ── Fetch TradingView Colombia ────────────────────────────────────────────────
def fetch_tv_colombia(tc: float) -> list[dict]:
    now   = datetime.datetime.now(tz=datetime.timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ts_from = int((today - datetime.timedelta(weeks=4)).timestamp())
    ts_to   = int((today + datetime.timedelta(weeks=8, seconds=86399)).timestamp())

    raw = CalendarScraper().scrape_dividends(
        timestamp_from=ts_from,
        timestamp_to=ts_to,
        markets=["colombia"],
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
        monto_cop = _to_cop(amount, currency, tc)
        seen[key] = {
            "symbol"         : full_sym,
            "nombre"         : ev.get("name") or ev.get("description"),
            "fuente"         : "TV",
            "fecha_corte"    : ex_date,
            "fecha_pago"     : _ts_to_date(ev.get("dividend_payment_date_upcoming")) or
                               _ts_to_date(ev.get("dividend_payment_date_recent")),
            "monto_original" : amount,
            "moneda_original": currency,
            "tc_usdcop"      : tc if currency == "USD" else None,
            "monto_cop"      : monto_cop,
            "tipo"           : "efectivo",
            "en_partes"      : False,
            "concepto"       : None,
            "yield_tv_pct"   : ev.get("dividends_yield"),
        }
    rows = list(seen.values())

    # Para los sin yield en TV, calcular con precio COP de Overview
    sin_yield = [
        r["symbol"].split(":")[-1]
        for r in rows
        if r["yield_tv_pct"] is None and r["monto_cop"]
    ]
    if sin_yield:
        precios = _get_bvc_prices(sin_yield)
        for r in rows:
            if r["yield_tv_pct"] is None and r["monto_cop"]:
                sym_short = r["symbol"].split(":")[-1]
                precio = precios.get(sym_short)
                if precio and precio > 0:
                    r["yield_tv_pct"] = round(r["monto_cop"] / precio * 100, 6)

    return rows


# ── Preview ───────────────────────────────────────────────────────────────────
def get_preview() -> dict:
    tc  = get_tc_usdcop()
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    rows = fetch_tv_colombia(tc)

    return {
        "fecha_preview" : now.strftime("%Y-%m-%d %H:%M UTC"),
        "tc_usdcop"     : tc,
        "ventana_tv"    : {
            "desde": (now - datetime.timedelta(weeks=4)).strftime("%Y-%m-%d"),
            "hasta": (now + datetime.timedelta(weeks=8)).strftime("%Y-%m-%d"),
        },
        "resumen": {
            "tv_total"  : len(rows),
            "con_yield" : sum(1 for r in rows if r["yield_tv_pct"] is not None),
            "sin_yield" : sum(1 for r in rows if r["yield_tv_pct"] is None),
        },
        "dividendos": rows,
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


def sync_to_supabase(rows: list[dict]) -> dict:
    if not SUPABASE_URL or not (SUPABASE_SERVICE_KEY or SUPABASE_KEY):
        raise RuntimeError("Faltan credenciales Supabase en .env")

    url     = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    results = {"guardados": 0, "errores": []}

    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        r = http.post(url, json=batch, headers=_supabase_headers(), timeout=30)
        if r.status_code in (200, 201, 204):
            results["guardados"] += len(batch)
        else:
            results["errores"].append(
                f"batch {i//BATCH+1}: {r.status_code} {r.text[:100]}"
            )
    return results
