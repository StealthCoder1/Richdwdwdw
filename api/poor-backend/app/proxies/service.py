from datetime import datetime

import msgspec
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.database import execute, fetch_all, fetch_one
from app.proxies.models import Proxy
from app.proxies.schemas import ProxiesUploadRequest, Service
from app.proxies.utils import validate_proxy_urls
from app.rabbitmq import rabbitmq
from app.rediss import redis
from app.tasks import service as tasks_service
from app.websocket.connection_manager import manager


async def upload_proxies(proxies: list[str]):
    # proxy_urls = validate_proxy_urls(data.type, data.proxies)

    db_proxies = await get_proxies_by_url(proxies)

    to_insert = []

    for proxy in proxies:
        exists = next((x for x in db_proxies if x["url"] == proxy), None)

        if not exists:
            to_insert.append({"url": proxy})

    if len(to_insert) != 0:
        db_proxies.extend(await create_proxies(to_insert))

    return db_proxies


async def get_proxy_ids(user_id: int, service: Service):
    return [
        int(id)
        for id in await redis.client.lrange(f"proxies:{user_id}:{str(service)}", 0, -1)
    ]


async def get_proxies_by_url(urls: list[str]):
    select_query = select(Proxy).where(Proxy.url.in_(urls))

    return await fetch_all(select_query)


async def get_proxies_by_ids(ids: list[int]):
    select_query = select(Proxy).where(Proxy.id.in_(ids))

    return await fetch_all(select_query)


async def create_proxies(proxies: list[dict]):
    insert_query = (
        insert(Proxy).values(proxies).on_conflict_do_nothing().returning(Proxy)
    )

    return await fetch_all(insert_query)


async def get_proxy_by_id(proxy_id: int):
    select_query = select(Proxy).where(Proxy.id == proxy_id)

    return await fetch_one(select_query)


async def update_proxy_by_id(proxy_id: int, values: dict):
    update_query = update(Proxy).where(Proxy.id == proxy_id).values(values)

    return await execute(update_query)


async def on_update_status(data, task_id):
    task = await tasks_service.get_task(task_id)

    proxy = await get_proxy_by_id(data["id"])

    for client in manager.clients:
        if client.user_id != task.user_id:
            continue

        # await client.send_event("update_proxy_status", data)

        await client.send_event(
            "log",
            {
                "service": "telegram",
                "data": {
                    "type": "authorization",
                    "text": f"{data['latency'] == -1 and 'invalid' or 'valid'} proxy {proxy['url']}. latency = {data['latency']}",
                },
            },
        )

    await update_proxy_by_id(
        data["id"], {"latency": data["latency"], "last_checked_at": datetime.utcnow()}
    )


async def on_task_completed(data):
    await tasks_service.set_task_status(data["task_id"], "completed")

    task = await tasks_service.get_task(data["task_id"])

    # print("completed", data["data"])

    await redis.client.hset(
        f"sessions:{task.service}:{task.user_id}",
        "proxies",
        msgspec.json.encode(data["data"]),
    )

    # check scheduled

    await tasks_service.remove_task(task.id)


async def on_update(data):
    task = await tasks_service.get_task(data["task_id"])

    if not task:
        pass

    proxy = await get_proxy_by_id(data["data"]["id"])

    for client in manager.clients:
        if client.user_id != task.user_id:
            continue

        await client.send_event(
            "log",
            {
                "service": task.service,
                "data": {
                    "type": "proxy",
                    "text": f"{data['data']['latency'] == -1 and 'invalid' or 'valid'} proxy {proxy['url']}. latency = {data['data']['latency']}",
                },
            },
        )

    # add to redis?

    await update_proxy_by_id(
        data["data"]["id"],
        {"latency": data["data"]["latency"], "last_checked_at": datetime.utcnow()},
    )
