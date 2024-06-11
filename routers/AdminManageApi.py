from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from dependencies_admin import get_current_active_admin
from models.AdminModel import (
    AdminBasicInfoModel, UpdateAdminUserRequestModel,
    RemoveAdminUserRequestModel, UpdateOrderStateRequestModel,
    RemoveProductRequestModel, UpdateProductRequestModel,
    RemoveProductCategoryRequestModel, UpdateProductCategoryRequestModel,
    CreateCouponRequestModel, RemoveCouponRequestModel, UpdateShopRequestModel,
    GiftCouponRequestModel, UpdatePointStoreItemRequestModel,
    AddShopSwiperRequestModel, RemoveShopSwiperRequestModel,
    RemovePointStoreItemRequestModel)
from database.models.AdminInfo import AdminInfoDb
from database.models.UserInfo import UserInfoDb
from database.models.Order import OrderDb
from database.models.Shop import ShopDb
from database.models.Swiper import SwiperDb
from database.models.Product import ProductDb, ProductCategoryDb
from database.models.Coupon import CouponDb, UserCouponDb
from database.models.PointStore import PointStoreDb
from utils.enums import ORDER_STATE
from utils.oss import upload_image

router = APIRouter(prefix='/manage')


@router.get("/shop/get")
async def get_admin_shops_api(current_admin: AdminBasicInfoModel = Depends(
    get_current_active_admin)):
    if current_admin.role == 0:
        shops = await ShopDb.get_all_shops()
    else:
        shops = [await ShopDb.get_shop_by_id(current_admin.permission)]
    return_list = []
    for shop in shops:
        swipers = await SwiperDb.get_swipers_by_shop_id(shop_id=shop.id)
        return_list.append({
            "shopId": shop.id,
            "name": shop.name,
            "address": shop.address,
            "email": shop.email,
            "phone": shop.phone,
            "announcement": shop.announcement,
            "about": shop.about,
            "swipers": swipers if swipers is not None else []
        })

    return {"shops": return_list}


