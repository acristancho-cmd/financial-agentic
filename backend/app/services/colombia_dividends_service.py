"""
Servicio de dividendos Colombia: boletín oficial BVC (Fechas Exdividendo) + precio TradingView.
Dividendos: boletín "Fechas Exdividendo" de BVC (CMS Hygraph -> XLSX oficial),
filtrado al mes calendario actual (mes que contiene la fecha de hoy, completo).
Precio (solo para calcular yield): TradingView Overview — es lo único que se sigue
consultando en TV; el calendario de dividendos de TV (fetch_tv_colombia) quedó abajo comentado.
Moneda base: COP. Cada moneda que traiga el boletín se convierte a COP con su propia tasa FX.
"""
import calendar
import io
import os
import re
import datetime
import requests as http
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from openpyxl import load_workbook
# from tradingview_scraper.symbols.cal import CalendarScraper  # ya no se usa: dividendos vienen del boletín oficial BVC
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

# Nombres completos por ticker (fuente: whitelist oficial)
NOMBRES_COLOMBIA: dict[str, str] = {
    "AGUASACO":    "Aguas Andinas S.A.",
    "ALICORC1CO":  "Alicorp S.A.",
    "GOOGL":       "Alphabet Inc.",
    "AMZN":        "Amazon",
    "AAPL":        "Apple Inc.",
    "PFAVAL":      "Aval Preferencial",
    "BHI":         "BAC Holding International",
    "BOGOTA":      "Banco de Bogotá",
    "CHILECO":     "Banco de Chile",
    "BCICO":       "Banco de Crédito e Inversiones",
    "BAC":         "Bank of America Corporation",
    "BRKB":        "Berkshire Hathaway Inc Class B",
    "BVC":         "Bolsa de Valores de Colombia",
    "CNEC":        "Canacol",
    "CAPCO":       "Cap S.A.",
    "CELSIA":      "Celsia",
    "CEMARGOS":    "Cementos Argos",
    "PFCEMARGOS":  "Cementos Argos Preferencial",
    "CPACASC1CO":  "Cementos Pacasmayo S.A.A.",
    "CENCOSUDCO":  "Cencosud SA",
    "CENCOMALCO":  "Cencosud Shopping S.A.",
    "C":           "Citigroup Inc.",
    "COLBUNCO":    "Colbún S.A.",
    "CCUCO":       "Compañía Cervecerías Unidas S.A.",
    "BVNCO":       "Compañía de Minas Buenaventura S.A.A.",
    "VAPORESCO":   "Compañía Sud Americana de Vapores S.A.",
    "CONCONCRET":  "Concreto",
    "EIMI":        "Core MSCI EM IMI UCITS ETF USD",
    "CSPX":        "Core S&P 500",
    "CORFICOLCF":  "Corficolombiana",
    "PFCORFICOL":  "Corficolombiana Preferencial",
    "BAPCO":       "Credicorp Limited",
    "PFDAVVNDA":   "Davivienda",
    "PFDAVIGRP":   "Davivienda Group S.A",
    "SPXS":        "Direxion Daily S&P 500 Bear 3X Shares ETF",
    "AMDVASCCO":   "DVA Silicon Fund",
    "ECOPETROL":   "Ecopetrol",
    "ANDINABCO":   "Embotelladora Andina S.A. Serie B",
    "ENTELCO":     "Empresa Nacional de Telecomunicaciones S.A.",
    "CMPCCO":      "Empresas CMPC S.A.",
    "COPECCO":     "Empresas Copec S.A.",
    "ENELAMCO":    "Enel Américas SA",
    "ENELCHILCO":  "Enel Chile S.A.",
    "ECLCO":       "Engie Energía Chile S.A.",
    "ENKA":        "Enka de Colombia S.A.",
    "ETB":         "Etb",
    "ICHN":        "iShares MSCI China UCITS ETF USD (Acc)",
    "EXITO":       "Éxito S.A.",
    "FALABELLCO":  "Falabella SA",
    "FERREYC1CO":  "Ferreycorp S.A.A.",
    "F":           "Ford",
    "GEHC":        "GE HealthCare Technologies Inc.",
    "GE":          "General Electric Company",
    "COPX":        "Global X Copper Miners ETF",
    "LIT":         "Global X Lithium & Battery Tech ETF",
    "GXTESCOL":    "Global X Tes Colombia ETF",
    "URA":         "Global X Uranium ETF",
    "GRUPOARGOS":  "Grupo Argos",
    "PFGRUPOARG":  "Grupo Argos Preferencial",
    "GRUPOAVAL":   "Grupo Aval",
    "GRUBOLIVAR":  "Grupo Bolívar",
    "CIBEST":      "Grupo Cibest",
    "PFCIBEST":    "Grupo Cibest Preferencial",
    "GEB":         "Grupo Energía de Bogotá",
    "NUTRESA":     "Grupo Nutresa",
    "GRUPOSURA":   "Grupo Suramericana",
    "PFGRUPOSURA": "Grupo Suramericana Preferencial",
    "PFGRUPSURA":  "Grupo Suramericana Preferencial",
    "HCOLSEL":     "Hcolsel",
    "HIVECO":      "HIVE Digital Technologies",
    "ICOLPCAP":    "Icolcap",
    "ICOLCAP":     "Icolcap",
    "INRETC1CO":   "InRetail Peru Corp",
    "IFSCO":       "Intercorp Financial Services Inc.",
    "IAMCO":       "Inversiones Aguas Metropolitanas S.A.",
    "IPCHBC1CO":   "Inversiones Portuarias Chancay S.A.A.",
    "EQAC":        "Invesco EQQQ Nasdaq-100 UCITS ETF",
    "SGLD":        "Invesco Physical Gold ETC",
    "ISA":         "Isa",
    "IUIT":        "iShare S&P 500 Tech",
    "IB01":        "iShare US Treas 0.1 YR USD A",
    "LQDA":        "iShares $ Corp Bond UCITS ETF",
    "SDIA":        "iShares $ Short Duration Corp Bond UCITS",
    "CBU7":        "iShares $ Treasury Bond 3-7yr UCITS ETF",
    "RBOT":        "iShares Automation & Robotics UCITS",
    "IBIT":        "iShares Bitcoin Trust",
    "IJPA":        "iShares Core MSCI Japan IMI UCITS ETF USD Acc",
    "IWVL":        "iShares Edge MSCI World Value Fact UCITS",
    "INRA":        "iShares Global Clean Energy UCITS ETF USD (Acc)",
    "D26ACO":      "iShares iBonds Dec 2026 Term $ Corp UCITS ETF",
    "ID27CO":      "iShares iBonds Dec 2027 Term $ Corp UCITS ETF",
    "D28ACO":      "iShares iBonds Dec 2028 Term $ Corp UCITS ETF",
    "ID29CO":      "iShares iBonds Dec 2029 Term $ Corp UCITS ETF",
    "ID30CO":      "iShares iBonds Dec 2030 Term $ Corp UCITS ETF",
    "EMGA":        "iShares J.P. Morgan EM Local Govt Bond UCITS ETF",
    "ISAC":        "iShares MSCI ACWI",
    "4BRZ":        "iShares MSCI Brazil UCITS ETF",
    "IDSE":        "iShares MSCI Europe SRI UCITS ETF USD (Acc)",
    "SUAS":        "iShares MSCI USA SRI",
    "I500CO":      "iShares S&P 500 Colombia",
    "IUES":        "iShares S&P 500 Energy Sector UCITS (Acc)",
    "IUFS":        "iShares S&P 500 Financials",
    "IUHC":        "iShares SP 500 Health Care Sector UCITS (Acc)",
    "CFMITNIPCO":  "IT NOW S&P IPSA",
    "ITAUCLCO":    "Itaú Corpbanca",
    "JPEA":        "J. P. Morgan USD EM Bond",
    "JNJ":         "Johnson & Johnson",
    "JPM":         "JPMorgan Chase & Co",
    "LTMCO":       "Latam",
    "META":        "Meta Platforms, Inc.",
    "MSFTCO":      "Microsoft Corp",
    "MINEROS":     "Mineros",
    "NKE":         "Nike, Inc.",
    "NUAMCO":      "Nuam Exchange",
    "NU":          "Nubank",
    "NVDA":        "Nvidia Corporation",
    "PARAUCOCO":   "Parque Arauco S.A.",
    "PEI":         "Patrimonio Autónomo Estrategias Inmobiliarias",
    "PBR":         "Petróleo Brasileiro S.A",
    "PFE":         "Pfizer",
    "MALLPLAZCO":  "Plaza S.A.",
    "PROMIGAS":    "Promigas",
    "QUINENCOCO":  "Quiñenco S.A.",
    "RIPLEYCO":    "Ripley Corporación S.A.",
    "BSANTANDCO":  "Santander Chile Holding S.A.",
    "SMUCO":       "SMU S.A.",
    "CVERDEC1CO":  "Sociedad Minera Cerro Verde S.A.",
    "PORT":        "Sociedad Portafolio",
    "SQMBCO":      "Sociedad Química y Minera de Chile",
    "SCCOCO":      "Southern Copper Corp",
    "SUM":         "Summit Materials",
    "TERPEL":      "Terpel",
    "TSLACO":      "Tesla, Inc.",
    "KOCO":        "The Coca-Cola Company",
    "JETS":        "The U.S. Global Jets ETF",
    "TIN":         "Títulos Inmobiliarios TIN",
    "GOAUCO":      "U.S. Global GO GOLD",
    "UBER":        "Uber",
    "SDHA":        "USD Corp Bond UCITS ETF",
    "GDXCO":       "VanEck Gold Miners ETF",
    "SMHCO":       "VanEck Semiconductor ETF",
    "VOO":         "Vanguard 500 Index Fund ETF",
    "CONCHATOCO":  "Viña Concha y Toro S.A.",
    "VOLCABC1CO":  "Volcan Compañía Minera S.A.A.",
}


