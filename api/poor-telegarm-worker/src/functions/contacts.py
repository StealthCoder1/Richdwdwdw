from src import functions
from src.constants import LogLevel, Messages
from src.utils import Link, format_additional_error_info


class Contacts:
    async def add_to_contacts(self: "functions.Function", chat_id: int | str):
        link = Link.parse(str(chat_id))

        try:
            await self.client.add_contact(chat_id, str(chat_id))

            await self.task.send_log(LogLevel.INFO, Messages.CONTACT_ADDED.format(link))
        except Exception as exception:
            await self.task.send_log(
                LogLevel.ERROR,
                Messages.FAILED_ADD_CONTACT.format(
                    link, format_additional_error_info(exception)
                ),
            )
