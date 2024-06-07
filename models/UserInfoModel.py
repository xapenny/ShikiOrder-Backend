from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date


class UserBasicInfoModel(BaseModel):
    open_id: str
    user_id: int
    nickname: str
    avatar: str
    phone: Optional[int]
    gender: Literal['男', '女', '保密']
    total_points: int
    level_exp: int
    last_signin_date: Optional[date]


class UpdateUserInfoRequestModel(BaseModel):
    nickname: str
    gender: Literal['男', '女', '保密']
    phone: int
