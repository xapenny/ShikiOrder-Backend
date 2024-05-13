from models.UserInfoModel import UserBasicInfoModel, UpdateUserInfoRequestModel
from fastapi import APIRouter, Depends, Response, status
from dependencies import get_current_active_user
from database.models.UserInfo import UserInfoDb

router = APIRouter()


@router.post("/update")
async def updateUserInfo(
    request: UpdateUserInfoRequestModel,
    response: Response,
    current_user: UserBasicInfoModel = Depends(get_current_active_user)):

    # Validate request data
    if request.nickname == None or request.nickname == "":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "昵称不能为空"}
    if request.phone < 13000000000 or request.phone > 19899999999:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "手机号格式错误"}

    # Update user info
    await UserInfoDb.update_user_info(open_id=current_user.open_id,
                                      nickname=request.nickname,
                                      phone=request.phone,
                                      gender=request.gender)
    return {"message": "更新用户信息成功"}
