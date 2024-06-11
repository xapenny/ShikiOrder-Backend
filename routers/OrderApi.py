from models.UserInfoModel import UserBasicInfoModel
from models.CreateOrderRequestModel import CreateOrderRequestModel
from fastapi import APIRouter, Depends, status, Response
from dependencies import get_current_active_user
from database.models.Coupon import CouponDb, UserCouponDb
from database.models.Order import OrderDb, OrderState
from database.models.Product import ProductDb
from datetime import datetime
from utils.verify_code import VerifyCode
from random import randint

router = APIRouter(prefix="/order")


@router.post("/create")
async def create_order(
    request: CreateOrderRequestModel,
    response: Response,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):

    # Calculate total price
    total_price = 0
    products = await ProductDb.get_product_by_shop_id(request.shop_id)
    if products is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "非法请求"}
    for product_id, quantity in request.products:
        product = next((p for p in products if p.id == int(product_id)), None)
        if product is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "非法请求"}
        total_price += product.price * quantity

    # Inspect coupon
    if request.used_coupon_id != -1:
        user_coupon = await UserCouponDb.get_user_coupon_by_id(
            user_coupon_id=request.used_coupon_id)
        if user_coupon is None:
            return {"error": "没有找到该优惠券"}
        coupon = await CouponDb.get_coupon_by_id(
            coupon_id=user_coupon.coupon_id)
        if coupon is None:
            await UserCouponDb.consume_user_coupon(id=user_coupon.id,
                                                   shop_id=request.shop_id,
                                                   user_id=user_info.user_id)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "优惠券已失效"}
        # Calculate discount
        if coupon.threshold is not None and total_price < coupon.threshold:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "优惠券未达到使用条件"}
        if coupon.discount is not None:
            total_price -= coupon.discount
        if coupon.discount_percentage is not None:
            total_price = round(total_price *
                                (1 - coupon.discount_percentage / 100))

    # Verify total price
    if abs(total_price - request.total_price) > 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "优惠金额校验失败"}

    # Consume coupon
    if request.used_coupon_id != -1:
        coupon_result = await UserCouponDb.consume_user_coupon(
            id=request.used_coupon_id,
            shop_id=request.shop_id,
            user_id=user_info.user_id)
        if coupon_result is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "非法请求"}

    # Create order
    product_ids = ";".join([str(x[0]) for x in request.products])
    product_quantities = ";".join([str(x[1]) for x in request.products])
    verify_code = VerifyCode.get_code(is_takeout=request.is_takeout)
    order = await OrderDb.create_order(shop_id=request.shop_id,
                                       shop_name=request.shop_name,
                                       table_id=request.table_id,
                                       user_id=user_info.user_id,
                                       phone=request.phone,
                                       time=datetime.now(),
                                       is_takeout=request.is_takeout,
                                       verify_code=verify_code,
                                       product_ids=product_ids,
                                       product_quantities=product_quantities,
                                       state=OrderState.UNPAID,
                                       paid_price=total_price,
                                       comments=request.comments)
    if order is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "创建订单失败"}

    return {"order_id": order.id}


@router.get("/history")
async def get_user_order_history(
    shop: int,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):
    order_ids = await OrderDb.get_user_recent_order_id(
        user_id=user_info.user_id, shop_id=shop)
    return {"order_ids": order_ids if order_ids is not None else []}


@router.get("/info")
async def get_order_info(
    id: int,
    response: Response,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):
    order_info = await OrderDb.get_order_by_id(id)
    if order_info is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "订单不存在"}
    if order_info.user_id != user_info.user_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "非法请求"}

    return {
        "order_id":
        order_info.id,
        "verify_code":
        order_info.verify_code,
        "time":
        order_info.time,
        "state":
        order_info.state,
        "shop_name":
        order_info.shop_name,
        "table_id":
        order_info.table_id,
        "products": [[int(product_id), int(quantity)]
                     for product_id, quantity in zip(
                         order_info.product_ids.split(";"),
                         order_info.product_quantities.split(";"))],
        "is_takeout":
        order_info.is_takeout,
        "comments":
        order_info.comments,
        "paid_price":
        order_info.paid_price
    }


@router.get("/cancel")
async def cancel_order(
    id: int,
    response: Response,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):
    order = await OrderDb.get_order_by_id(id)
    if order is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "订单不存在"}
    if order.user_id != user_info.user_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "非法请求"}
    if order.state != OrderState.UNPAID:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "订单状态不允许取消"}

    await OrderDb.update_order_state(order_id=id, state=OrderState.CANCELED)
    return {"order_id": id}


@router.get('/pay')
async def pay_order(
    id: int,
    response: Response,
    user_info: UserBasicInfoModel = Depends(get_current_active_user)):
    order = await OrderDb.get_order_by_id(id)
    if order is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "订单不存在"}
    if order.user_id != user_info.user_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "非法请求"}
    if order.state != OrderState.UNPAID:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "订单状态不允许支付"}

        # Fake Payment
    if (randint(0, 1)):
        await OrderDb.update_order_state(order_id=id, state=OrderState.PENDING)
        return {"order_id": id}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "付款失败(测试)"}
