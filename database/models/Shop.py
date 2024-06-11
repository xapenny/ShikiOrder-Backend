from typing import Optional
from sqlalchemy import Column, String, BigInteger, update

from database.dbInit import db


class ShopDb(db.Model):
    __tablename__ = 'shop'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    announcement = Column(String(255))
    about = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(BigInteger)

    @classmethod
    async def add_shop(
            cls,
            name: str,
            address: str,
            about: str,
            email: str,
            phone: Optional[int] = None,
            announcement: Optional[str] = None) -> Optional["ShopDb"]:
        create = await cls.create(name=name,
                                  address=address,
                                  about=about,
                                  email=email,
                                  phone=phone,
                                  announcement=announcement)
        return create

    @classmethod
    async def get_all_shops(cls) -> Optional[list["ShopDb"]]:
        query = await cls.query.gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def remove_shop(cls, shop_id: int) -> Optional["ShopDb"]:
        query = await cls.query.where(cls.id == shop_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def get_shop_by_id(cls, shop_id: int) -> Optional["ShopDb"]:
        query = await cls.query.where(cls.id == shop_id).gino.first()
        return query

    @classmethod
    async def is_shop_exists(cls, shop_id: int) -> bool:
        query = await cls.query.where(cls.id == shop_id).gino.first()
        return query is not None

    @classmethod
    async def update_shop_info(
            cls,
            shop_id: int,
            name: Optional[str] = None,
            address: Optional[str] = None,
            about: Optional[str] = None,
            email: Optional[str] = None,
            phone: Optional[int] = None,
            announcement: Optional[str] = None) -> Optional["ShopDb"]:
        query = await cls.query.where(cls.id == shop_id).gino.first()
        if not query:
            return None
        query2 = update(cls).where(cls.id == shop_id)
        if name:
            query2 = query2.values(name=name)
        if address:
            query2 = query2.values(address=address)
        if about:
            query2 = query2.values(about=about)
        if email:
            query2 = query2.values(email=email)
        if phone:
            query2 = query2.values(phone=phone)
        if announcement:
            query2 = query2.values(announcement=announcement)
        result = await db.status(query2)
        return result
