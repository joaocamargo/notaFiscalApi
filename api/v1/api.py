from fastapi import APIRouter

from api.v1.endpoints import notafiscal

api_router = APIRouter()

api_router.include_router(notafiscal.router, prefix='/notafiscal', tags=['notafiscal'])
