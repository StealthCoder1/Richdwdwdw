from fastapi import APIRouter, Depends

from app.auth.jwt import UserDependency, parse_jwt_user_data
from app.products import service
from app.products.dependencies import valid_product_id
from app.products.models import Product
from app.products.schemas import ProductSchema
from app.utils.schemas import APISuccess, create_response

router = APIRouter(tags=["Products"], dependencies=[Depends(parse_jwt_user_data)])


@router.post("/products.get", response_model=APISuccess[list[ProductSchema]])
async def get():
    return create_response(await service.get_products())


@router.post("/products.getById", response_model=APISuccess[ProductSchema])
async def get_by_id(product: Product = Depends(valid_product_id)):
    return create_response(product)


@router.post("/products.buy", response_model=APISuccess[bool])
async def buy(user: UserDependency, product: Product = Depends(valid_product_id)):
    await service.buy(product, user)

    return create_response(True)
