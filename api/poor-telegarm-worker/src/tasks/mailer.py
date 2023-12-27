import asyncio
import random

from typing import Any, TypedDict

from pyrogram import types
from pyrogram.errors import UserAlreadyParticipant, FloodWait

from src.constants import LogLevel, Messages
from src.custom_client import CustomClient
from src.functions import Function
from src.schemas import MailerTaskData, MessagesBlock
from src.sessions_hub import SessionTask
from src.utils import Link, format_additional_error_info


class SessionMailerStorage(TypedDict):
    chat_ids_queue: asyncio.Queue[int | str]
    spammed: list[int | str]


class SessionMailerTask(SessionTask):
    storage: SessionMailerStorage


async def pool(task: SessionMailerTask, client: CustomClient, data: MailerTaskData):
    chat_ids_queue = task.storage["chat_ids_queue"]

    sent_messages = 0

    function = Function(task, client)

    items: list[list[int] | int] = []

    if data.config.forward:
        for block in data.config.items:
            if isinstance(block, MessagesBlock):
                message_ids: list[int] = []

                for message in block.messages:
                    try:
                        sent_message = await function.send_one_message(
                            "me", message.media, message.text
                        )

                        if sent_message:
                            message_ids.append(sent_message.id)

                            await task.increase_counter("success")
                            await task.send_log(
                                LogLevel.INFO,
                                Messages.MESSAGE_SENT.format("в Избранное"),
                            )
                        else:
                            await task.increase_counter("error")
                            await task.send_log(
                                LogLevel.ERROR,
                                Messages.FAILED_SEND_MESSAGE.format("в Избранное", ""),
                            )
                    except Exception as exception:
                        await task.increase_counter("error")

                        await task.send_log(
                            LogLevel.ERROR,
                            Messages.FAILED_SEND_MESSAGE.format(
                                "в Избранное", format_additional_error_info(exception)
                            ),
                        )

                items.append(message_ids)
            else:  # cooldown
                items.append(block.cooldown)

    while not chat_ids_queue.empty():
        try:
            chat_id = chat_ids_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        if chat_id in task.storage["spammed"]:
            continue

        if data.config.limit != 0 and sent_messages >= data.config.limit:
            await task.send_log(LogLevel.ERROR, Messages.LIMIT_REACHED)

            chat_ids_queue.put_nowait(chat_id)

            break

        link = Link.parse(str(chat_id))

        chat = None

        if data.config.add_to_contacts is None:
            try:
                chat = await client.join_chat(link.get_short())

                await task.increase_counter("success")
                await task.send_log(LogLevel.INFO, Messages.JOINED_CHAT.format(link))
            except Exception as exception:
                if isinstance(exception, UserAlreadyParticipant):
                    chat = await client.get_chat(link.get_short())

                    if isinstance(chat, types.ChatPreview):
                        # User Already Participant, but Telegram returned Chat Preview o_O

                        continue
                else:
                    await task.increase_counter("error")
                    await task.send_log(
                        LogLevel.ERROR,
                        Messages.FAILED_JOIN_CHAT.format(
                            link, format_additional_error_info(exception)
                        ),
                    )

                    continue

        try:
            if data.config.forward:
                for item in items:
                    if isinstance(item, int):
                        # cooldown

                        await asyncio.sleep(item)
                    else:
                        message_id = random.choice(item)

                        #if data.config.add_to_contacts is True:
                        #    await function.add_to_contacts(link.data)

                        await client.forward_messages(
                            chat.id if chat else link.data, "me", message_id
                        )
            else:
                await function.send_message(chat.id if chat else link.data, data.config)

            async with task.lock_storage:
                task.storage["spammed"].append(chat_id)

            sent_messages = sent_messages + 1

            await task.increase_counter("success")
            await task.send_log(LogLevel.INFO, Messages.MESSAGE_SENT.format(link))
        except Exception as exception:
            seconds = 0

            if isinstance(exception, FloodWait):
                chat_ids_queue.put_nowait(chat_id)

                seconds = exception.value

            await task.increase_counter("error")
            await task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_SEND_MESSAGE.format(
                    link, format_additional_error_info(exception)
                ),
            )

            await asyncio.sleep(seconds)

        await asyncio.sleep(data.config.delay)


async def run(task: SessionTask, obj: Any):
    data = MailerTaskData.model_validate(obj)

    clients = task.get_session_clients()

    chat_ids_queue = asyncio.Queue[int | str]()

    for chat_id in data.chat_ids:
        chat_ids_queue.put_nowait(chat_id)

    async with task.lock_storage:
        task.storage = {
            "spammed": [],
            "chat_ids_queue": chat_ids_queue,
        }

    await asyncio.gather(*[pool(task, client, data) for client in clients])
