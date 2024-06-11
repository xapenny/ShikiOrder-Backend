from typing import Optional
from sqlalchemy import Column, String, Integer, update

from database.dbInit import db


class ProductDb(db.Model):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    image = Column(String(255), nullable=False)
    stock = Column(Integer, nullable=False)

    @classmethod
    async def add_product(
            cls,
            shop_id: int,
            category_id: int,
            price: int,
            name: str,
            image: str,
            stock: int,
            description: Optional[str] = None) -> Optional["ProductDb"]:
        create = await cls.create(shop_id=shop_id,
                                  category_id=category_id,
                                  price=price,
                                  name=name,
                                  description=description,
                                  image=image,
                                  stock=stock)
        return create

    @classmethod
    async def get_product_by_id(cls, product_id: int) -> Optional["ProductDb"]:
        query = await cls.query.where(cls.id == product_id).gino.first()
        if not query:
            return None
        return query

    @classmethod
    async def get_product_by_shop_id(
            cls, shop_id: int) -> Optional[list["ProductDb"]]:
        query = await cls.query.where(cls.shop_id == shop_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def get_product_by_category_id(
            cls, category_id: int) -> Optional[list["ProductDb"]]:
        query = await cls.query.where(cls.category_id == category_id
                                      ).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def remove_product(cls, product_id: int) -> Optional["ProductDb"]:
        query = await cls.query.where(cls.id == product_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def update_product(cls, product_id: int, **kwargs) -> bool:
        query = update(cls).where(cls.id == product_id).values(**kwargs)
        result = await db.status(query)
        return True if result else False

    @classmethod
    async def get_all_products(cls) -> Optional[list["ProductDb"]]:
        query = await cls.query.gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def is_category_id_exist(cls, category_id: int) -> bool:
        query = await cls.query.where(cls.category_id == category_id
                                      ).gino.first()
        return True if query is not None else False


class ProductCategoryDb(db.Model):
    __tablename__ = 'product_category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255))

    @classmethod
    async def add_category(cls,
                           shop_id: int,
                           name: str,
                           description: Optional[str] = None
                           ) -> Optional["ProductCategoryDb"]:
        create = await cls.create(shop_id=shop_id,
                                  name=name,
                                  description=description)
        return create

    @classmethod
    async def get_category_by_id(
            cls, category_id: int) -> Optional["ProductCategoryDb"]:
        query = await cls.query.where(cls.id == category_id).gino.first()
        if not query:
            return None
        return query

    @classmethod
    async def get_category_by_shop_id(
            cls, shop_id: int) -> Optional[list["ProductCategoryDb"]]:
        query = await cls.query.where(cls.shop_id == shop_id).gino.all()
        if not query:
            return None
        return query

    @classmethod
    async def update_category_name(cls, category_id: int, name: str):
        query = update(cls).where(cls.id == category_id).values(name=name)
        result = await db.status(query)
        return result

    @classmethod
    async def remove_category(
            cls, category_id: int) -> Optional["ProductCategoryDb"]:
        query = await cls.query.where(cls.id == category_id).gino.first()
        if not query:
            return None
        await query.delete()
        return query

    @classmethod
    async def get_all_categories(cls) -> Optional[list["ProductCategoryDb"]]:
        query = await cls.query.gino.all()
        if not query:
            return None
        return query
