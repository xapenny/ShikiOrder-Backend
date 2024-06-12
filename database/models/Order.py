from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, BigInteger, update, DateTime, Boolean

from database.dbInit import db


class OrderState():
    UNPAID = 0
    CANCELED = 1
    PENDING = 2
    READY = 3
    FINISH = 4


class OrderDb(db.Model):
    __tablename__ = 'order'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    shop_name = Column(String(255), nullable=False)
    table_id = Column(Integer)
    user_id = Column(Integer, nullable=False)
    phone = Column(BigInteger, nullable=False)
    time = Column(DateTime, nullable=False)
    is_takeout = Column(Boolean, nullable=False)
    verify_code = Column(String(5), nullable=False)
    product_ids = Column(String(255), nullable=False)
    product_quantities = Column(String(255), nullable=False)
    state = Column(Integer, nullable=False, default=OrderState.UNPAID)
    comments = Column(String(255))
    paid_price = Column(Integer)

    @classmethod
    async def create_order(
            cls,
            shop_id: int,
            shop_name: str,
            table_id: int,
            user_id: int,
            phone: int,
            time: str,
            is_takeout: bool,
            verify_code: str,
            product_ids: str,
            product_quantities: str,
            state: int,
            paid_price: int,
            comments: Optional[str] = None) -> Optional["OrderDb"]:
        create = await cls.create(shop_id=shop_id,
                                  shop_name=shop_name,
                                  table_id=table_id,
                                  user_id=user_id,
                                  phone=phone,
                                  time=time,
                                  is_takeout=is_takeout,
                                  verify_code=verify_code,
                                  product_ids=product_ids,
                                  product_quantities=product_quantities,
                                  state=state,
                                  paid_price=paid_price,
                                  comments=comments)
        return create

    @classmethod
    async def remove_order(cls, order_id: int) -> Optional["OrderDb"]:
        query = await cls.query.where(cls.id == order_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def update_order_state(cls, order_id: int, state: int) -> bool:
        query = update(cls).where(cls.id == order_id).values(state=state)
        result = await db.status(query)
        return result

    @classmethod
    async def get_user_order(cls, user_id: str) -> Optional[list["OrderDb"]]:
        query = await cls.query.where(cls.user_id == user_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_order_by_id(cls, order_id: int) -> Optional["OrderDb"]:
        query = await cls.query.where(cls.id == order_id).gino.first()
        if not query:
            return None
        return query

    @classmethod
    async def get_user_recent_order_id(cls, user_id: int,
                                       shop_id: int) -> list["int"]:
        query = await cls.query.where(cls.user_id == user_id
                                      ).where(cls.shop_id == shop_id).order_by(
                                          cls.id.desc()).limit(10).gino.all()
        if not query:
            return None
        return [x.id for x in query]

    @classmethod
    async def get_orders_by_shop_id(cls, page_size: int, offset: int,
                                    shop_id: int) -> Optional[list["OrderDb"]]:
        query = await cls.query.where(cls.shop_id == shop_id).where(
            cls.time >= datetime.now() - timedelta(days=30)
        ).order_by(cls.time.desc()).offset(offset).limit(page_size).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_all_orders(cls, page_size: int,
                             offset: int) -> Optional[list["OrderDb"]]:
        query = await cls.query.order_by(
            cls.time.desc()).offset(offset).limit(page_size).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def remove_orders_by_shop_id(cls,
                                       shop_id: int) -> Optional["OrderDb"]:
        query = await cls.query.where(cls.shop_id == shop_id).gino.all()
        if not query:
            return None
        for order in query:
            await order.delete()
        return query

    @classmethod
    async def get_order_counts_by_shop_id(cls, shop_id: int) -> int:
        return await db.select([db.func.count(cls.id)]
                               ).where(cls.shop_id == shop_id).gino.scalar()

    @classmethod
    async def get_all_order_counts(cls):
        return await db.func.count(cls.id).gino.scalar()
