import asyncio
import re

from enum import auto, StrEnum

from pyrogram.errors import YouBlockedUser
from pyrogram.types import Message

from src import functions
from src.constants import LogLevel, Messages
from src.utils import format_additional_error_info

DATE_REGEXP = re.compile(r"\d+\s\w+\s\d{4}")


class SpamBlockStatus(StrEnum):
    UNKNOWN = auto()
    NO = auto()
    TEMPORARY = auto()
    PERMANENT = auto()


class Account:
    async def check_spam(self: "functions.Function") -> SpamBlockStatus:
        try:
            await self.client.send_message("SpamBot", "/start")
        except YouBlockedUser:
            await self.client.unblock_user("SpamBot")

            return await self.check_spam()
        except Exception as exception:
            await self.task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_SEND_MESSAGE.format(
                    "@SpamBot", format_additional_error_info(exception)
                ),
            )

            return SpamBlockStatus.UNKNOWN

        await asyncio.sleep(1)

        try:
            chat_history_iterator = await self.client.get_chat_history("SpamBot", 1)

            if not chat_history_iterator:
                return SpamBlockStatus.UNKNOWN

            messages: list[Message] = [i async for i in chat_history_iterator]

            if len(messages) == 0:
                return SpamBlockStatus.UNKNOWN

            message = messages[0]
            message_text = message.text

            if len(message_text.split("\n")) == 1:
                return SpamBlockStatus.NO
            else:
                result = re.findall(DATE_REGEXP, message_text)

                return (
                    SpamBlockStatus.TEMPORARY if result else SpamBlockStatus.PERMANENT
                )
        except Exception as exception:
            await self.task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_GET_MESSAGES.format(
                    "@SpamBot", format_additional_error_info(exception)
                ),
            )

            return SpamBlockStatus.UNKNOWN
