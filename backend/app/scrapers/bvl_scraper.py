"""
Scraper de Entrega de Derechos (dividendos locales) de BVL.
Fuente: https://documents.bvl.com.pe/empresas/entrder1.htm
HTML estático — solo requests + BeautifulSoup, sin browser.
"""
import re
import datetime
import requests
from bs4 import BeautifulSoup
from typing import Optional

BVL_URL = "https://documents.bvl.com.pe/empresas/entrder1.htm"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ── Parseo del campo "Derechos" ───────────────────────────────────────────────
_RE_SOLES = re.compile(r"S/\s*([\d,\.]+)\s*Efe\.", re.IGNORECASE)
_RE_USD   = re.compile(r"US\$\s*([\d,\.]+)\s*Efe\.", re.IGNORECASE)
_RE_PCT   = re.compile(r"([\d,\.]+)\s*%\s*Accs?\.", re.IGNORECASE)
_RE_ACCS  = re.compile(r"([\d,\.]+)\s*Accs?\.\s*x\s*Acci[oó]n", re.IGNORECASE)


def _num(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", ""))
    except Exception:
        return None


def _parse_derechos(raw: str) -> dict:
    raw = raw.strip()

    m = _RE_SOLES.search(raw)
    if m:
        return {"amount": _num(m.group(1)), "currency": "PEN", "tipo": "efectivo"}

    m = _RE_USD.search(raw)
    if m:
        return {"amount": _num(m.group(1)), "currency": "USD", "tipo": "efectivo"}

    m = _RE_PCT.search(raw)
    if m:
        return {"amount": _num(m.group(1)), "currency": None, "tipo": "acciones_pct"}

    m = _RE_ACCS.search(raw)
    if m:
        return {"amount": _num(m.group(1)), "currency": None, "tipo": "acciones_ratio"}

    return {"amount": None, "currency": None, "tipo": "desconocido"}


def _parse_fecha(s: str) -> Optional[str]:
    s = s.strip()
    if not s or s.lower() in ("en partes", "—", "-", ""):
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def scrape_bvl_dividends(timeout: int = 15) -> list[dict]:
    """
    Descarga y parsea la tabla de Entrega de Derechos de BVL.
    Retorna lista de dicts normalizados.
    """
    try:
        resp = requests.get(BVL_URL, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "latin-1"
    except Exception as e:
        raise RuntimeError(f"BVL no disponible: {e}") from e

    soup = BeautifulSoup(resp.text, "html.parser")

    # Buscar la tabla principal
    table = soup.find("table")
    if not table:
        print("  [BVL scraper] No se encontró tabla en el HTML")
        return []

    results = []
    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        texts = [c.get_text(separator=" ", strip=True) for c in cells]

        symbol = texts[0].strip()

        # Filtrar filas no-dato: encabezados, leyendas y basura
        # Un símbolo válido es corto, sin espacios y alfanumérico
        if not symbol:
            continue
        if " " in symbol:
            continue
        if len(symbol) > 15:
            continue
        if symbol.lower() in ("valor", "emisor", "entrega"):
            continue
        derechos_raw      = texts[1].strip()
        concepto          = texts[2].strip()
        fecha_acuerdo     = _parse_fecha(texts[3])
        fecha_corte       = _parse_fecha(texts[4])   # ex-date
        fecha_registro    = _parse_fecha(texts[5])
        fecha_entrega_raw = texts[6].strip()
        fecha_entrega     = _parse_fecha(fecha_entrega_raw)
        en_partes         = "partes" in fecha_entrega_raw.lower()

        parsed = _parse_derechos(derechos_raw)

        if not symbol:
            continue

        results.append({
            "symbol"              : symbol,
            "fuente"              : "BVL",
            "derechos_raw"        : derechos_raw,
            "concepto"            : concepto,
            "fecha_acuerdo"       : fecha_acuerdo,
            "fecha_corte"         : fecha_corte,
            "fecha_registro"      : fecha_registro,
            "fecha_entrega"       : fecha_entrega,
            "fecha_entrega_parcial": en_partes,
            "amount"              : parsed["amount"],
            "currency"            : parsed["currency"],
            "tipo"                : parsed["tipo"],
        })

    return results
