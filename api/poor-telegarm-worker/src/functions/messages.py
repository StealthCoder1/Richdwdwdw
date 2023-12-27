import asyncio
import io
import random

from typing import Any

import aiofiles

from src import functions
from src.schemas import CooldownBlock, MailingConfig, Media, MediaType, MessagesBlock
from src.utils import generate_variations, get_random_message, get_random_symbols


class Messages:
    async def send_message(
        self: "functions.Function",
        chat_id: int | str,
        config: MailingConfig,
        reply_to: int | None = None,
    ):
        #if config.add_to_contacts is True:
        #    await self.add_to_contacts(chat_id)

        is_saved_messages_chat_id = chat_id in ("me", "self")

        if is_saved_messages_chat_id:
            config.edit_message = False

        for item in config.items:
            if isinstance(item, MessagesBlock):
                message = random.choice(item.messages)

                generated_text = random.choice(generate_variations(message.text))

                text = get_random_message() if config.edit_message else generated_text

                sent_message = await self.send_one_message(
                    chat_id, message.media, text, reply_to_message_id=reply_to
                )

                if not sent_message:
                    raise

                if config.edit_message and not (
                    message.media and message.media.type == "video_note"
                ):
                    await sent_message.edit_caption(generated_text)

                if not is_saved_messages_chat_id and config.add_to_contacts is not None:
                    await sent_message.delete(False)

                return sent_message
            elif isinstance(item, CooldownBlock):
                await asyncio.sleep(item.cooldown)

    async def send_one_message(
        self: "functions.Function",
        chat_id: int | str,
        media: Media | None,
        text: str = "",
        **kwargs: Any
    ):
        sent_message = None

        if media:
            filename = get_random_symbols()

            async with aiofiles.open(media.filename, "rb") as f:
                file = io.BytesIO(await f.read())

            file.name = filename

            if media.type == MediaType.PHOTO:
                file.name += ".jpg"

                sent_message = await self.client.send_photo(
                    chat_id, file, text, **kwargs
                )
            elif media.type == MediaType.VIDEO:
                file.name += ".mp4"

                sent_message = await self.client.send_video(
                    chat_id, file, text, **kwargs
                )
            elif media.type == MediaType.VIDEO_NOTE:
                file.name += ".mp4"

                sent_message = await self.client.send_video_note(
                    chat_id, file, **kwargs
                )
        else:
            sent_message = await self.client.send_message(chat_id, text, **kwargs)

        return sent_message
