from datetime import timedelta, datetime

from fastapi import APIRouter, Response, status, Depends

from dependencies import (ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token,
                          get_wc_code2session, get_current_active_user)
from models.UserLoginModel import UserLoginRequestModel
from database.models.UserInfo import UserInfoDb
from models.UserInfoModel import UserBasicInfoModel, UpdateUserInfoRequestModel

router = APIRouter(prefix='/user')


@router.post("/login")
async def login_for_access_token(response: Response,
                                 request: UserLoginRequestModel):
    code2session = await get_wc_code2session(request.code)
    if code2session is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "登录失败: 0"}
    elif isinstance(code2session, str):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "登录失败: " + code2session}
    open_id = code2session.get("openid")
    session_key = code2session.get("session_key")
    if open_id is None or session_key is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "登录失败: 1"}

    user = await UserInfoDb.get_user_by_open_id(open_id)
    if user is None:
        user = await UserInfoDb.add_user(open_id=open_id,
                                         avatar=request.avatar,
                                         total_points=0,
                                         level_exp=0,
                                         nickname=request.nickname)
    if not user:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "登录失败: 2"}
    await UserInfoDb.update_user_info(open_id=open_id, session_key=session_key)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={
        "open_id": open_id,
        "session_key": session_key
    },
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/info", response_model=UserBasicInfoModel)
async def getUserBasicInfoApi(
        current_user: UserBasicInfoModel = Depends(get_current_active_user)):
    return current_user


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


@router.get("/points")
async def getUserPoints(
        current_user: UserBasicInfoModel = Depends(get_current_active_user)):
    return {"points": current_user.total_points}


@router.get("/signin")
async def signin(
    response: Response,
    current_user: UserBasicInfoModel = Depends(get_current_active_user)):
    if datetime.now().date() == current_user.last_signin_date:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "今日已签到过"}
    await UserInfoDb.update_user_info(open_id=current_user.open_id,
                                      total_points=current_user.total_points +
                                      1,
                                      level_exp=current_user.level_exp + 10,
                                      last_signin_date=datetime.now().date())
    return {"added_points": 1, "added_exp": 10}
