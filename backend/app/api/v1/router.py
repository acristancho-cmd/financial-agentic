from fastapi import APIRouter
from app.api.v1.endpoints.peru_dividends import router as peru_router
from app.api.v1.endpoints.colombia_dividends import router as colombia_router
from app.api.v1.endpoints.chile_dividends import router as chile_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(peru_router, prefix="/dividends")
api_router.include_router(colombia_router, prefix="/dividends")
api_router.include_router(chile_router, prefix="/dividends")
