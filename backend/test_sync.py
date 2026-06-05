"""
Script de debugging para probar el sync a Supabase directamente.
Ejecutar desde backend/: python test_sync.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL         = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY         = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TABLE                = "dividendos_peru"

key = SUPABASE_SERVICE_KEY or SUPABASE_KEY
print(f"URL   : {SUPABASE_URL}")
print(f"KEY   : {key[:30]}..." if key else "KEY   : None")
print(f"MODO  : {'service_role' if SUPABASE_SERVICE_KEY else 'anon'}")
print()

if not SUPABASE_URL or not key:
    print("ERROR: Faltan credenciales en .env")
    exit(1)

headers = {
    "apikey"       : key,
    "Authorization": f"Bearer {key}",
    "Content-Type" : "application/json",
    "Prefer"       : "resolution=merge-duplicates,return=representation",
}

payload = [
    {
        "symbol"         : "BVL:TEST_DEBUG",
        "nombre"         : "TEST_DEBUG",
        "fuente"         : "TV",
        "fecha_corte"    : "2026-06-05",
        "fecha_pago"     : "2026-06-23",
        "monto_original" : 1.0,
        "moneda_original": "USD",
        "tc_usdpen"      : 3.4425,
        "monto_pen"      : 3.4425,
        "tipo"           : "efectivo",
        "en_partes"      : False,
        "concepto"       : None,
        "yield_tv_pct"   : 1.0,
    }
]

url = f"{SUPABASE_URL}/rest/v1/{TABLE}"
print(f"POST -> {url}")
print(f"Payload: {payload[0]['symbol']}")
print()

r = requests.post(url, json=payload, headers=headers, timeout=15)

print(f"Status : {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Body   : {r.text[:500] if r.text else '(vacío)'}")
print()

if r.status_code in (200, 201, 204):
    print("✅ INSERT OK — el registro debería estar en Supabase")
else:
    print("❌ FALLÓ — revisar error arriba")
