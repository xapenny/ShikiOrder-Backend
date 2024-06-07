from datetime import datetime, timedelta
from typing import Optional
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from configs.Config import Config
from database.models.AdminInfo import AdminInfoDb
from models.AdminModel import AdminBasicInfoModel

SECRET_KEY = Config.get_token_crypto()["SECRET_KEY"]
ALGORITHM = Config.get_token_crypto()["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = Config.get_token_crypto(
)["ACCESS_TOKEN_EXPIRE_MINUTES"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/token")


class AdminInDb(AdminBasicInfoModel):
    hashed_password: str


async def get_admin(phone: int) -> Optional[AdminInDb]:
    admin_obj = await AdminInfoDb.get_admin_by_phone(phone=phone)
    if admin_obj is None:
        return None
    admin_dict = {
        "user_id": admin_obj.id,
        "nickname": admin_obj.nickname,
        "phone": admin_obj.phone,
        "role": admin_obj.role,
        "permission": admin_obj.permission,
        "hashed_password": admin_obj.password
    }
    return AdminInDb(**admin_dict)


def verify_password(plain_password, hashed_password):
    md5_hash = hashlib.md5()
    md5_hash.update(plain_password.encode('utf-8'))
    md5_result = md5_hash.hexdigest()
    return md5_result == hashed_password


async def authenticate_user(username: str,
                            password: str) -> Optional[AdminInDb]:
    user = await get_admin(int(username))
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
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


async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire_until: float = payload.get("expire")  # type: ignore
        if datetime.utcnow().timestamp() > expire_until:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credential expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        phone: Optional[int] = payload.get("phone")
        if phone is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_admin(phone=phone)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_admin(
        current_admin: AdminBasicInfoModel = Depends(get_current_admin)):
    return current_admin
