from models.UserInfoModel import UserBasicInfoModel
from fastapi import APIRouter, Depends, Response, status
from dependencies import get_current_active_user
from database.models.Coupon import CouponDb

router = APIRouter(prefix='/coupon')


@router.get("/all")
async def get_all_coupons(
    shop: int,
    response: Response,
    _: UserBasicInfoModel = Depends(get_current_active_user)):
    coupons = await CouponDb.get_coupons_by_shop_id(shop_id=shop)
    result = []
    if coupons is not None:
        for coupon in coupons:
            result.append({
                'id': coupon.id,
                'shop_id': coupon.shop_id,
                'name': coupon.name,
                'threshold': coupon.threshold,
                'discount': coupon.discount,
                'discount_percentage': coupon.discount_percentage,
                'valid_date': coupon.valid_date
            })
    return {'coupons': result}
