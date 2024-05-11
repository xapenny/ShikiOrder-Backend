from pydantic import BaseModel
from typing import Optional


class UserBasicInfoModel(BaseModel):
    open_id: str
    nickname: str
    avatar: str
    phone: Optional[int]
    gender: str
    total_points: int
    level_exp: int
