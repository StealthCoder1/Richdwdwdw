import asyncio

from typing import Any, TypedDict

from pyrogram import filters, types, enums
from pyrogram.errors import FloodWait, UserAlreadyParticipant

from src.constants import LogLevel, Messages
from src.custom_client import CustomClient
from src.functions import Function
from src.schemas import FirstMessagerTaskData
from src.sessions_hub import SessionTask
from src.utils import Link, format_additional_error_info


class SessionFirstMessagerStorage(TypedDict):
    post_ids: list[int]


class SessionFirstMessagerTask(SessionTask):
    storage: SessionFirstMessagerStorage


async def pool(
    task: SessionFirstMessagerTask, client: CustomClient, data: FirstMessagerTaskData
):
    data.config.add_to_contacts = None

    sent_messages = 0

    function = Function(task, client)

    chats: dict[int, types.Chat] = {}

    for chat_id in data.chat_ids:
        link = Link.parse(chat_id)

        try:
            chat = await client.join_chat(link.get_short())

            if chat.type != enums.ChatType.CHANNEL:
                await task.send_log(
                    LogLevel.WARN, Messages.CHAT_NOT_CHANNEL.format(link)
                )

            chats[chat.id] = chat

            await task.increase_counter("success")
            await task.send_log(LogLevel.INFO, Messages.JOINED_CHANNEL.format(link))
        except Exception as exception:
            if isinstance(exception, UserAlreadyParticipant):
                chat = await client.get_chat(link.get_short())

                if isinstance(chat, types.ChatPreview):
                    # User Already Participant, but Telegram returned Chat Preview o_O

                    continue

                chats[chat.id] = chat
            else:
                await task.increase_counter("error")
                await task.send_log(
                    LogLevel.ERROR,
                    Messages.FAILED_JOIN_CHANNEL.format(
                        link, format_additional_error_info(exception)
                    ),
                )

                continue

    chat_ids = list(chats.keys())

    # https://docs.pyrogram.org/api/decorators#pyrogram.Client.on_message
    # https://docs.pyrogram.org/api/filters#module-pyrogram.filters
    @client.on_message(filters.chat(chat_ids))
    async def _(_, message: types.Message):
        nonlocal sent_messages

        await task.send_log(
            LogLevel.DEBUG,
            Messages.NEW_CHANNEL_POST.format(message.chat.title),
        )

        if message.id in task.storage["post_ids"]:
            return

        async with task.lock_storage:
            task.storage["post_ids"].append(message.id)

        if data.config.limit != 0 and sent_messages >= data.config.limit:
            await task.send_log(LogLevel.ERROR, Messages.LIMIT_REACHED)

            return

        try:
            comment = await client.get_discussion_message(message.chat.id, message.id)

            await function.send_message(comment.chat.id, data.config, comment.id)

            sent_messages += 1

            await task.increase_counter("success")
            await task.send_log(
                LogLevel.INFO,
                Messages.COMMENTED_IN_CHANNEL.format(message.chat.title),
            )
        except Exception as exception:
            seconds = 0

            if isinstance(exception, FloodWait):
                async with task.lock_storage:
                    task.storage["post_ids"].pop(message.id)

                seconds = exception.value

            await task.increase_counter("error")
            await task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_COMMENT.format(
                    message.chat.title, format_additional_error_info(exception)
                ),
            )

            await asyncio.sleep(seconds)


async def run(task: SessionTask, obj: Any):
    data = FirstMessagerTaskData.model_validate(obj)

    clients = task.get_session_clients()

    async with task.lock_storage:
        task.storage = {"post_ids": []}

    await asyncio.gather(*[pool(task, client, data) for client in clients])
