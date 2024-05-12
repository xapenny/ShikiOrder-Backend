from models.UserInfoModel import UserBasicInfoModel
from models.CreateOrderRequestModel import CreateOrderRequestModel
from fastapi import APIRouter, Depends, status, Response
from dependencies import get_current_active_user
from database.models.Coupon import CouponDb
from database.models.Order import OrderDb, OrderState
from database.models.Product import ProductDb
from datetime import datetime
from utils.verify_code import VerifyCode

router = APIRouter(prefix="/order")


@router.post("/create")
async def createOrderApi(
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
        coupon = await CouponDb.get_coupon_by_id(request.used_coupon_id)
        if coupon is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "没有找到该优惠券"}
        if coupon.open_id != user_info.open_id:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "非法请求"}
        # Calculate discount
        if coupon.threshold is not None and total_price < coupon.threshold:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "优惠券未达到使用条件"}
        if coupon.discount is not None:
            total_price -= coupon.discount
        elif coupon.discount_percentage is not None:
            total_price = int(total_price *
                              (1 - coupon.discount_percentage / 100))

    # Verify total price
    if total_price != request.total_price:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "优惠金额校验失败"}

    # Consume coupon
    if request.used_coupon_id != -1:
        await CouponDb.consume_coupon(coupon_id=request.used_coupon_id)

    # Create order
    product_ids = ";".join([str(x[0]) for x in request.products])
    product_quantities = ";".join([str(x[1]) for x in request.products])
    verify_code = VerifyCode.get_code(is_takeout=request.is_takeout)
    order = await OrderDb.create_order(shop_id=request.shop_id,
                                       shop_name=request.shop_name,
                                       table_id=request.table_id,
                                       open_id=user_info.open_id,
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

    return {
        "order_id": order.id,
        "verify_code": verify_code,
        "time": order.time,
        "state": order.state,
        "shop_name": order.shop_name,
        "products": {
            product_id: quantity
            for product_id, quantity in zip(product_ids.split(";"),
                                            product_quantities.split(";"))
        },
        "is_takeout": order.is_takeout,
        "comments": order.comments,
        "paid_price": order.paid_price
    }
