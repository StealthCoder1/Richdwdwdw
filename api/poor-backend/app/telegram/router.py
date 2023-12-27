from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import Json

from app.auth.jwt import JWTUserDataDependency, parse_jwt_user_data
from app.rabbitmq import rabbitmq
from app.rediss import redis
from app.telegram import service
from app.telegram.dependencies import has_valid_license
from app.telegram.schemas import (
    CreateAuthorizationTask,
    CreateFirstMessagerTask,
    CreateInviterTask,
    CreateMailerTask,
    GetTaskRequest,
    StopTaskRequest,
)
from app.utils.schemas import APISuccess, create_response

router = APIRouter(tags=["Telegram"], dependencies=[Depends(parse_jwt_user_data), Depends(has_valid_license)])


@router.post("/telegram.createTask", response_model=APISuccess[None])
async def create_task(
    task: Annotated[
        Json[
            CreateAuthorizationTask
            | CreateInviterTask
            | CreateMailerTask
            | CreateFirstMessagerTask
        ],
        Form(),
    ],
    jwt_user_data: JWTUserDataDependency,
    files: Annotated[list[UploadFile], File()] = None,
):
    await service.handle_create_task(task, files, jwt_user_data.user_id)

    return create_response(None)


@router.post("/telegram.getTask", response_model=APISuccess[bool])
async def get_task(data: GetTaskRequest, jwt_user_data: JWTUserDataDependency):
    session_id = str(jwt_user_data.user_id)

    task = await service.get_task(session_id, str(data.type))

    return create_response(task)


@router.post("/telegram.terminateTask", response_model=APISuccess[bool])
async def terminate_task(data: StopTaskRequest, jwt_user_data: JWTUserDataDependency):
    session_id = str(jwt_user_data.user_id)

    await rabbitmq.rpc.call(
        "telegram.terminateTask", dict(session_id=session_id, type=str(data.type))
    )

    return create_response(True)