def _get_nombre_colombia(ticker: str) -> str | None:
    """Nombre desde dict estático. Normaliza punto (BRK.B→BRKB).
    Si el ticker termina en 'CO', prueba también sin el sufijo."""
    t = ticker.strip().upper().replace(".", "")
    if t in NOMBRES_COLOMBIA:
        return NOMBRES_COLOMBIA[t]
    if len(t) > 2 and t.endswith("CO") and t[:-2] in NOMBRES_COLOMBIA:
        return NOMBRES_COLOMBIA[t[:-2]]
    return None


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


# ── Tasa de cambio {moneda}->COP via TradingView Overview (FX_IDC) ────────────
def _get_fx_rate_to_cop(currency: str, cache: dict) -> float | None:
    """Tasa {currency}->COP. Cachea por moneda dentro de la misma ejecución."""
    currency = (currency or "COP").strip().upper()
    if currency == "COP":
        return 1.0
    if currency in cache:
        return cache[currency]

    rate = None
    try:
        overview = Overview()
        result = overview.get_symbol_overview(symbol=f"FX_IDC:{currency}COP")
        if result.get("status") == "success":
            close = result["data"].get("close")
            if close:
                rate = round(float(close), 4)
    except Exception:
        rate = None

    cache[currency] = rate
    return rate


