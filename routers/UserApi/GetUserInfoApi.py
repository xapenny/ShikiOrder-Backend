from models.UserInfoModel import UserBasicInfoModel
from fastapi import APIRouter, Depends
from dependencies import get_current_active_user

router = APIRouter()


@router.get("/info", response_model=UserBasicInfoModel)
async def getUserBasicInfoApi(
        current_user: UserBasicInfoModel = Depends(get_current_active_user)):
    return current_user
