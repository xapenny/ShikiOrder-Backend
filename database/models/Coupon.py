from typing import Optional
from datetime import date
from sqlalchemy import Column, String, Integer, Date, BigInteger, UniqueConstraint, update

from database.dbInit import db


class CouponDb(db.Model):
    __tablename__ = 'coupon'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    shop_id = Column(Integer, nullable=False)
    threshold = Column(Integer)
    discount = Column(Integer)
    discount_percentage = Column(Integer)
    valid_date = Column(Date, nullable=False)

    @classmethod
    async def create_coupon(
            cls,
            name: str,
            shop_id: int,
            valid_date: date,
            threshold: Optional[int] = None,
            discount: Optional[int] = None,
            discount_percentage: Optional[int] = None) -> Optional["CouponDb"]:
        create = await cls.create(name=name,
                                  shop_id=shop_id,
                                  valid_date=valid_date,
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

    @classmethod
    async def get_all_user_coupons(cls) -> Optional[list["UserCouponDb"]]:
        query = await cls.query.gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_coupons_by_shop_id(
            cls, shop_id: int) -> Optional[list["CouponDb"]]:
        query = await cls.query.where(cls.shop_id == shop_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def remove_coupon(cls, coupon_id: int) -> Optional["CouponDb"]:
        query = await cls.query.where(cls.id == coupon_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query


class UserCouponDb(db.Model):
    __tablename__ = 'user_coupon'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    shop_id = Column(Integer, nullable=False)

    @classmethod
    async def add_user_coupon(cls, coupon_id: int, shop_id: int,
                              user_id: int) -> Optional["UserCouponDb"]:
        create = await cls.create(coupon_id=coupon_id,
                                  user_id=user_id,
                                  shop_id=shop_id)
        return create

    @classmethod
    async def get_user_coupons(cls, shop_id: int,
                               user_id: int) -> Optional[list["UserCouponDb"]]:
        query = await cls.query.where(cls.user_id == user_id
                                      ).where(cls.shop_id == shop_id
                                              ).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_user_all_coupons(
            cls, user_id: int) -> Optional[list["UserCouponDb"]]:
        query = await cls.query.where(cls.user_id == user_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def consume_user_coupon(cls, id: int, shop_id: int,
                                  user_id: int) -> Optional["UserCouponDb"]:
        query = await cls.query.where(cls.id == id
                                      ).where(cls.user_id == user_id
                                              ).where(cls.shop_id == shop_id
                                                      ).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def remove_coupon_users(cls, shop_id: int,
                                  coupon_id: int) -> Optional["UserCouponDb"]:
        query = await cls.query.where(cls.coupon_id == coupon_id
                                      ).where(cls.shop_id == shop_id
                                              ).gino.all()
        if not query:
            return None
        for user in query:
            await user.delete()
        return query

    @classmethod
    async def get_user_coupon_by_id(
            cls, user_coupon_id: int) -> Optional["UserCouponDb"]:
        query = await cls.query.where(cls.id == user_coupon_id).gino.first()
        if not query:
            return None
        return query
