from datetime import timedelta

from fastapi import APIRouter, Response, status

from dependencies import (ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token,
                          get_wc_code2session)
from models.UserLoginModel import UserLoginRequestModel
from database.models.UserInfo import UserInfoDb

router = APIRouter()


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
        user = await UserInfoDb.addUser(open_id=open_id,
                                        avatar=request.avatar,
                                        total_points=0,
                                        level_exp=0,
                                        nickname=request.nickname)
    if not user:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "登录失败: 2"}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={
        "open_id": open_id,
        "session_key": session_key
    },
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
