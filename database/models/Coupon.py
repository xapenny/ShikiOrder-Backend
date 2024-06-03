from typing import Optional
from sqlalchemy import Column, String, Integer, BigInteger, UniqueConstraint

from database.dbInit import db


class CouponDb(db.Model):
    __tablename__ = 'coupon'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    shop_id = Column(Integer, nullable=False)
    threshold = Column(Integer)
    discount = Column(Integer)
    discount_percentage = Column(Integer)

    @classmethod
    async def create_coupon(
            cls,
            name: str,
            shop_id: int,
            threshold: Optional[int] = None,
            discount: Optional[int] = None,
            discount_percentage: Optional[int] = None) -> Optional["CouponDb"]:
        create = await cls.create(name=name,
                                  shop_id=shop_id,
                                  threshold=threshold,
                                  discount=discount,
                                  discount_percentage=discount_percentage)
        return create

    @classmethod
    async def get_coupon_by_id(cls, coupon_id: int) -> Optional["CouponDb"]:
        query = await cls.query.where(cls.id == coupon_id).gino.first()
        if not query:
            return None
        return query

class UserCouponDb(db.Model):
    __tablename__ = 'user_coupon'

    id = Column(BigInteger, primary_key=True)
    coupon_id = Column(Integer, nullable=False)
    open_id = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('open_id',
                                       'coupon_id',
                                       name='uq_openid_couponid'), )

    @classmethod
    async def add_user_coupon(cls, coupon_id: int, open_id: str,
                              quantity: int) -> Optional["UserCouponDb"]:
        query = await cls.query.where(cls.coupon_id == coupon_id,
                                      cls.open_id == open_id).gino.first()
        if query:
            query.quantity += quantity
            await query.update()
            return query
        else:
            create = await cls.create(coupon_id=coupon_id,
                                      open_id=open_id,
                                      quantity=quantity)
            return create

    @classmethod
    async def get_user_coupon(cls,
                              open_id: str) -> Optional[list["UserCouponDb"]]:
        query = await cls.query.where(cls.open_id == open_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def consume_user_coupon(cls, coupon_id: int, open_id: str):
        query = await cls.query.where(cls.coupon_id == coupon_id,
                                      cls.open_id == open_id).gino.first()
        if query:
            query.quantity -= 1
            if query.quantity == 0:
                await query.delete()
            else:
                await query.update()
            return query
        return None
