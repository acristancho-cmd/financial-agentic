"""
Router principal de la API v1
Agrupa todos los endpoints de la versión 1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import dividends

api_router = APIRouter(prefix="/api/v1")

# Incluir routers de cada funcionalidad
api_router.include_router(dividends.router)


