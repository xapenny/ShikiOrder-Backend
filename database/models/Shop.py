from typing import Optional
from sqlalchemy import Column, String, BigInteger, DECIMAL

from database.dbInit import db


class ShopDb(db.Model):
    __tablename__ = 'shop'
    id = Column(BigInteger, primary_key=True)
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
    async def remove_shop(cls, shop_id: int):
        query = await cls.query.where(cls.id == shop_id).gino.first()
        if query:
            await query.delete()
