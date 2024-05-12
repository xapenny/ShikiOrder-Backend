from pydantic import BaseModel
from typing import Optional


class CreateOrderRequestModel(BaseModel):
    shop_id: int
    shop_name: str
    table_id: Optional[int]
    phone: int
    is_takeout: bool
    products: list[list]
    used_coupon_id: int
    total_price: int
    comments: Optional[str]
