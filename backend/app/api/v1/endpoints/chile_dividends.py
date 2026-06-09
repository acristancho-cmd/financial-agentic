"""
Endpoints de dividendos Chile con revisión humana antes de persistir.
GET  /api/v1/dividends/chile/preview  → corre scraper TV, devuelve datos para revisar
POST /api/v1/dividends/chile/sync     → recibe los datos revisados y guarda en Supabase
"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chile_dividends_service import get_preview, sync_to_supabase

router = APIRouter(tags=["dividends-chile"])


class SyncPayload(BaseModel):
    dividendos: List[dict] = []


@router.get("/chile/preview")
async def preview_chile_dividends():
    """
    Obtiene dividendos de Chile desde TradingView (BCS) sin guardar nada.

    - Ventana: hoy - 4 semanas → hoy + 8 semanas
    - Cubre acciones locales, internacionales con sufijo CL y fondos CFI

    El frontend puede editar los datos antes de enviar a /sync.
    """
    try:
        return get_preview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chile/sync")
async def sync_chile_dividends(payload: SyncPayload):
    """
    Guarda en Supabase los datos revisados por el usuario.

    Usa UPSERT: inserta nuevos, actualiza TC y yield en existentes.
    Clave única: (symbol, fecha_corte, fuente) — sin duplicados.
    """
    try:
        result = sync_to_supabase(rows=payload.dividendos)
        return {
            "status"         : "ok" if not result["errores"] else "parcial",
            "guardados"      : result["guardados"],
            "errores"        : result["errores"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