# ── Fetch TradingView Colombia (LEGACY — reemplazado por boletín oficial BVC) ─
# Se deja comentado en vez de borrarse por si hay que revertir. El calendario de
# dividendos ahora viene de fetch_bvc_colombia(); TV solo se sigue usando arriba
# en _get_bvc_prices()/_get_fx_rate_to_cop() para precio y tasa de cambio.
#
# def fetch_tv_colombia(tc: float) -> list[dict]:
#     now   = datetime.datetime.now(tz=datetime.timezone.utc)
#     today = now.replace(hour=0, minute=0, second=0, microsecond=0)
#     ts_from = int((today - datetime.timedelta(weeks=4)).timestamp())
#     ts_to   = int((today + datetime.timedelta(weeks=8, seconds=86399)).timestamp())
#
#     raw = CalendarScraper().scrape_dividends(
#         timestamp_from=ts_from,
#         timestamp_to=ts_to,
#         markets=["colombia"],
#     )
#
#     seen: dict[tuple, dict] = {}
#     for ev in raw:
#         ex_date = _ts_to_date(ev.get("dividend_ex_date_upcoming")) or \
#                   _ts_to_date(ev.get("dividend_ex_date_recent"))
#         if not ex_date:
#             continue
#         full_sym = ev.get("full_symbol", "")
#         ticker   = full_sym.split(":")[-1]
#         if not _in_whitelist(ticker):
#             continue
#         key = (full_sym, ex_date)
#         if key in seen:
#             continue
#         amount   = ev.get("dividend_amount_upcoming") or ev.get("dividend_amount_recent")
#         currency = ev.get("fundamental_currency_code", "USD")
#         monto_cop = _to_cop(amount, currency, tc)
#         seen[key] = {
#             "symbol"         : full_sym,
#             "nombre"         : _get_nombre_colombia(ticker) or ev.get("name") or ev.get("description"),
#             "fuente"         : "TV",
#             "fecha_corte"    : ex_date,
#             "fecha_pago"     : _ts_to_date(ev.get("dividend_payment_date_upcoming")) or
#                                _ts_to_date(ev.get("dividend_payment_date_recent")),
#             "monto_original" : amount,
#             "moneda_original": currency,
#             "tc_usdcop"      : tc if currency == "USD" else None,
#             "monto_cop"      : monto_cop,
#             "tipo"           : "efectivo",
#             "en_partes"      : False,
#             "concepto"       : None,
#             "yield_tv_pct"   : ev.get("dividends_yield"),
#         }
#     rows = list(seen.values())
#
#     # Para los sin yield en TV, calcular con precio COP de Overview
#     sin_yield = [
#         r["symbol"].split(":")[-1]
#         for r in rows
#         if r["yield_tv_pct"] is None and r["monto_cop"]
#     ]
#     if sin_yield:
#         precios = _get_bvc_prices(sin_yield)
#         for r in rows:
#             if r["yield_tv_pct"] is None and r["monto_cop"]:
#                 sym_short = r["symbol"].split(":")[-1]
#                 precio = precios.get(sym_short)
#                 if precio and precio > 0:
#                     r["yield_tv_pct"] = round(r["monto_cop"] / precio * 100, 6)
#
#     return rows


