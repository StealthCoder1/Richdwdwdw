from app.products import service
from app.products.exceptions import ProductNotFound
from app.products.schemas import ProductssGetByIdRequest


async def valid_product_id(data: ProductssGetByIdRequest):
    product = await service.get_product_by_id(data.license_id)

    if not product:
        raise ProductNotFound()

    return product
