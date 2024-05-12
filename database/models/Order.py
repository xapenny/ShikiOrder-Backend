from typing import Optional
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

    id = Column(BigInteger, primary_key=True)
    shop_id = Column(Integer, nullable=False)
    shop_name = Column(String(255), nullable=False)
    table_id = Column(Integer)
    open_id = Column(String(255), nullable=False)
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
            open_id: str,
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
                                  open_id=open_id,
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

    async def remove_order(cls, order_id: int):
        query = await cls.query.where(cls.id == order_id).gino.first()
        if not query:
            return None
        await query.delete()

    async def update_order_state(cls, order_id: int, state: int):
        query = update(cls).where(cls.id == order_id).values(state=state)
        await db.status(query)

    async def get_user_order(cls, open_id: str) -> Optional[list["OrderDb"]]:
        query = await cls.query.where(cls.open_id == open_id).gino.all()
        if not query:
            return None
        return query
