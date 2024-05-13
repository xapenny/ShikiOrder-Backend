from pydantic import BaseModel
from typing import Optional, Literal


class UserBasicInfoModel(BaseModel):
    open_id: str
    nickname: str
    avatar: str
    phone: Optional[int]
    gender: Literal['男', '女', '保密']
    total_points: int
    level_exp: int


class UpdateUserInfoRequestModel(BaseModel):
    nickname: str
    gender: Literal['男', '女', '保密']
    phone: int
