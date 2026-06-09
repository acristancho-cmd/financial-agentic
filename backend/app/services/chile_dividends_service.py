"""
Servicio de dividendos Chile: solo TradingView (BCS - Bolsa de Chile).
TV cubre acciones locales, internacionales CL y fondos CFI.
Moneda base: CLP. Dividendos USD se convierten con TC USDCLP=X.
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
TABLE                = "dividendos_chile"
BATCH                = 50


def _norm(t: str) -> str:
    """Normaliza un ticker: mayúsculas, sin espacios extremos,
    guiones y espacios → '_', puntos eliminados.
    Así EMBONOR-A, embonor_a y 'EMBONOR A' se comparan igual."""
    return t.strip().upper().replace("-", "_").replace(" ", "_").replace(".", "")


# Whitelist de tickers permitidos para Chile (BCS).
# Todos los valores están pre-normalizados con _norm().
# TV usa '_' donde la Bolsa usa '-' o espacios (EMBONOR_A, SQM_A, AZUL_AZUL).
# Sufijo CL para internacionales (GOOGLCL, MSFTCL...); la red de seguridad
# en _in_whitelist lo maneja si TV omite el sufijo.
_RAW_WHITELIST = [
    "MMMCL", "HABITAT", "CUPRUM", "ABTCL", "AAISA", "AESANDES", "PLANVITAL",
    "AGUAS-B", "AGUAS-A", "ALMENDRAL", "GOOGLCL", "GOOGCL", "AMZNCL", "AXPCL",
    "CFIAMDHY-A", "CFIADGHI", "CFIADGHC", "CFIAMDDA-E", "CFIAMDDI-E",
    "CFIAMDVACA", "CFIAMDVACB", "CFIAMDVACC", "CFIAMDVACI", "CFIAMDVACM",
    "CFIAMDVATA", "CFIAMDVAMC", "CFIAMDVAMA", "CFIAMDVASC", "CFIASPCP-E",
    "CFIASPLP-E", "CFIASSCP-E", "CFIASSLP-E", "ANTARCHILE", "AAPLCL",
    "AQUACHILE", "AZUL AZUL", "CHILE", "BCI", "BSANTANDER", "BANCOLOMCL",
    "BAC", "BACCL", "BANVIDA", "CFIBCISCBC", "BESALCO", "CFIBDEUDAI",
    "BICECORP", "BIIBCL", "COLO COLO", "BLUMAR", "BOLSASTGO", "BKNGCL",
    "CFIBTGRRA", "CFIBTGCYFA", "CFIBTGDAPA", "CFIBPDCCHA", "CFIDLDA-E",
    "CFIBPDPA-E", "CFIBTGFGIA", "CFIBTGRCA", "CFISCCH", "CAP", "CATCL",
    "CEMARGOSCL", "CEMENTOS", "CENCOSUD", "CENCOMALLS", "CFINASDAQ",
    "NTGCLGAS", "CVXCL", "CFIMCITI", "CINTAC", "CSCOCL", "CCL",
    "LAS CONDES", "EMBONOR-A", "EMBONOR-B", "COLBUN", "CCU", "CAMANCHACA",
    "VAPORES", "CIC", "CFICOMDPB", "CFICGGLOEB", "COSTCL", "CRISTALES",
    "CRUZADOS", "DAVIVIENCL", "CONDES-OSA", "HITES-OSA", "NITRA-OSA",
    "NORTE-OSA", "OROBCO-OSA", "EBAYCL", "EISA", "ANDINA-A", "ANDINA-B",
    "EDELMAG", "PEHUENCHE", "NUEVAPOLAR", "ENTEL", "CMPC", "COPEC",
    "HITES", "LIPIGAS", "TRICOT", "ENAEX", "ENELAM", "ENELCHILE",
    "ENELDXCH", "ENELGXCH", "ECL", "ENJOY", "CFISP500", "XOMCL",
    "CFIAFESA", "FBCL", "FALABELLA", "CFIBCLATCP", "CFIETFLP", "CFIETFIPSA",
    "CFMDIVO", "CFIDHS1", "CFIDHS2-A", "CFIAMDDC-E", "CFIBCDALTP",
    "CFICARVA-E", "CFIBCHBLEN", "CFIAMDVAMD", "CFIIMSCLI", "CFIBCHDALT",
    "CFIBCHDECH", "CFIBCHDEGB", "CFIBEDRA-E", "CFIBCHEMEQ", "CFIETFCC",
    "CFIETFCD", "CFIGC", "CFIETFGE", "CFIUSREIT", "CFIBCHEETA",
    "CFIFALCFIW", "CFIFALCEQA", "CFIFALCGLA", "CFIFALCTAC", "CFIBGRESTA",
    "CFINRENTAS", "CFILVFA-L", "CFILVCOR-I", "CFILVCOR-O", "CFILVCOR-A",
    "CFILVDPU-E", "CFILVPARI1", "CFIBCHLCHY", "CFIBACHLAT", "CFIBMPEM-E",
    "CFIBCHMPUS", "CFIBMPEU-E", "CFIBCHMPGB", "CFINVDPR-E", "CFISANDCHA",
    "CFISANTDCA", "CFISANTDLA", "CFISANRVGA", "CFISANTSCA", "CFILEASA",
    "CFIPROYA", "CFITACTI-A", "CFISUAUSE", "CFISUDCHE", "CFIBCHUETA",
    "CFMITNIPSA", "CFMESGIPSA", "PASUR", "FORUS", "FCXCL", "CFIFTRLPP",
    "GASCO", "GECL", "GILDCL", "GRPARGOSCL", "NAVIERA", "NUTRESACL",
    "SECURITY", "HALCL", "HDCL", "HONCL", "HF", "IANSA", "INGEVEC",
    "MANQUEHUE", "INDISA", "INTCCL", "IBMCL", "INVERCAP", "IAM", "ILC",
    "TRICAHUE", "SGOVCL", "TLT CL", "IBB CL", "IBITCL", "DGRO CL",
    "IYMCL", "IYKCL", "IYCCL", "IYECL", "ITBCL", "IYJCL", "IDUCL",
    "IYRCL", "IYZCL", "FXICL", "ICLNCL", "IAUCL", "HDV CL", "HYGCL",
    "LQDCL", "EMB CL", "ACWICL", "AAXJCL", "EPUCL", "EWACL", "EWZCL",
    "ECHCL", "MCHICL", "EFACL", "EEMCL", "EZUCL", "EWQCL", "EWGCL",
    "EWHCL", "INDA CL", "EWICL", "EWJCL", "EWWCL", "EPPCL", "ERUSCL",
    "EWYCL", "EWPCL", "EWTCL", "EWUCL", "IVWCL", "IVVCL", "ILFCL",
    "DVY CL", "IYG CL", "IYFCL", "IYH CL", "IYWCL", "ITAUCL", "JNJCL",
    "JPMCL", "LTM", "MASISA", "CFIMBILA-A", "CFIMBIDA-A", "CFIMBIRF-A",
    "CFIMBDPA-E", "CFIMBIDT-B", "CFIMBIGL-A", "CFIMBIRFUS", "MCDCL",
    "MRKCL", "MSFTCL", "MINERA", "CFIMDCHA", "CFIMDLATAE", "CFIMDCHD",
    "CFIMDCHE", "CFIMDCHI", "CFIMDLIG-A", "CFIMLDLAE", "CFIMLDL-B",
    "CFIMDLIG-I", "CFIIMDLAT", "CFIMLE-A", "CFIMLE-B", "CFIMLDL",
    "CFIMRCLPR", "CFIMRCLP", "CFIMRFIHYA", "CFIMRFIHYB", "CFIMRFHYBE",
    "CFIMRFIIGA", "CFIMRVCHA", "CFIMRBCHAE", "CFIMRVCHAE", "CFIMRVCHE",
    "CFIMRVCHI", "CFIMRVEA", "CFIMRVEC", "CFIMRVIA", "CFIMRVIB",
    "CFIMRVUSAA", "CFIMRVUSAC", "CFIMSC", "CFIMSCAE", "MSCL", "MULTI X",
    "NEMCL", "NKECL", "NITRATOS", "NORTEGRAN", "NUAM", "NVDACL",
    "RENTAS-OSA", "ORCLCL", "ORCL", "PARAUCO", "PAZ", "PEPCL", "PFECL",
    "CFIPIONERO", "CFIPIONAE", "MPLAZA-OSA", "MALLPLAZA", "FROWARD",
    "potasios-a", "potasios-b", "PGCL", "PROVIDA", "VENTANAS", "QCOMCL",
    "CFIQAC", "CFIQRGA", "QUINENCO", "RIPLEY", "SALFACORP", "SALMOCAM",
    "SCHWAGER", "SK", "CFIMSIGLO", "SMU", "ORO BLANCO", "SMSAAM",
    "PUCOBRE", "SQM-A", "SQM-B", "SOCOVESA", "SONDA", "SOQUICOM",
    "SBUXCL", "SURACL", "CFITACPI-E", "CFITACP2-E", "TGTCL", "BACL",
    "KOCL", "DISCL", "UPSCL", "XCL", "UNHCL", "CONCHATORO", "VCL",
    "WALMARTCL", "WATTS", "WFCCL", "ZOFRI",
]

CHILE_TICKER_WHITELIST: frozenset[str] = frozenset(_norm(t) for t in _RAW_WHITELIST)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _in_whitelist(ticker: str) -> bool:
    """Verifica si un ticker BCS está en la whitelist de Chile.
    Normaliza guiones/espacios a '_' y elimina puntos.
    Red de seguridad: si el ticker termina en 'CL', prueba sin el sufijo.
    """
    t = _norm(ticker)
    if t in CHILE_TICKER_WHITELIST:
        return True
    if len(t) > 2 and t.endswith("CL") and t[:-2] in CHILE_TICKER_WHITELIST:
        return True
    return False


def _ts_to_date(ts) -> str | None:
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")


def _to_clp(amount, currency, tc) -> float | None:
    if amount is None:
        return None
    return round(amount * tc, 2) if currency == "USD" else round(amount, 2)


def get_tc_usdclp() -> float:
    return round(yf.Ticker("USDCLP=X").fast_info["last_price"], 2)


# ── Precios BCS via TradingView Overview ──────────────────────────────────────
def _get_bcs_prices(symbols: list[str]) -> dict[str, float | None]:
    """Precio actual en CLP para stocks BCS sin yield en TV."""
    if not symbols:
        return {}

    overview = Overview()

    def _fetch(sym: str):
        try:
            result = overview.get_symbol_overview(symbol=f"BCS:{sym}")
            if result.get("status") == "success":
                price = result["data"].get("close")
                if price:
                    return sym, float(price)
        except Exception:
            pass
        return sym, None

    with ThreadPoolExecutor(max_workers=8) as ex:
        return dict(ex.map(_fetch, symbols))


# ── Fetch TradingView Chile ───────────────────────────────────────────────────
def fetch_tv_chile(tc: float) -> list[dict]:
    now   = datetime.datetime.now(tz=datetime.timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ts_from = int((today - datetime.timedelta(weeks=4)).timestamp())
    ts_to   = int((today + datetime.timedelta(weeks=8, seconds=86399)).timestamp())

    raw = CalendarScraper().scrape_dividends(
        timestamp_from=ts_from,
        timestamp_to=ts_to,
        markets=["chile"],
    )

    rows = []
    for ev in raw:
        ex_date = _ts_to_date(ev.get("dividend_ex_date_upcoming")) or \
                  _ts_to_date(ev.get("dividend_ex_date_recent"))
        if not ex_date:
            continue
        full_sym = ev.get("full_symbol", "")
        ticker   = full_sym.split(":")[-1]
        if not _in_whitelist(ticker):
            continue
        amount    = ev.get("dividend_amount_upcoming") or ev.get("dividend_amount_recent")
        currency  = ev.get("fundamental_currency_code", "USD")
        monto_clp = _to_clp(amount, currency, tc)
        rows.append({
            "symbol"         : full_sym,
            "nombre"         : ev.get("name") or ev.get("description"),
            "fuente"         : "TV",
            "fecha_corte"    : ex_date,
            "fecha_pago"     : _ts_to_date(ev.get("dividend_payment_date_upcoming")) or
                               _ts_to_date(ev.get("dividend_payment_date_recent")),
            "monto_original" : amount,
            "moneda_original": currency,
            "tc_usdclp"      : tc if currency == "USD" else None,
            "monto_clp"      : monto_clp,
            "tipo"           : "efectivo",
            "en_partes"      : False,
            "concepto"       : None,
            "yield_tv_pct"   : ev.get("dividends_yield"),
        })

    # Para los sin yield en TV, calcular con precio CLP de Overview
    sin_yield = [
        r["symbol"].split(":")[-1]
        for r in rows
        if r["yield_tv_pct"] is None and r["monto_clp"]
    ]
    if sin_yield:
        precios = _get_bcs_prices(sin_yield)
        for r in rows:
            if r["yield_tv_pct"] is None and r["monto_clp"]:
                sym_short = r["symbol"].split(":")[-1]
                precio = precios.get(sym_short)
                if precio and precio > 0:
                    r["yield_tv_pct"] = round(r["monto_clp"] / precio * 100, 6)

    return rows


# ── Preview ───────────────────────────────────────────────────────────────────
def get_preview() -> dict:
    tc  = get_tc_usdclp()
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    rows = fetch_tv_chile(tc)

    return {
        "fecha_preview" : now.strftime("%Y-%m-%d %H:%M UTC"),
        "tc_usdclp"     : tc,
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
