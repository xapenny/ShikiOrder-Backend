from pydantic import BaseModel


class UserLoginRequestModel(BaseModel):
    code: str
    avatar: str
    nickname: str
