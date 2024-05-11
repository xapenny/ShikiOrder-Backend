from fastapi import APIRouter

from .UserApi import user_api_router
from .ProductApi import product_api_router

base_api_router = APIRouter(prefix="/shiki-api/v1")
base_api_router.include_router(user_api_router)
base_api_router.include_router(product_api_router)
