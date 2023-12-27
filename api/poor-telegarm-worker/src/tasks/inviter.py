import asyncio

from typing import Any, TypedDict

from pyrogram.errors import UserAlreadyParticipant
from pyrogram import types

from src.constants import LogLevel, Messages
from src.custom_client import CustomClient
from src.functions import Function
from src.schemas import InviterTaskData
from src.sessions_hub import SessionTask
from src.utils import Link, format_additional_error_info
from src.bot import bot


class SessionInviterStorage(TypedDict):
    user_ids_queue: asyncio.Queue[int | str]


class SessionInviterTask(SessionTask):
    storage: SessionInviterStorage


async def pool(task: SessionInviterTask, client: CustomClient, data: InviterTaskData):
    user_ids_queue = task.storage["user_ids_queue"]

    link = Link.parse(data.chat_id)

    function = Function(task, client)

    try:
        chat = await client.join_chat(link.get_short())

        await task.increase_counter("success")
        await task.send_log(LogLevel.INFO, Messages.JOINED_CHAT.format(link))
    except Exception as exception:
        if isinstance(exception, UserAlreadyParticipant):
            chat = await client.get_chat(link.get_short())

            if isinstance(chat, types.ChatPreview):
                # User Already Participant, but Telegram returned Chat Preview o_O

                return
        else:
            await task.increase_counter("error")
            await task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_JOIN_CHAT.format(
                    link, format_additional_error_info(exception)
                ),
            )

            return

    async with task.lock_storage:
        if not task.storage.get("permissions_ok"):
            try:
                me = await bot.get_me()
            except Exception:
                await task.send_log(LogLevel.ERROR, Messages.INTERNAL_ERROR)

                return

            try:
                chat_administrators = await bot.get_chat_administrators(chat.id)
            except Exception:
                await task.send_log(
                    LogLevel.ERROR,
                    Messages.FAILED_GET_CHAT_ADMINISTRATORS.format(me.username),
                )

                return

            has_permissions = await bot.check_permissions(chat_administrators)

            if not has_permissions:
                await task.send_log(
                    LogLevel.ERROR,
                    Messages.FAILED_CHECK_PERMISSIONS.format(me.username),
                )

                return

            task.storage["permissions_ok"] = True

    if not client.me:
        try:
            client.me = await client.get_me()
        except Exception as exception:
            await task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_GET_ME.format(format_additional_error_info(exception)),
            )

            return

    async with task.lock_storage:
        if not task.storage.get("permissions_ok"):
            return

    try:
        await bot.promote_chat_member(chat.id, client.me.id, can_invite_users=True)

        full_name = client.me.first_name

        if client.me.last_name:
            full_name += " " + client.me.last_name

        await task.send_log(LogLevel.INFO, Messages.MEMBER_PROMOTED.format(full_name))
    except Exception:
        await task.send_log(LogLevel.ERROR, Messages.FAILED_PROMOTE_MEMBER)

    # peer = await client.resolve_peer(chat.id)

    # users_per_invite = 1 if isinstance(peer, InputPeerChat) else 200

    users_per_invite = 1

    while not user_ids_queue.empty():
        user_ids: list[int | str] = []

        for _ in range(users_per_invite):
            try:
                user_ids.append(user_ids_queue.get_nowait())
            except asyncio.QueueEmpty:
                pass

        if len(user_ids) == 0:
            break

        try:
            #if users_per_invite == 1:
            #    await function.add_to_contacts(user_ids[0])

            # user_ids_resolved = []

            # for user_id in user_ids:
            #     try:
            #         user_link = Link.parse(user_id)

            #         peer = await client.resolve_peer(user_link.data)

            #         if isinstance(peer, (raw.types.InputPeerUser, raw.base.InputUser)):
            #             user_ids_resolved.append(peer)
            #     except Exception as exception:
            #         print(exception)

            #         pass

            # print(user_ids_resolved)

            # if users_per_invite == 1:
            #     await client.add_chat_members(chat.id, user_ids_resolved)
            # else:
            #     await client.invoke(
            #         raw.functions.channels.InviteToChannel(
            #             channel=await client.resolve_peer(chat.id),
            #             users=user_ids_resolved,
            #         )
            #     )

            await client.add_chat_members(chat.id, user_ids)

            await task.increase_counter("success")

            if users_per_invite == 1:
                user_link = Link.parse(str(user_ids[0]))

                text = Messages.USER_INVITED_TO_CHAT.format(user_link, link)
            else:
                text = Messages.USERS_INVITED_TO_CHAT.format(link)

            await task.send_log(LogLevel.INFO, text)
        except Exception as exception:
            if not isinstance(exception, UserAlreadyParticipant):
                await task.increase_counter("error")

                if users_per_invite == 1:
                    user_link = Link.parse(str(user_ids[0]))

                    text = Messages.FAILED_INVITE_USER_TO_CHAT.format(
                        user_link, link, format_additional_error_info(exception)
                    )
                else:
                    text = Messages.FAILED_INVITE_USERS_TO_CHAT.format(
                        link, format_additional_error_info(exception)
                    )

                await task.send_log(LogLevel.ERROR, text)

        await asyncio.sleep(5)


async def run(task: SessionTask, obj: Any):
    data = InviterTaskData.model_validate(obj)

    clients = task.get_session_clients()

    user_ids_queue = asyncio.Queue[int | str]()

    for user_id in data.user_ids:
        user_ids_queue.put_nowait(user_id)

    async with task.lock_storage:
        task.storage = {
            "spammed": [],
            "user_ids_queue": user_ids_queue,
        }

    await asyncio.gather(*[pool(task, client, data) for client in clients])
