from aiogram import Bot
from aiogram.types import (
    ChatAdministratorRights,
    User,
    ChatMember,
    ChatMemberAdministrator,
)


class CustomBot(Bot):
    async def set_default_administrator_rights(self, for_channels: bool):
        await self.set_my_default_administrator_rights(
            ChatAdministratorRights(
                is_anonymous=True,
                can_manage_chat=True,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=False,
                can_invite_users=True,
                can_post_messages=False,
                can_edit_messages=False,
                can_pin_messages=False,
                can_post_stories=False,
                can_edit_stories=False,
                can_delete_stories=False,
                can_manage_topics=False,
            ),
            for_channels,
        )

    async def check_permissions(me: User, chat_administrators: list[ChatMember]):
        has_permissions = False

        for chat_member in chat_administrators:
            if not isinstance(chat_member, ChatMemberAdministrator):
                continue

            if chat_member.user.id != me.id:
                continue

            has_permissions = (
                chat_member.can_promote_members and chat_member.can_invite_users
            )

            break

        return has_permissions


bot = CustomBot("6486625380:AAHQPQi-Gy947th9mtY0SbFhN3UvIOfrwbs")
