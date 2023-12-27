import asyncio
import logging

from pyrogram import Client, raw, types
from pyrogram.session.auth import Auth
from pyrogram.errors import Unauthorized
from pyrogram.handlers import RawUpdateHandler

from src import custom_client

log = logging.getLogger(__name__)


class CustomClient(Client):
    lang_pack: str

    async def connect(self, load_session: bool = True) -> bool:
        if self.is_connected:
            raise ConnectionError("Client is already connected")

        if load_session:
            await self.load_session()

        self.session = custom_client.CustomSession(
            self,
            await self.storage.dc_id(),
            await self.storage.auth_key(),
            await self.storage.test_mode(),
        )

        await self.session.start()

        self.is_connected = True

        return bool(await self.storage.user_id())

    async def start(self, load_session: bool = True):
        is_authorized = await self.connect(load_session)

        try:
            if not is_authorized:
                raise Unauthorized

            if not await self.storage.is_bot() and self.takeout:
                self.takeout_id = (
                    await self.invoke(raw.functions.account.InitTakeoutSession())
                ).id
                log.info("Takeout session %s initiated", self.takeout_id)

            await self.invoke(raw.functions.updates.GetState())
        except (Exception, KeyboardInterrupt):
            await self.disconnect()
            raise
        else:
            self.me = await self.get_me()
            await self.initialize()

            return self

    async def switch_dc(self, dc_id: int):
        await self.session.stop()

        await self.storage.dc_id(dc_id)
        await self.storage.auth_key(
            await Auth(
                self, await self.storage.dc_id(), await self.storage.test_mode()
            ).create()
        )

        self.session = custom_client.CustomSession(
            self,
            await self.storage.dc_id(),
            await self.storage.auth_key(),
            await self.storage.test_mode(),
        )

        await self.session.start()

    async def qr_login_to_new_client(self):
        new_client = CustomClient(
            "",
            self.api_id,
            self.api_hash,
            self.app_version,
            self.device_model,
            self.system_version,
            self.lang_code,
            proxy=self.proxy,
            in_memory=True,
        )

        new_client.lang_pack = self.lang_pack

        await new_client.connect()

        await new_client.dispatcher.start()

        login_token: raw.types.auth.LoginToken = await new_client.invoke(
            raw.functions.auth.ExportLoginToken(
                api_id=self.api_id, api_hash=self.api_hash, except_ids=[]
            )
        )

        event = asyncio.Event()

        async def handler(
            _: "CustomClient",
            update: raw.base.Update,
            users: dict[int, types.User],
            chats: dict[int, types.Chat | raw.types.Channel],
        ):
            if isinstance(update, raw.types.UpdateLoginToken):
                r = await _.invoke(
                    raw.functions.auth.ExportLoginToken(
                        api_id=self.api_id, api_hash=self.api_hash, except_ids=[]
                    )
                )

                if isinstance(r, raw.types.auth.LoginTokenSuccess):
                    event.set()
                elif isinstance(r, raw.types.auth.LoginTokenMigrateTo):
                    await _.switch_dc(r.dc_id)

                    r = await _.invoke(
                        raw.functions.auth.ImportLoginToken(token=r.token)
                    )

                    if isinstance(r, raw.types.auth.LoginTokenSuccess):
                        event.set()
                    else:
                        print(r)

        raw_update_handler = new_client.add_handler(RawUpdateHandler(handler))

        await self.invoke(raw.functions.auth.AcceptLoginToken(token=login_token.token))

        try:
            await asyncio.wait_for(event.wait(), 30)
        finally:
            new_client.remove_handler(*raw_update_handler)

        print(await new_client.get_me())

        return new_client

    async def set_storage(
        self,
        dc_id: int,
        api_id: int,
        test_mode: bool,
        auth_key: bytes,
        user_id: int,
        is_bot: bool,
        date: int,
    ):
        await self.storage.dc_id(dc_id)
        await self.storage.api_id(api_id)
        await self.storage.test_mode(test_mode)
        await self.storage.auth_key(auth_key)
        await self.storage.user_id(user_id)
        await self.storage.is_bot(is_bot)
        await self.storage.date(date)
