from typing import Optional
from sqlalchemy import Column, String, Integer, BigInteger

from database.dbInit import db


class CouponDb(db.Model):
    __tablename__ = 'coupon'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    open_id = Column(String(255), nullable=False)
    shop_id = Column(Integer, nullable=False)
    threshold = Column(Integer)
    discount = Column(Integer)
    discount_percentage = Column(Integer)

    @classmethod
    async def create_coupon(
            cls,
            name: str,
            open_id: str,
            shop_id: int,
            threshold: Optional[int] = None,
            discount: Optional[int] = None,
            discount_percentage: Optional[int] = None) -> Optional["CouponDb"]:
        create = await cls.create(open_id=open_id,
                                  name=name,
                                  shop_id=shop_id,
                                  threshold=threshold,
                                  discount=discount,
                                  discount_percentage=discount_percentage)
        return create

    @classmethod
    async def get_user_coupon(cls, open_id: str) -> Optional[list["CouponDb"]]:
        query = await cls.query.where(cls.open_id == open_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_coupon_by_id(cls, coupon_id: int) -> Optional["CouponDb"]:
        query = await cls.query.where(cls.id == coupon_id).gino.first()
        if not query:
            return None
        return query

    @classmethod
    async def consume_coupon(cls, coupon_id: int):
        await cls.delete.where(cls.id == coupon_id).gino.status()