# ── Boletín oficial BVC: "Fechas Exdividendo" (CMS Hygraph -> XLSX) ───────────
BVC_HYGRAPH_URL = "https://us-east-1-bolsa-co.cdn.hygraph.com/content/ckdolgg6k07rc01xnc22d25r1/master"
BVC_EXDIVIDEND_CATEGORY_ID = "ckgp9xu6g2ddw098110jscm0f"

# Token público de solo-lectura embebido en el bundle JS del sitio de BVC (no es
# secreto: se envía al navegador de cualquier visitante). Se usa como fast-path;
# si BVC lo rota, _discover_hygraph_token() lo vuelve a extraer del sitio en
# caliente, así que nunca hay que actualizarlo a mano. El valor de arranque
# puede overridearse por env si se quiere fijar uno propio.
_hygraph_token_cache: dict[str, str | None] = {
    "token": os.getenv(
        "BVC_HYGRAPH_TOKEN",
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImdjbXMtbWFpbi1wcm9kdWN0aW9uIn0."
        "eyJ2ZXJzaW9uIjozLCJpYXQiOjE2Mzk2ODQ5NDUsImF1ZCI6WyJodHRwczovL2FwaS11cy1lYXN0LTEtYm9sc2EtY28uZ3JhcGhjbXMuY29tL3YyL2NrZG9sZ2c2azA3cmMwMXhuYzIyZDI1cjEvbWFzdGVyIiwiaHR0cHM6Ly9tYW5hZ2VtZW50LW5leHQuZ3JhcGhjbXMuY29tIl0sImlzcyI6Imh0dHBzOi8vbWFuYWdlbWVudC5ncmFwaGNtcy5jb20vIiwic3ViIjoiMmNmMzY5ZTMtNWYwMS00YjUwLThhNGMtZTM3YmQxNDI4ZGYwIiwianRpIjoiY2tpcDdjaWhxODdsNDAxejEwcHplOTI4byJ9."
        "ZFDpgyyGMnav1J6BRVt_ZT43vLFzQgf-iWddP2BmzgjCm1-zx_qZFMIRMo0q7TRqDgFWhpQIt2Xuku0ens8KfvdkaPpnkeqzeZYufXeIjpXgyF_nF0tXsZjN3eSm-LkLYQK65dcJsA1UwJJjUu9wk1i-sDjnBU2LiXhFc6XCMXoH912cG3eb9sCwWatodMrkrV4qgK-zdKU2nc3FGJwL2X-lUtwdvnmKhRmLbnAzTmi4pLlog7KWYof5Syk44ysYF3stThRb8uJA580Wgcw7WEFOSJerpvdvnGPxHNYudSJdxQ2kF4SchJUnohUNdrSkmAgkogtWy-Vs1uB7Px03b4QhjjxYMTnocoTY_0a7r1pulvi0vtp_foOD-XgPlR1qoza6g9LW1KLJ39gBVv6SD_TLZ4j94HvR3iloXN8iIta_KGS4zXHg10ay6ZI1SXvomSbHxaOzZXclk1yWZDv76n1ZbwDWDfRkgf4figWLKqJCenL-_uIdXBe3lnD8odBLDqvQ_BM-We2MrCAPWzGC2Vo_fIpyYYDsS8h4AUZw3m3E7w1j_61fFJOIIRDpmSA49KA9Dy4hlO-eLQVvTPUWw-Tn6QAfZDrc-slr_EgjTMJg0KCP4e3NYlDPxWmbQKUzErZj_GwDp85ezaCJTFapCy1A2Ax1CVirdk88TbjoqJE",
    )
}

