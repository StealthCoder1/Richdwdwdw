
from sqlalchemy import select

from app.database import fetch_all, fetch_one
from app.products.constants import ProductType
from app.products.exceptions import InsufficientFunds
from app.products.models import Product
from app.transactions.constants import PaymentCategory, PaymentMethod
from app.users import service as users_service
from app.users.models import User
from app.transactions import service as transactions_service


async def get_products():
    select_query = select(Product)

    return await fetch_all(select_query)


async def get_product_by_id(product_id: int):
    select_query = select(Product).where(Product.id == product_id)

    return await fetch_one(select_query)


async def buy(product: Product, user: User):
    if user.balance < product.price:
        raise InsufficientFunds()

    await users_service.take_user_balance(user.id, product.price)

    await transactions_service.create_transaction(
        {
            "amount": product.price,
            "sender_id": user.id,
            "category": PaymentCategory.PURCHASE,
            "payment_method": PaymentMethod.BALANCE,
            "payload": { "type": "product", "data": { "id": product.id }},
        }
    )

    if product.type == ProductType.LICENSE:
        await users_service.give_user_license(
            user.id, product.payload["id"], product.payload["duration"]
        )
    else:
        print("wtf")
