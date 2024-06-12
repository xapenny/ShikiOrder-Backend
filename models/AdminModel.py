from pydantic import BaseModel
from typing import Optional, Literal


class AdminBasicInfoModel(BaseModel):
    user_id: int
    nickname: str
    phone: int
    role: int
    permission: int


class AdminUpdatePasswordRequestModel(BaseModel):
    new_password: str


class AdminUpdateInfoRequestModel(BaseModel):
    nickname: str
    phone: int


class UpdateAdminUserRequestModel(BaseModel):
    user_id: int
    username: str
    phone: str
    password: str
    role: int
    permission: int


class RemoveAdminUserRequestModel(BaseModel):
    user_id: int


class UpdateOrderStateRequestModel(BaseModel):
    order_id: int
    state: Literal[1, 3, 4]


class UpdateShopRequestModel(BaseModel):
    shop_id: int
    shop_name: str
    shop_address: str
    shop_phone: int
    shop_email: str
    shop_about: str
    shop_announcement: str


class RemoveShopRequestModel(BaseModel):
    shop_id: int


class AddShopSwiperRequestModel(BaseModel):
    shop_id: int
    image: str


class RemoveShopSwiperRequestModel(BaseModel):
    swiper_id: int


class UpdateProductRequestModel(BaseModel):
    product_id: int
    shop_id: int
    category_id: int
    product_name: str
    product_price: int
    product_description: str
    product_image: str
    product_stock: int


class RemoveProductRequestModel(BaseModel):
    product_id: int


class UpdateProductCategoryRequestModel(BaseModel):
    category_id: int
    shop_id: int
    category_name: str


class RemoveProductCategoryRequestModel(BaseModel):
    category_id: int


class CreateCouponRequestModel(BaseModel):
    name: str
    shop_id: int
    valid_date: str
    threshold: Optional[int] = None
    discount: Optional[int] = None
    discount_percentage: Optional[int] = None


class RemoveCouponRequestModel(BaseModel):
    coupon_id: int


class GiftCouponRequestModel(BaseModel):
    gift_all: bool
    phone: Optional[str] = None
    coupon_id: int
    shop_id: int
    quantity: int


class UpdatePointStoreItemRequestModel(BaseModel):
    item_id: int
    shop_id: int
    item_type: Literal[0, 1]
    item_name: str
    item_price: int
    item_description: str
    item_image: str
    item_stock: int


class RemovePointStoreItemRequestModel(BaseModel):
    item_id: int
