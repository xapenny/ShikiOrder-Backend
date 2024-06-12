from datetime import timedelta, datetime

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from dependencies_admin import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                create_access_token, get_current_active_admin)
from models.AdminModel import AdminBasicInfoModel, AdminUpdatePasswordRequestModel, AdminUpdateInfoRequestModel
from dependencies_admin import authenticate_user
from database.models.AdminInfo import AdminInfoDb
from database.models.Order import OrderDb
from database.models.Shop import ShopDb
from .AdminManageApi import router as admin_manage_router

router = APIRouter(prefix='/admin')
router.include_router(admin_manage_router)


@router.post("/login")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()):
    if not (form_data.username.isdigit() and len(form_data.username) == 11):
        return {"error": "手机号不正确"}
    user = await authenticate_user(form_data.username, form_data.password)
    if user is None:
        return {"error": "账号或密码不正确"}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"phone": user.phone},
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/info", response_model=AdminBasicInfoModel)
async def get_admin_basic_info_api(
        current_admin: AdminBasicInfoModel = Depends(
            get_current_active_admin)):
    return current_admin


@router.post("/password")
async def change_admin_password_api(
    request: AdminUpdatePasswordRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if len(request.new_password) != 32:
        return {"error": "非法请求"}
    result = await AdminInfoDb.update_admin_info(id=current_admin.user_id,
                                                 password=request.new_password)
    if result is None:
        return {"error": "修改失败"}
    return {"message": "修改成功"}


@router.post("/update")
async def update_admin_info_api(
    request: AdminUpdateInfoRequestModel,
    current_admin: AdminBasicInfoModel = Depends(get_current_active_admin)):
    if request.nickname == "":
        return {"error": "昵称不能为空"}
    if request.phone < 13000000000 or request.phone > 19299999999:
        return {"error": "手机号格式不正确"}
    result = await AdminInfoDb.update_admin_info(id=current_admin.user_id,
                                                 phone=request.phone,
                                                 nickname=request.nickname)
    if result is None:
        return {"error": "修改失败"}
    return {"message": "修改成功"}


@router.get("/dashboard")
async def get_dashboard_info_api(current_admin: AdminBasicInfoModel = Depends(
    get_current_active_admin)):
    shops = []
    if current_admin.role == 0:
        shops = await ShopDb.get_all_shops()
    else:
        shops = [await ShopDb.get_shop_by_id(current_admin.permission)]
    if shops is None:
        return {"error": "获取店铺信息失败"}

    # Initialize dashboard data
    pending_orders = 0
    finished_orders = 0
    canceled_orders = 0
    today_income = 0
    today_active_users = set()
    today_dealed_orders = 0
    month_income = 0
    month_active_users = set()
    month_dealed_orders = 0
    # Get orders from all shops
    all_orders: list[OrderDb] = []
    for shop in shops:
        shop_orders = await OrderDb.get_orders_by_shop_id(page_size=10000,
                                                          offset=0,
                                                          shop_id=shop.id)
        if shop_orders is not None:
            all_orders.extend(shop_orders)
    # Calculate dashboard data
    for order in all_orders:
        # Current pending orders
        if order.state == 2:
            pending_orders += 1
        # Calculate today
        if order.time.date() == datetime.today().date():
            # Check order state
            if order.state == 1:
                canceled_orders += 1
            elif order.state > 2:
                if order.state == 4:
                    finished_orders += 1
                today_dealed_orders += 1
                # Calculate today income
                today_income += order.paid_price
            # Collect today active users
            today_active_users.add(order.user_id)
        elif order.time >= datetime.today() - timedelta(days=30):
            # Collect month active users
            month_active_users.add(order.user_id)
            # Check order state
            if order.state > 2:
                # Calculate month income
                month_income += order.paid_price
                month_dealed_orders += 1
    return {
        "pendingOrders": pending_orders,
        "finishedOrders": finished_orders,
        "canceledOrders": canceled_orders,
        "todayIncome": today_income,
        "todayActiveUsers": len(today_active_users),
        "todayDealedOrders": today_dealed_orders,
        "monthIncome": month_income,
        "monthActiveUsers": len(month_active_users),
        "monthDealedOrders": month_dealed_orders
    }
