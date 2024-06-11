from fastapi import APIRouter

from .UserApi import router as user_api_router
from .OrderApi import router as order_api_router
from .ProductApi import router as product_api_router
from .ShopApi import router as shop_api_router
from .AdminApi import router as admin_api_router
from .PointShopApi import router as point_shop_api_router
from .CouponApi import router as coupon_api_router

base_api_router = APIRouter(prefix="/shiki-api/v1")
base_api_router.include_router(user_api_router)
base_api_router.include_router(product_api_router)
base_api_router.include_router(order_api_router)
base_api_router.include_router(shop_api_router)
base_api_router.include_router(admin_api_router)
base_api_router.include_router(point_shop_api_router)
base_api_router.include_router(coupon_api_router)
