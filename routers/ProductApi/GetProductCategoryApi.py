from models.UserInfoModel import UserBasicInfoModel
from fastapi import APIRouter, Depends
from dependencies import get_current_active_user
from database.models.Product import ProductCategoryDb, ProductDb

router = APIRouter()


@router.get("/category")
async def getUserBasicInfoApi(
    shop: int,
    current_user: UserBasicInfoModel = Depends(get_current_active_user)):
    product_category = await ProductCategoryDb.get_category_by_shop_id(shop)
    if product_category is None:
        return {"error": "No category found"}
    result = []
    for category in product_category:
        cat_products = await ProductDb.get_product_by_category_id(category.id)
        if cat_products is not None:
            children = []
            for product in cat_products:
                children.append({
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image,
                    "stock": product.stock,
                    "description": product.description
                })
            result.append({
                "id": category.id,
                "catName": category.name,
                "children": children
            })
    return result