@router.post("/shop/update")
async def update_shop_api(
    request: UpdateShopRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:

        return {"error": "权限不足"}

    if request.shop_id == -1:
        # Add new shop
        if await ShopDb.is_shop_exists(shop_id=request.shop_id):

            return {"error": "该店铺已存在"}
        result = await ShopDb.add_shop(name=request.shop_name,
                                       address=request.shop_address,
                                       phone=request.shop_phone,
                                       email=request.shop_email,
                                       about=request.shop_about,
                                       announcement=request.shop_announcement)
        if result is None:

            return {"error": "添加失败"}
        return {"message": "添加成功"}
    else:
        # Update shop
        result = await ShopDb.update_shop_info(
            shop_id=request.shop_id,
            name=request.shop_name,
            address=request.shop_address,
            phone=request.shop_phone,
            email=request.shop_email,
            about=request.shop_about,
            announcement=request.shop_announcement)
        if result is None:

            return {"error": "修改失败"}
        return {"message": "修改成功"}


@router.post("/swiper/add")
async def add_shop_swiper_api(
    request: AddShopSwiperRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    image_url = request.image
    if not request.image.startswith('http'):
        image_url = upload_image(request.image)
        if image_url is None:
            return {"error": "图片上传失败"}

    result = await SwiperDb.add_swiper(shop_id=request.shop_id,
                                       image=image_url)
    if result is None:
        return {"error": "添加失败"}
    return {"message": "添加成功", "swiper_id": result.id}


@router.post("/swiper/remove")
async def remove_shop_swiper_api(
    request: RemoveShopSwiperRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    swiper = await SwiperDb.get_swiper_by_id(swiper_id=request.swiper_id)
    if swiper is None:
        return {"error": "轮播图不存在"}
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != swiper.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    result = await SwiperDb.remove_swiper(swiper_id=request.swiper_id)
    if result is None:
        return {"error": "删除失败"}
    return {"message": "删除成功"}


@router.get("/order/get")
async def get_admin_orders_api(current_admin: AdminBasicInfoModel = Depends(
    get_current_active_admin)):
    if current_admin.role == 0:
        orders = await OrderDb.get_all_orders()
    else:
        orders = await OrderDb.get_orders_by_shop_id(
            shop_id=current_admin.permission)
    return_list = []
    if orders is not None:
        for order in orders[::-1]:
            return_list.append({
                "orderId":
                order.id,
                "shopId":
                order.shop_id,
                "shopName":
                order.shop_name,
                "tableId":
                order.table_id,
                "userId":
                order.user_id,
                "phone":
                order.phone,
                "orderTime":
                order.time,
                "orderState":
                order.state,
                "isTakeout":
                order.is_takeout,
                "verifyCode":
                order.verify_code,
                "comments":
                order.comments,
                "paidPrice":
                order.paid_price,
                "tag":
                ORDER_STATE[order.state],
                "products": [{
                    "id": int(x),
                    "quantity": int(y)
                } for x, y in zip(order.product_ids.split(";"),
                                  order.product_quantities.split(";"))]
            })

    return {"orders": return_list}


@router.post("/order/state/update")
async def update_order_state_api(
    request: UpdateOrderStateRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    order = await OrderDb.get_order_by_id(order_id=request.order_id)
    if order is None:
        return {"error": "订单不存在"}
    if current_admin.role != 0 and order.shop_id != current_admin.permission:
        return {"error": "非法请求"}
    if order.state == 4 and request.state == 1:
        return {"error": "订单已完成，不能取消"}
    result = await OrderDb.update_order_state(order_id=request.order_id,
                                              state=request.state)
    if result is None:
        return {"error": "修改失败"}
    return {"message": "修改成功"}


@router.get("/product/get")
async def get_admin_products_api(current_admin: AdminBasicInfoModel = Depends(
    get_current_active_admin)):
    if current_admin.role == 0:
        products = await ProductDb.get_all_products()
    else:
        products = await ProductDb.get_product_by_shop_id(
            shop_id=current_admin.permission)
    return_list = []
    if products is not None:
        for product in products:
            return_list.append({
                "productId": product.id,
                "shopId": product.shop_id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "image": product.image,
                "categoryId": product.category_id,
                "stock": product.stock
            })
    return {"products": return_list}


@router.post("/product/update")
async def update_product_api(
    request: UpdateProductRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role in [1, 2]:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    # Check if category exists
    if await ProductCategoryDb.get_category_by_id(
            category_id=request.category_id) is None:
        return {"error": "分类不存在"}

    # Upload Image
    image_url = request.product_image
    if not request.product_image.startswith('http'):
        image_url = upload_image(request.product_image)
        if image_url is None:
            return {"error": "图片上传失败"}

    product_id = request.product_id
    if request.product_id == -1:
        # Add new product
        result = await ProductDb.add_product(
            shop_id=request.shop_id,
            category_id=request.category_id,
            price=request.product_price,
            name=request.product_name,
            image=image_url,
            stock=request.product_stock,
            description=request.product_description)
        product_id = result.id
    else:
        # Update product
        result = await ProductDb.update_product(
            product_id=request.product_id,
            shop_id=request.shop_id,
            category_id=request.category_id,
            price=request.product_price,
            name=request.product_name,
            image=image_url,
            stock=request.product_stock,
            description=request.product_description)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功", "product_id": product_id}


@router.post("/product/remove")
async def remove_product_api(
    request: RemoveProductRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    product = await ProductDb.get_product_by_id(product_id=request.product_id)
    if product is None:
        return {"error": "商品不存在"}
    if current_admin.role == 0:
        pass
    elif current_admin.role in [1, 2]:
        if current_admin.permission != product.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    result = await ProductDb.remove_product(product_id=request.product_id)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功"}


@router.get("/category/get")
async def get_admin_categories_api(
        current_admin: AdminBasicInfoModel = Depends(
            get_current_active_admin)):
    if current_admin.role == 0:
        categories = await ProductCategoryDb.get_all_categories()
    else:
        categories = await ProductCategoryDb.get_category_by_shop_id(
            shop_id=current_admin.permission)
    return_list = []
    for category in categories:
        return_list.append({
            "categoryId": category.id,
            "shopId": category.shop_id,
            "name": category.name
        })
    return {"categories": return_list}


@router.post("/category/update")
async def update_product_category_api(
    request: UpdateProductCategoryRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    if request.category_id == -1:
        # Add new category
        result = await ProductCategoryDb.add_category(
            shop_id=request.shop_id, name=request.category_name)
        category_id = result.id
    else:
        # Update category
        result = await ProductCategoryDb.update_category_name(
            category_id=request.category_id, name=request.category_name)
        category_id = request.category_id
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功", "category_id": category_id}


@router.post("/category/remove")
async def remove_product_category_api(
    request: RemoveProductCategoryRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    category = await ProductCategoryDb.get_category_by_id(
        category_id=request.category_id)
    if category is None:
        return {"error": "分类不存在"}
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != category.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    # Check if any product still using this category
    if await ProductDb.is_category_id_exist(category_id=request.category_id):
        return {"error": "该分类下还有商品，不能删除"}

    result = await ProductCategoryDb.remove_category(
        category_id=request.category_id)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功"}


@router.get("/user/get")
async def get_admin_basic_info_api(
        current_admin: AdminBasicInfoModel = Depends(
            get_current_active_admin)):
    if current_admin.role > 1:
        return {"error": "权限不足"}

    users = await AdminInfoDb.get_admins_by_role_and_permission(
        role=current_admin.role, permission=current_admin.permission)
    return_list = []
    for user in users:
        return_list.append({
            "userId": user.id,
            "nickname": user.nickname,
            "phone": user.phone,
            "role": user.role,
            "permission": user.permission
        })

    return {"users": return_list}


@router.post("/user/update")
async def add_admin_user_api(
    request: UpdateAdminUserRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role not in [0, 1]:
        return {"error": "权限不足"}
    if request.role != 0 and request.role < current_admin.role:
        return {"error": "只能编辑比自己权限低的用户"}
    if not await ShopDb.is_shop_exists(shop_id=request.permission):
        return {"error": "该店铺不存在"}
    is_shop_exists = await AdminInfoDb.is_user_exists(phone=request.phone)
    if request.user_id == -1:
        # Add new user
        if is_shop_exists:
            return {"error": "该手机号已存在"}
        result = await AdminInfoDb.add_admin(nickname=request.username,
                                             role=request.role,
                                             permission=request.permission,
                                             phone=request.phone,
                                             password=request.password)
    else:
        # Update user
        if not is_shop_exists:
            return {"error": "该用户不存在"}
        result = await AdminInfoDb.update_admin_info(
            id=request.user_id,
            phone=request.phone,
            nickname=request.username,
            role=request.role,
            permission=request.permission,
            password=request.password)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功"}


@router.post("/user/remove")
async def remove_admin_user_api(
    request: RemoveAdminUserRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role not in [0, 1]:
        return {"error": "权限不足"}
    if request.user_id == current_admin.user_id:
        return {"error": "不能删除自己"}
    user = await AdminInfoDb.get_admin_by_uid(user_id=request.user_id)
    if user is None:
        return {"error": "用户不存在"}
    if user.role == 0:
        return {"error": "不能删除超级管理员"}
    if user.role < current_admin.role:
        return {"error": "只能删除比自己权限低的用户"}
    result = await AdminInfoDb.remove_admin(phone=user.phone)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功"}


@router.get("/coupon/get")
async def get_admin_coupons_api(current_admin: AdminBasicInfoModel = Depends(
    get_current_active_admin)):
    if current_admin.role == 0:
        coupons = await CouponDb.get_all_user_coupons()
    else:
        coupons = await CouponDb.get_coupons_by_shop_id(
            shop_id=current_admin.permission)
    return_list = []
    if coupons is not None:
        for coupon in coupons:
            return_list.append({
                "couponId":
                coupon.id,
                "shopId":
                coupon.shop_id,
                "name":
                coupon.name,
                "threshold":
                coupon.threshold,
                "discount":
                coupon.discount,
                "discountPercentage":
                coupon.discount_percentage,
                "type":
                "优惠金额" if coupon.discount is not None else "优惠百分比",
                "validDate":
                coupon.valid_date.strftime("%Y-%m-%d")
            })
    return {"coupons": return_list}


@router.post("/coupon/create")
async def create_coupon_api(
    request: CreateCouponRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    if request.discount is None and request.discount_percentage is None:
        return {"error": "优惠金额和优惠百分比不能同时为空"}

    result = await CouponDb.create_coupon(
        name=request.name,
        shop_id=request.shop_id,
        valid_date=datetime.fromisoformat(
            request.valid_date.replace(
                "Z", "+00:00")).replace(tzinfo=timezone.utc).date(),
        threshold=request.threshold,
        discount=request.discount,
        discount_percentage=request.discount_percentage)

    if result is None:
        return {"error": "操作失败"}
    return {
        "message": "操作成功",
        "coupon_id": result.id,
        "type": "优惠金额" if result.discount is not None else "优惠百分比",
        "valid_date": result.valid_date.strftime("%Y-%m-%d")
    }


@router.post("/coupon/remove")
async def remove_coupon_api(
    request: RemoveCouponRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    coupon = await CouponDb.get_coupon_by_id(coupon_id=request.coupon_id)
    if coupon is None:
        return {"error": "优惠券不存在"}
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != coupon.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}
    await UserCouponDb.remove_coupon_users(coupon_id=request.coupon_id)
    result = await CouponDb.remove_coupon(coupon_id=request.coupon_id)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功"}


@router.post("/coupon/gift")
async def gift_coupon_api(
    request: GiftCouponRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}
    coupon = await CouponDb.get_coupon_by_id(coupon_id=request.coupon_id)
    if coupon is None:
        return {"error": "优惠券不存在"}
    if coupon.shop_id != request.shop_id:
        return {"error": "非法请求"}
    if request.gift_all:
        users = await UserInfoDb.get_all_users()
        if users is None:
            return {"error": "没有用户"}
        result = True
        for user in users:
            for _ in range(request.quantity):
                temp = await UserCouponDb.add_user_coupon(
                    coupon_id=request.coupon_id, user_id=user.id)
                result = result and (temp is not None)
        if not result:
            return {"error": "操作失败"}
        return {"message": "操作成功"}
    else:
        user = await UserInfoDb.get_user_by_phone(phone=int(request.phone))
        if user is None:
            return {"error": "用户不存在"}
        result = True
        for _ in range(request.quantity):
            temp = await UserCouponDb.add_user_coupon(
                coupon_id=request.coupon_id, user_id=user.id)
            result = result and (temp is not None)
        if not result:
            return {"error": "操作失败"}
        return {"message": "操作成功"}


@router.get("/point-store/get")
async def get_point_store_api(current_admin: AdminBasicInfoModel = Depends(
    get_current_active_admin)):
    if current_admin.role == 0:
        point_store = await PointStoreDb.get_all_items()
    else:
        point_store = await PointStoreDb.get_items_by_shop_id(
            shop_id=current_admin.permission)
    return_list = []
    if point_store is not None:
        for item in point_store:
            return_list.append({
                "itemId": item.id,
                "shopId": item.shop_id,
                "type": item.type,
                "name": item.name,
                "image": item.image,
                "price": item.price,
                "stock": item.stock,
                "description": item.description
            })
    return {"items": return_list}


@router.post("/point-store/update")
async def update_point_store_item_api(
    request: UpdatePointStoreItemRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != request.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    # Upload Image
    image_url = request.item_image
    if not request.item_image.startswith('http'):
        image_url = upload_image(request.item_image)
        if image_url is None:
            return {"error": "图片上传失败"}

    item_id = request.item_id
    if request.item_id == -1:
        # Add new item
        result = await PointStoreDb.add_item(
            shop_id=request.shop_id,
            price=request.item_price,
            type=request.item_type,
            name=request.item_name,
            image=image_url,
            stock=request.item_stock,
            description=request.item_description)
        item_id = result.id
    else:
        # Update item
        result = await PointStoreDb.update_item(
            item_id=request.item_id,
            price=request.item_price,
            type=request.item_type,
            name=request.item_name,
            image=image_url,
            stock=request.item_stock,
            description=request.item_description)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功", "item_id": item_id}


@router.post("/point-store/remove")
async def remove_point_store_item_api(
    request: RemovePointStoreItemRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    item = await PointStoreDb.get_item_by_id(item_id=request.item_id)
    if item is None:
        return {"error": "商品不存在"}
    if current_admin.role == 0:
        pass
    elif current_admin.role == 1:
        if current_admin.permission != item.shop_id:
            return {"error": "权限不足"}
    else:
        return {"error": "权限不足"}

    result = await PointStoreDb.remove_item(item_id=request.item_id)
    if result is None:
        return {"error": "操作失败"}
    return {"message": "操作成功"}
