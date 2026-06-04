"""
Endpoints de dividendos Peru con revisión humana antes de persistir.
GET  /api/v1/dividends/peru/preview  → corre scrapers, devuelve datos para revisar
POST /api/v1/dividends/peru/sync     → recibe los datos revisados y guarda en Supabase
"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.peru_dividends_service import get_preview, sync_to_supabase

router = APIRouter(tags=["dividends-peru"])


class SyncPayload(BaseModel):
    tradingview: List[dict] = []
    bvl: List[dict] = []


@router.get("/peru/preview")
async def preview_peru_dividends():
    """
    Obtiene dividendos de Peru desde TradingView y BVL.com.pe sin guardar nada.

    - TV  : ventana hoy - 4 semanas → hoy + 8 semanas
    - BVL : lista completa declarada (sin filtro de fecha)

    El frontend puede editar los datos antes de enviar a /sync.
    """
    try:
        return get_preview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/peru/sync")
async def sync_peru_dividends(payload: SyncPayload):
    """
    Guarda en Supabase los datos revisados (y opcionalmente editados) por el usuario.

    Recibe el mismo formato que devuelve /preview.
    Usa UPSERT: inserta nuevos, actualiza TC y yield en existentes.
    Clave única: (symbol, fecha_corte, fuente) — sin duplicados.
    """
    try:
        result = sync_to_supabase(
            tv_rows  = payload.tradingview,
            bvl_rows = payload.bvl,
        )
        return {
            "status"         : "ok" if not result["errores"] else "parcial",
            "tv_guardados"   : result["tv"],
            "bvl_guardados"  : result["bvl"],
            "total_guardados": result["tv"] + result["bvl"],
            "errores"        : result["errores"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
