from models.UserInfoModel import UserBasicInfoModel
from fastapi import APIRouter, Depends, Response, status
from dependencies import get_current_active_user
from database.models.UserInfo import UserInfoDb
from database.models.PointStore import PointStoreDb, PointStoreLogDb

router = APIRouter(prefix='/point-store')


@router.get("/items")
async def get_point_shop_items(
    shop: int, _: UserBasicInfoModel = Depends(get_current_active_user)):
    items = await PointStoreDb.get_items_by_shop_id(shop_id=shop)
    result = []
    if items is not None:
        for item in items:
            result.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'image': item.image,
                'stock': item.stock,
                'description': item.description
            })
    return {'items': result}


@router.get("/purchase")
async def purchase_item(
    item: int,
    response: Response,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):
    item_info = await PointStoreDb.get_item_by_id(item)
    if item_info is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "商品不存在"}
    if item_info.stock <= 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "商品库存不足"}
    if item_info.price > user_info.total_points:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "积分不足"}
    await PointStoreDb.update_item(item_id=item, stock=item_info.stock - 1)
    await UserInfoDb.update_user_info(open_id=user_info.open_id,
                                      total_points=user_info.total_points -
                                      item_info.price)
    await PointStoreLogDb.add_log(user_id=user_info.user_id,
                                  shop_id=item_info.shop_id,
                                  item_id=item_info.id)
    return {"success": "购买成功"}


@router.get("/logs")
async def get_log(
    shop: int,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):
    logs = await PointStoreLogDb.get_logs_by_uid_and_shop_id(
        user_id=user_info.user_id, shop_id=shop)
    result = []
    if logs is not None:
        for log in logs:
            result.append({
                'id': log.id,
                'user_id': log.user_id,
                'shop_id': log.shop_id,
                'express_id': log.express_id,
                'item_id': log.item_id,
                'created_at': log.created_at
            })
    return {'logs': result}
