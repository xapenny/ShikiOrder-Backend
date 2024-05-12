from models.UserInfoModel import UserBasicInfoModel
from fastapi import APIRouter, Depends, Response, status
from dependencies import get_current_active_user
from database.models.Product import ProductCategoryDb, ProductDb

router = APIRouter()


@router.get("/product")
async def getProductInfoApi(
    shop: int,
    response: Response,
    _: UserBasicInfoModel = Depends(get_current_active_user)):
    product_category = await ProductCategoryDb.get_category_by_shop_id(shop)
    if product_category is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "No category found"}
    result_all = []
    result_category = []
    for category in product_category:
        cat_products = await ProductDb.get_product_by_category_id(category.id)
        if cat_products is not None:
            children = []
            for product in cat_products:
                info = {
                    "id": product.id,
                    "catId": category.id,
                    "catName": category.name,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image,
                    "stock": product.stock,
                    "description": product.description
                }
                children.append(info)
                result_all.append(info)
            result_category.append({
                "id": category.id,
                "catName": category.name,
                "children": children
            })
    return {"all": result_all, "category": result_category}
