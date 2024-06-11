from typing import Optional
from sqlalchemy import Column, String, Integer, update

from database.dbInit import db


class SwiperDb(db.Model):
    __tablename__ = 'swiper'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    image = Column(String(255), nullable=False)

    @classmethod
    async def add_swiper(cls, shop_id: int,
                         image: str) -> Optional["SwiperDb"]:
        create = await cls.create(shop_id=shop_id, image=image)
        return create

    @classmethod
    async def remove_swiper(cls, swiper_id: int) -> Optional["SwiperDb"]:
        query = await cls.query.where(cls.id == swiper_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def get_swipers_by_shop_id(
            cls, shop_id: int) -> Optional[list["SwiperDb"]]:
        query = await cls.query.where(cls.shop_id == shop_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_swiper_by_id(cls, swiper_id: int) -> Optional["SwiperDb"]:
        query = await cls.query.where(cls.id == swiper_id).gino.first()
        if not query:
            return None
        return query
