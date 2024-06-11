from typing import Optional, Literal
from sqlalchemy import Column, String, Integer, update

from database.dbInit import db


class PointStoreDb(db.Model):
    __tablename__ = 'point_store'

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    image = Column(String(255), nullable=False)
    stock = Column(Integer, nullable=False)

    @classmethod
    async def add_item(
            cls,
            shop_id: int,
            price: int,
            type: Literal[0, 1],
            name: str,
            image: str,
            stock: int,
            description: Optional[str] = None) -> Optional["PointStoreDb"]:
        create = await cls.create(shop_id=shop_id,
                                  price=price,
                                  type=type,
                                  name=name,
                                  description=description,
                                  image=image,
                                  stock=stock)
        return create

    @classmethod
    async def get_item_by_id(cls, item_id: int) -> Optional["PointStoreDb"]:
        query = await cls.query.where(cls.id == item_id).gino.first()
        if not query:
            return None
        return query

    @classmethod
    async def get_items_by_shop_id(
            cls, shop_id: int) -> Optional[list["PointStoreDb"]]:
        query = await cls.query.where(cls.shop_id == shop_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def remove_item(cls, item_id: int) -> Optional["PointStoreDb"]:
        query = await cls.query.where(cls.id == item_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def update_item(cls, item_id: int, **kwargs) -> bool:
        query = update(cls).where(cls.id == item_id).values(**kwargs)
        result = await db.status(query)
        return True if result else False

    @classmethod
    async def get_all_items(cls) -> Optional[list["PointStoreDb"]]:
        query = await cls.query.gino.all()
        if not query:
            return None
        return query
