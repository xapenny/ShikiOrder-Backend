from typing import Optional, Literal
from sqlalchemy import BigInteger, Column, String, Integer, Date, update

from database.dbInit import db


class UserInfoDb(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    open_id = Column(String(255), nullable=False, unique=True)
    nickname = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=False)
    total_points = Column(Integer, nullable=False)
    level_exp = Column(Integer, nullable=False)
    gender = Column(String(2), nullable=False)
    phone = Column(BigInteger)
    last_signin_date = Column(Date)
    session_key = Column(String(255))

    @classmethod
    async def get_user_by_open_id(cls, open_id: str) -> Optional["UserInfoDb"]:
        query: Optional["UserInfoDb"] = await cls.query.where(
            cls.open_id == open_id).gino.first()
        if not query:
            return None
        return query  # type: ignore

    @classmethod
    async def is_user_exists(cls, open_id: int) -> bool:
        query: Optional["UserInfoDb"] = await cls.query.where(
            cls.open_id == open_id).gino.first()
        if query:
            return True
        return False

    @classmethod
    async def add_user(
        cls,
        open_id: str,
        avatar: str,
        total_points: int,
        level_exp: int,
        nickname: str,
        session_key: Optional[str] = None,
        phone: Optional[int] = None,
        gender: Optional[Literal['男', '女', '保密']] = '保密'
    ) -> Optional["UserInfoDb"]:

        create = await cls.create(open_id=open_id,
                                  avatar=avatar,
                                  total_points=total_points,
                                  level_exp=level_exp,
                                  nickname=nickname,
                                  phone=phone,
                                  gender=gender,
                                  session_key=session_key)
        return create

    @classmethod
    async def update_user_info(
            cls,
            open_id: str,
            avatar: Optional[str] = None,
            total_points: Optional[int] = None,
            level_exp: Optional[int] = None,
            nickname: Optional[str] = None,
            phone: Optional[int] = None,
            session_key: Optional[str] = None,
            gender: Optional[Literal['男', '女', '保密']] = None,
            last_signin_date: Optional[Date] = None) -> Optional["UserInfoDb"]:
        query = update(cls).where(cls.open_id == open_id)
        if avatar:
            query = query.values(avatar=avatar)
        if total_points:
            query = query.values(total_points=total_points)
        if level_exp:
            query = query.values(level_exp=level_exp)
        if nickname:
            query = query.values(nickname=nickname)
        if phone:
            query = query.values(phone=phone)
        if gender:
            query = query.values(gender=gender)
        if last_signin_date:
            query = query.values(last_signin_date=last_signin_date)
        if session_key:
            query = query.values(session_key=session_key)
        result = await db.status(query)
        return result

    @classmethod
    async def get_all_users(cls) -> Optional[list["UserInfoDb"]]:
        query = await cls.query.gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_user_by_phone(cls, phone: int) -> Optional["UserInfoDb"]:
        query = await cls.query.where(cls.phone == phone).gino.first()
        if not query:
            return None
        return query

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Optional["UserInfoDb"]:
        query = await cls.query.where(cls.id == user_id).gino.first()
        if not query:
            return None
        return query
