from models.UserInfoModel import UserBasicInfoModel
from fastapi import APIRouter, Depends, Response, status
from dependencies import get_current_active_user
from database.models.Shop import ShopDb
from database.models.Swiper import SwiperDb

router = APIRouter(prefix='/shop')


@router.get("/all")
async def get_all_shops(
    response: Response,
    _: UserBasicInfoModel = Depends(get_current_active_user)):
    shops = await ShopDb.get_all_shops()
    if shops is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "还没有商店喔"}
    result = []
    for shop in shops:
        swipers = await SwiperDb.get_swipers_by_shop_id(shop_id=shop.id)
        result.append({
            'id': shop.id,
            'name': shop.name,
            'address': shop.address,
            'announcement': shop.announcement,
            'about': shop.about,
            'email': shop.email,
            'phone': shop.phone,
            'swipers': swipers if swipers is not None else []
        })
    return {'shops': result}
