from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from configs.Config import Config
from utils.ahttp import AsyncAioHTTP
from database.models.UserInfo import UserInfoDb
from models.UserInfoModel import UserBasicInfoModel

SECRET_KEY = Config.get_token_crypto()["SECRET_KEY"]
ALGORITHM = Config.get_token_crypto()["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = Config.get_token_crypto(
)["ACCESS_TOKEN_EXPIRE_MINUTES"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_user(open_id: str) -> Optional[UserBasicInfoModel]:
    user_obj = await UserInfoDb.get_user_by_open_id(open_id=open_id)
    if user_obj is None:
        return None

    user_dict = {
        "open_id": user_obj.open_id,
        "user_id": user_obj.id,
        "nickname": user_obj.nickname,
        "avatar": user_obj.avatar,
        "phone": user_obj.phone,
        "total_points": user_obj.total_points,
        "level_exp": user_obj.level_exp,
        "gender": user_obj.gender,
        "last_signin_date": user_obj.last_signin_date
    }
    return UserBasicInfoModel(**user_dict)


async def get_wc_code2session(
        code: str) -> Union[str, Optional[dict[str, str]]]:
    url = f"https://api.weixin.qq.com/sns/jscode2session"
    resp = await AsyncAioHTTP.get(url=url,
                                  params={
                                      "appid":
                                      Config.get_wechat_config()['APP_ID'],
                                      "secret":
                                      Config.get_wechat_config()['SECRET'],
                                      "js_code":
                                      code,
                                      "grant_type":
                                      "authorization_code"
                                  })
    if resp is not None:
        if 'errmsg' not in resp:
            return resp
        return resp['errmsg']
    return None


async def check_wc_session_expired(open_id: str, session_key: str):
    if open_id is None or session_key is None:
        return False
    user = await UserInfoDb.get_user_by_open_id(open_id=open_id)
    if user is None:
        return False
    if user.session_key != session_key:
        return False
    return True


async def authenticate_user(code: str):
    user = await get_wc_code2session(code=code)
    if not user:
        return False
    if not isinstance(user, dict):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"expire": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire_until: float = payload.get("expire")  # type: ignore
        if datetime.utcnow().timestamp() > expire_until:
            is_wc_session_expired = await check_wc_session_expired(
                open_id=payload.get("open_id"),
                session_key=payload.get("session_key"))
            if is_wc_session_expired:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credential expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        open_id: Optional[int] = payload.get("open_id")
        if open_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(open_id=open_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: UserBasicInfoModel = Depends(get_current_user)):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
