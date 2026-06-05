"""
Endpoints de dividendos Colombia.
GET  /api/v1/dividends/colombia/preview  -> scraper TV, devuelve datos para revisar
POST /api/v1/dividends/colombia/sync     -> recibe datos revisados y guarda en Supabase
"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.colombia_dividends_service import get_preview, sync_to_supabase

router = APIRouter(tags=["dividends-colombia"])


class SyncPayload(BaseModel):
    dividendos: List[dict] = []


@router.get("/colombia/preview")
async def preview_colombia_dividends():
    try:
        return get_preview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/colombia/sync")
async def sync_colombia_dividends(payload: SyncPayload):
    try:
        result = sync_to_supabase(payload.dividendos)
        return {
            "status"   : "ok" if not result["errores"] else "parcial",
            "guardados": result["guardados"],
            "errores"  : result["errores"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