_APP_CHUNK_RE = re.compile(r'/_next/static/chunks/pages/_app-[a-zA-Z0-9]+\.js')
_TOKEN_NEAR_RE = re.compile(r'cdn\.hygraph\.com[^"]*"[^}]*?content:"([^"]+)"')


def _discover_hygraph_token() -> str | None:
    """Extrae en caliente el token público de Hygraph desde el chunk _app de bvc.com.co
    (se carga en toda la web, no solo en /informes-y-boletines). Self-healing: si BVC
    rota el token, esto lo vuelve a encontrar sin tocar código ni variables de entorno."""
    try:
        home = http.get(
            "https://www.bvc.com.co/",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=15,
        )
        home.raise_for_status()
        chunk_match = _APP_CHUNK_RE.search(home.text)
        if not chunk_match:
            return None

        chunk = http.get(
            f"https://www.bvc.com.co{chunk_match.group(0)}",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.bvc.com.co/",
            },
            timeout=15,
        )
        chunk.raise_for_status()
        token_match = _TOKEN_NEAR_RE.search(chunk.text)
        return token_match.group(1) if token_match else None
    except Exception:
        return None


def _hygraph_query(query: str, variables: dict, operation_name: str) -> dict:
    """POST a Hygraph con el token cacheado. Si falla por auth (401 o sin data),
    redescubre el token desde el sitio y reintenta una vez antes de fallar."""
    payload = {"query": query, "variables": variables, "operationName": operation_name}

    def _post(token: str | None):
        return http.post(
            BVC_HYGRAPH_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=20,
        )

    r = _post(_hygraph_token_cache["token"])
    auth_failed = r.status_code in (401, 403) or "errors" in r.json()
    if auth_failed:
        fresh_token = _discover_hygraph_token()
        if fresh_token and fresh_token != _hygraph_token_cache["token"]:
            _hygraph_token_cache["token"] = fresh_token
            r = _post(fresh_token)

    r.raise_for_status()
    body = r.json()
    if "errors" in body:
        raise RuntimeError(f"Hygraph (BVC) rechazó la consulta: {body['errors']}")
    return body["data"]


def _fetch_bvc_bulletin_meta() -> dict:
    """Consulta el CMS de BVC y devuelve el boletín vigente de Fechas Exdividendo (fileName + url)."""
    query = (
        "query ReportsAndBulletinsByCategoryAndDate($categoryId: ID!, $locales: [Locale!]!) {"
        "  pdReportsAndBulletins(where: {category: {id: $categoryId}}, stage: PUBLISHED, "
        "    locales: $locales, orderBy: date_DESC, first: 1) {"
        "    date title attached { fileName url }"
        "  }"
        "}"
    )
    data = _hygraph_query(
        query,
        {"categoryId": BVC_EXDIVIDEND_CATEGORY_ID, "locales": ["es_CO"]},
        "ReportsAndBulletinsByCategoryAndDate",
    )
    reports = data["pdReportsAndBulletins"]
    if not reports:
        raise RuntimeError("BVC no tiene publicado el boletín de Fechas Exdividendo")
    return reports[0]["attached"]


