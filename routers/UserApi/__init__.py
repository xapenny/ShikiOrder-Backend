from fastapi import APIRouter

from .GetUserInfoApi import router as get_user_info_router
from .UserLoginApi import router as get_user_token_router

user_api_router = APIRouter(prefix="/user")
user_api_router.include_router(get_user_info_router)
user_api_router.include_router(get_user_token_router)
