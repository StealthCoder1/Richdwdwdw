import sys
sys.path.append("/run/media/drochilla/FCECA718ECA6CC68/comp/programing/Python/frilanse/RichSIte/poop/poor-backend/")

from contextlib import asynccontextmanager
from aio_pika import ExchangeType

import msgspec
from aio_pika.abc import AbstractIncomingMessage
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.account.router import router as account_router
from app.auth.router import router as auth_router
from app.config import app_configs
from app.internal.router import router as internal_router
from app.payments.router import router as payments_router
from app.products.router import router as products_router
from app.proxies import service as proxies_service
# from app.proxies.router import router as proxies_router
from app.rabbitmq import rabbitmq
from app.rediss import redis
from app.telegram import service as telegram_service
from app.telegram.router import router as telegram_router
from app.users.router import router as users_router
from app.websocket.router import router as websocket_router


async def on_message(incoming_message: AbstractIncomingMessage):
    async with incoming_message.process():
        message = msgspec.msgpack.decode(incoming_message.body)

        if message["action"] == "telegram.data":
            await telegram_service.on_data(message["data"])
        if message["action"] == "telegram.taskCompleted":
            await telegram_service.on_task_completed(message)
        elif message["action"] == "proxies.taskCompleted":
            await proxies_service.on_task_completed(message)
        elif message["action"] == "proxies.update":
            await proxies_service.on_update(message)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with redis:
        async with rabbitmq:
            # queue = await rabbitmq.channel.declare_queue("api")

            # await queue.bind(rabbitmq.exchange, queue.name)
            # await queue.consume(on_message)

            logs_exchange = await rabbitmq.channel.declare_exchange(
                "api", ExchangeType.FANOUT
            )

            queue = await rabbitmq.channel.declare_queue(exclusive=True)

            await queue.bind(logs_exchange)

            await queue.consume(on_message)

            yield


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event('startup')
# async def on_event_startup() -> None:
#     print("Executing startup event")
#     # Дополнительный код
#
# @app.on_event('shutdown')
# async def on_event_shutdown() -> None:
#     print("Executing shutdown event")
#     # Дополнительный код



@app.exception_handler(StarletteHTTPException)
async def api_exception_handler(
    request: Request, exception: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        {
            "ok": False,
            "error_code": exception.status_code,
            "error_description": exception.detail,
        },
        exception.status_code,
    )


app.include_router(account_router)
app.include_router(auth_router)
app.include_router(internal_router)
app.include_router(products_router)
app.include_router(users_router)
#app.include_router(proxies_router)
app.include_router(telegram_router)
app.include_router(payments_router)
app.include_router(websocket_router)
