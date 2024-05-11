from typing import Optional
from sqlalchemy import BigInteger, Column, String, Integer

from database.dbInit import db


class UserInfoDb(db.Model):
    __tablename__ = 'user_info'

    id = Column(Integer, primary_key=True)
    open_id = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=False)
    total_points = Column(Integer, nullable=False)
    level_exp = Column(Integer, nullable=False)
    gender = Column(String(2), nullable=False)
    phone = Column(BigInteger)

    @classmethod
    async def get_user_by_open_id(cls, open_id: str) -> Optional["UserInfoDb"]:
        query: Optional["UserInfoDb"] = await cls.query.where(
            cls.open_id == open_id).gino.first()
        if not query:
            return None
        return query  # type: ignore

    @classmethod
    async def isUserExists(cls, open_id: int) -> bool:
        query: Optional["UserInfoDb"] = await cls.query.where(
            cls.open_id == open_id).gino.first()
        if query:
            return True
        return False

    @classmethod
    async def addUser(cls,
                      open_id: str,
                      avatar: str,
                      total_points: int,
                      level_exp: int,
                      nickname: str,
                      phone: Optional[int] = None,
                      gender: Optional[str] = '保密') -> Optional["UserInfoDb"]:

        create = await cls.create(open_id=open_id,
                                  avatar=avatar,
                                  total_points=total_points,
                                  level_exp=level_exp,
                                  nickname=nickname,
                                  phone=phone,
                                  gender=gender)
        return create
