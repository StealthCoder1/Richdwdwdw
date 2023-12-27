import sqlite3
import struct
import base64
import io
import zipfile
import tempfile
import os

import opentele
import magic
import aiofiles


class SessionReader:
    def __init__(self):
        self.sessions: set[tuple[bytes, int]] = set()

    def get_sessions(self):
        return [f"{session[0].hex()}:{session[1]}" for session in self.sessions]

    async def read_sessions_from_files(self, file_paths: list[str]):
        for file_path in file_paths:
            await self.read_sessions_from_file(file_path)

    async def read_sessions_from_file(self, file_path: str):
        async with aiofiles.open(file_path, "rb") as f:
            file = await f.read()

        type = magic.from_buffer(file, mime=True)

        if type == "text/plain":
            self.read_plain(file.decode())
        elif type in ("application/x-sqlite3", "application/vnd.sqlite3"):
            self.read_sqlite_session(file_path)
        elif type == "application/zip":
            with zipfile.ZipFile(io.BytesIO(file)) as zip:
                total_size, is_valid = 0, False

                tdata_dir = ""

                for zip_info in zip.infolist():
                    total_size += zip_info.file_size

                    if zip_info.filename == "tdata/":
                        tdata_dir = "tdata/"

                    if not is_valid:
                        is_valid = zip_info.filename in ["tdata/key_datas", "key_datas"]

                if not is_valid or total_size > 5e6:
                    return

                with tempfile.TemporaryDirectory() as temporary_dir_path:
                    zip.extractall(temporary_dir_path)

                    self.read_tdata_folder(os.path.join(temporary_dir_path, tdata_dir))
        else:
            print(type)

    def read_plain(self, text: str) -> None:
        for line in text.split("\n"):
            line = line.rstrip()

            try:
                if line.index(":") != -1:
                    self.read_lzt_string(line)
                else:
                    self.read_pyrogram_session_string(line)
            except Exception as e:
                print(e)

    def read_sqlite_session(self, path: str) -> None:
        try:
            connection = sqlite3.connect(path)

            rows = connection.execute("SELECT auth_key, dc_id FROM sessions").fetchall()

            for row in rows:
                self.sessions.add((row[0], row[1]))
        except Exception as e:
            print(e)

    def read_lzt_string(self, string: str):
        parts = string.split(":")

        self.sessions.add((bytes.fromhex(parts[0]), int(parts[1])))

    def read_pyrogram_session_string(self, session_string: str) -> None:
        unpacked = struct.unpack(
            ">BI?256sQ?",
            base64.urlsafe_b64decode(session_string + "=" * (-len(session_string) % 4)),
        )

        self.sessions.add((unpacked[3], unpacked[0]))

    def read_tdata_folder(self, path: str) -> None:
        try:
            tdesktop = opentele.td.TDesktop(path)

            for account in tdesktop.accounts:
                if not account.authKey:
                    continue

                self.sessions.add((account.authKey.key, account.authKey.dcId))
        except Exception as e:
            print(e)