def _download_bvc_bulletin() -> bytes:
    meta = _fetch_bvc_bulletin_meta()
    r = http.get(meta["url"], timeout=30)
    r.raise_for_status()
    return r.content


def _norm_header(value) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split()).strip().upper()


def _cell_to_date(value) -> str | None:
    """Convierte celda de fecha (datetime o serial de Excel) a 'YYYY-MM-DD'."""
    if value is None or value == "" or value == "-":
        return None
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, (int, float)):
        try:
            return (_EXCEL_EPOCH + datetime.timedelta(days=float(value))).isoformat()
        except (OverflowError, ValueError):
            return None
    return None


def _find_bvc_header_row(ws) -> tuple[int, dict[str, int]]:
    """Ubica la fila de headers en español (contiene NEMOTECNICO) y mapea columna->índice.
    El layout de columnas varía por año, por eso se busca por nombre y no por índice fijo."""
    for row in ws.iter_rows(min_row=1, max_row=15):
        values = [_norm_header(c.value) for c in row]
        if "NEMOTECNICO" not in values:
            continue
        col: dict[str, int] = {}
        for idx, v in enumerate(values):
            if v == "EMISOR":
                col["emisor"] = idx
            elif v == "NEMOTECNICO":
                col["ticker"] = idx
            elif v == "MODO DE PAGO":
                col["modo_pago"] = idx
            elif v == "MONEDA":
                col["moneda"] = idx
            elif v in {"FECHA INICIAL EX-DIVIDENDO", "FECHA INICIAL"}:
                col["fecha_ex"] = idx
            elif v in {"FECHA FINAL EX-DIVIDENDO", "FECHA FINAL Y DE PAGO", "FECHA FINAL"}:
                col["fecha_ex_final"] = idx
            elif v == "FECHA DE PAGO":
                col["fecha_pago"] = idx
            elif v == "VALOR TOTAL DEL DIVIDENDO":
                col["valor_total"] = idx
            elif v == "VALOR CUOTA":
                col["valor_cuota"] = idx
            elif v == "DESCRIPCION PAGO PDU":
                col["descripcion"] = idx
        return row[0].row, col
    raise RuntimeError("No se encontró la fila de headers (NEMOTECNICO) en el boletín BVC")


