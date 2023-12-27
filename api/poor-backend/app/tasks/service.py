from pydantic import BaseModel

from app.rediss import redis


class Task(BaseModel):
    id: str
    service: str
    user_id: int
    name: str
    status: str


async def create_task(name: str, user_id: int, service: str, task_id: str):
    await redis.client.hset(
        f"task:{task_id}",
        mapping=dict(service=service, user_id=user_id, name=name, status="running"),
    )

    return await get_task(task_id)


async def get_task(task_id: str):
    result = await redis.client.hgetall(
        f"task:{task_id}",
    )

    if "service" not in result:
        return None

    return Task(**result, id=task_id)


async def remove_task(task_id: str) -> None:
    await redis.client.delete(f"task:{task_id}")


async def set_task_status(task_id: str, status: str):
    await redis.client.hset(f"task:{task_id}", "status", status)
