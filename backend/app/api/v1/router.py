from fastapi import APIRouter
from app.api.v1.endpoints.peru_dividends import router as peru_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(peru_router, prefix="/dividends")
