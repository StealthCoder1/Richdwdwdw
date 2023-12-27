from fastapi import APIRouter, Depends

from app.auth.jwt import JWTUserDataDependency, parse_jwt_user_data
from app.payments.schemas import CreateInvoice, Invoice
from app.utils.schemas import APISuccess, create_response

router = APIRouter(tags=["Payments"], dependencies=[Depends(parse_jwt_user_data)])


@router.post("/payments.createInvoice", response_model=APISuccess[Invoice])
async def create_invoice(data: CreateInvoice, jwt_user_data: JWTUserDataDependency):
    return create_response(
        Invoice(
            invoice_url=f"https://payment.lua.cx/?payment_system={data.payment_system}&amount={data.amount}&user_id={jwt_user_data.user_id}"
        )
    )
