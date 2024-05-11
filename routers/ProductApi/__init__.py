from fastapi import APIRouter

from .GetProductCategoryApi import router as get_product_category_router

product_api_router = APIRouter(prefix="/product")
product_api_router.include_router(get_product_category_router)
