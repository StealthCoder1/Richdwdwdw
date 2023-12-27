from fastapi import APIRouter, Depends

from app.auth.jwt import parse_jwt_user_data
from app.utils.schemas import APISuccess

router = APIRouter(tags=["Services"], dependencies=[Depends(parse_jwt_user_data)])


@router.post("/services.createTask", response_model=APISuccess)
async def create_task():
    pass

