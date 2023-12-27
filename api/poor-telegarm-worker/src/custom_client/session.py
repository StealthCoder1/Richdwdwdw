import logging
import typing

from pyrogram.session import Session
from pyrogram.connection import Connection
from pyrogram.raw import functions, all
from pyrogram.errors import RPCError, AuthKeyDuplicated

if typing.TYPE_CHECKING:
    from src.custom_client import CustomClient

log = logging.getLogger(__name__)


class CustomSession(Session):
    client: "CustomClient"

    async def start(self):
        while True:
            self.connection = Connection(
                self.dc_id,
                self.test_mode,
                self.client.ipv6,
                self.client.proxy,
                self.is_media,
            )

            try:
                await self.connection.connect()

                self.recv_task = self.loop.create_task(self.recv_worker())

                await self.send(functions.Ping(ping_id=0), timeout=self.START_TIMEOUT)

                if not self.is_cdn:
                    await self.send(
                        functions.InvokeWithLayer(
                            layer=all.layer,
                            query=functions.InitConnection(
                                api_id=await self.client.storage.api_id(),
                                app_version=self.client.app_version,
                                device_model=self.client.device_model,
                                system_version=self.client.system_version,
                                system_lang_code=self.client.lang_code,
                                lang_code=self.client.lang_code,
                                lang_pack=self.client.lang_pack,
                                query=functions.help.GetConfig(),
                            ),
                        ),
                        timeout=self.START_TIMEOUT,
                    )

                self.ping_task = self.loop.create_task(self.ping_worker())

                log.info("Session initialized: Layer %s", all.layer)
                log.info(
                    "Device: %s - %s", self.client.device_model, self.client.app_version
                )
                log.info(
                    "System: %s (%s)", self.client.system_version, self.client.lang_code
                )
            except AuthKeyDuplicated as e:
                await self.stop()
                raise e
            except (OSError, RPCError):
                await self.stop()
            except Exception as e:
                await self.stop()
                raise e
            else:
                break

        self.is_started.set()

        log.info("Session started")