def _parse_bvc_month(xlsx_bytes: bytes, year: int, month: int) -> list[dict]:
    """Lee la hoja del año y devuelve filas cuya fecha ex-dividendo cae en ese mes completo."""
    wb = load_workbook(io.BytesIO(xlsx_bytes), data_only=True, read_only=True)
    sheet_name = f"FECHAS EX-DIVIDENDO {year}"
    if sheet_name not in wb.sheetnames:
        wb.close()
        return []

    ws = wb[sheet_name]
    header_row, col = _find_bvc_header_row(ws)
    if "ticker" not in col or "fecha_ex" not in col:
        wb.close()
        raise RuntimeError(f"Headers inesperados en la hoja '{sheet_name}' del boletín BVC")

    month_start = datetime.date(year, month, 1)
    month_end = datetime.date(year, month, calendar.monthrange(year, month)[1])
    fecha_pago_idx = col.get("fecha_pago", col.get("fecha_ex_final"))

    rows: list[dict] = []
    # +2: la hoja tiene header en español seguido de header en inglés antes de los datos
    for row in ws.iter_rows(min_row=header_row + 2):
        values = [c.value for c in row]

        ticker = values[col["ticker"]] if col["ticker"] < len(values) else None
        if not ticker or not str(ticker).strip():
            continue
        ticker = str(ticker).strip().upper()
        if not _in_whitelist(ticker):
            continue

        fecha_ex = _cell_to_date(values[col["fecha_ex"]]) if col["fecha_ex"] < len(values) else None
        if not fecha_ex:
            continue
        fecha_ex_dt = datetime.date.fromisoformat(fecha_ex)
        if not (month_start <= fecha_ex_dt <= month_end):
            continue

        monto = None
        if col.get("valor_total") is not None and col["valor_total"] < len(values):
            monto = values[col["valor_total"]]
        if monto is None and col.get("valor_cuota") is not None and col["valor_cuota"] < len(values):
            monto = values[col["valor_cuota"]]
        try:
            monto = float(monto)
        except (TypeError, ValueError):
            continue

        emisor = values[col["emisor"]] if col.get("emisor") is not None and col["emisor"] < len(values) else None
        moneda = values[col["moneda"]] if col.get("moneda") is not None and col["moneda"] < len(values) else "COP"
        modo_pago = values[col["modo_pago"]] if col.get("modo_pago") is not None and col["modo_pago"] < len(values) else None
        descripcion = values[col["descripcion"]] if col.get("descripcion") is not None and col["descripcion"] < len(values) else None
        fecha_pago = _cell_to_date(values[fecha_pago_idx]) if fecha_pago_idx is not None and fecha_pago_idx < len(values) else None

        rows.append({
            "ticker"     : ticker,
            "emisor"     : str(emisor).strip() if emisor else None,
            "moneda"     : str(moneda).strip().upper() if moneda else "COP",
            "modo_pago"  : str(modo_pago).strip() if modo_pago else None,
            "fecha_ex"   : fecha_ex,
            "fecha_pago" : fecha_pago,
            "monto"      : monto,
            "descripcion": str(descripcion).strip() if descripcion else None,
        })

    wb.close()
    return rows


def fetch_bvc_colombia() -> list[dict]:
    """Dividendos del mes calendario actual desde el boletín oficial BVC.
    El yield se calcula con precio de TradingView Overview (único uso restante de TV)."""
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    xlsx_bytes = _download_bvc_bulletin()
    raw_rows = _parse_bvc_month(xlsx_bytes, now.year, now.month)

    fx_cache: dict[str, float | None] = {}
    seen: dict[tuple, dict] = {}
    for r in raw_rows:
        tc = _get_fx_rate_to_cop(r["moneda"], fx_cache)
        monto_cop = round(r["monto"] * tc, 2) if tc is not None else None
        full_sym = f"BVC:{r['ticker']}"
        key = (full_sym, r["fecha_ex"])
        if key in seen:
            continue
        seen[key] = {
            "symbol"         : full_sym,
            "nombre"         : _get_nombre_colombia(r["ticker"]) or r["emisor"],
            "fuente"         : "BVC",
            "fecha_corte"    : r["fecha_ex"],
            "fecha_pago"     : r["fecha_pago"],
            "monto_original" : r["monto"],
            "moneda_original": r["moneda"],
            "tc_usdcop"      : tc if r["moneda"] != "COP" else None,
            "monto_cop"      : monto_cop,
            "tipo"           : "efectivo" if r["modo_pago"] and "EFECTIVO" in r["modo_pago"].upper() else (r["modo_pago"] or "efectivo"),
            "en_partes"      : False,
            "concepto"       : r["descripcion"],
            "yield_tv_pct"   : None,
        }
    rows = list(seen.values())

    # Yield vía precio de TradingView Overview (BVC no publica precio/yield en el boletín)
    tickers = [r["symbol"].split(":")[-1] for r in rows if r["monto_cop"]]
    if tickers:
        precios = _get_bvc_prices(tickers)
        for r in rows:
            if r["monto_cop"]:
                precio = precios.get(r["symbol"].split(":")[-1])
                if precio and precio > 0:
                    r["yield_tv_pct"] = round(r["monto_cop"] / precio * 100, 6)

    return rows


# ── Preview ───────────────────────────────────────────────────────────────────
def get_preview() -> dict:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    rows = fetch_bvc_colombia()

    return {
        "fecha_preview" : now.strftime("%Y-%m-%d %H:%M UTC"),
        "mes_consultado": now.strftime("%Y-%m"),
        "resumen": {
            "bvc_total" : len(rows),
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
