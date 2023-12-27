from pydantic import BaseModel

from app.products.constants import ProductType


class ProductSchema(BaseModel):
    id: int

    name: str
    description: str | None
    price: int
    images: list[str] | None
    type: ProductType
    payload: dict


class ProductssGetByIdRequest(BaseModel):
    license_id: int


# class UserLicenseSchema(BaseModel):
#     license_id: int
#     expires_at: int
