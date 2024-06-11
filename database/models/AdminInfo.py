from typing import Optional, Literal
from sqlalchemy import BigInteger, Column, String, Integer, update

from database.dbInit import db


class AdminInfoDb(db.Model):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(255), nullable=False)
    role = Column(Integer, nullable=False)
    permission = Column(Integer, nullable=False)
    phone = Column(BigInteger, nullable=False, unique=True)
    password = Column(String(32), nullable=False)

    @classmethod
    async def add_admin(cls, nickname: str, role: Literal[0, 1, 2],
                        permission: int, phone: int, password: str):
        create = await cls.create(nickname=nickname,
                                  role=role,
                                  permission=permission,
                                  phone=phone,
                                  password=password)
        return create

    @classmethod
    async def is_user_exists(cls, phone: int) -> bool:
        query = await cls.query.where(cls.phone == phone).gino.first()
        return query is not None

    @classmethod
    async def get_admin_by_uid(cls, user_id) -> Optional["AdminInfoDb"]:
        query = await cls.query.where(cls.id == user_id).gino.first()
        return query

    @classmethod
    async def get_admin_by_phone(cls, phone: int) -> Optional["AdminInfoDb"]:
        query = await cls.query.where(cls.phone == phone).gino.first()
        return query

    @classmethod
    async def get_admins_by_role_and_permission(
            cls, role: int, permission: int) -> Optional[list["AdminInfoDb"]]:
        query = cls.query.where(cls.role >= role)
        if role > 0:
            query = query.where(cls.permission == permission)
        result = await query.gino.all()
        return result

    @classmethod
    async def update_admin_info(cls,
                                id: int,
                                phone: Optional[int] = None,
                                nickname: Optional[str] = None,
                                role: Optional[Literal[0, 1, 2]] = None,
                                permission: Optional[int] = None,
                                password: Optional[str] = None):
        query = update(cls).where(cls.id == id)
        if phone:
            query = query.values(phone=phone)
        if nickname:
            query = query.values(nickname=nickname)
        if role:
            query = query.values(role=role)
        if permission:
            query = query.values(permission=permission)
        if password:
            query = query.values(password=password)
        result = await db.status(query)
        return result

    @classmethod
    async def remove_admin(cls, phone: int):
        query = await cls.query.where(cls.phone == phone).gino.first()
        if not query:
            return None
        await query.delete()
        return query
