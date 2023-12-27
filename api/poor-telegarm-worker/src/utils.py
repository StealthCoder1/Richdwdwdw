import asyncio
import hashlib
import random
import string
import struct
import base64
import re

from enum import StrEnum, auto
from urllib.parse import urlparse

from pyrogram.errors import RPCError, Flood

from src.constants import TELEGRAM_ERROR_CODES


class LinkType(StrEnum):
    ID = auto()
    USERNAME = auto()
    INVITE = auto()


class Link:
    id: int | None
    type: LinkType | None
    data: str | None

    INVITE_LINK_RE = re.compile(
        r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+))([\w-]+)$"
    )
    LINK_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)")

    @staticmethod
    def parse(url: str):
        link = Link()

        match = Link.INVITE_LINK_RE.match(str(url))

        if match:
            link.type = LinkType.INVITE
            link.data = match.group(1)
        elif url.isnumeric():
            link.type = LinkType.ID
            link.data = url
        else:
            link.type = LinkType.USERNAME
            link.data = re.sub(Link.LINK_RE, "", url).replace("@", "")

        return link

    def get_url(self, short: bool = True):
        if self.type == LinkType.INVITE:
            return f"https://t.me/{short and '+' or 'joinchat/'}{self.data}"
        else:
            return f"https://t.me/{self.data}"

    def get_short(self):
        return str(self) if self.type == LinkType.INVITE else self.data

    def __str__(self):
        if not self.data:
            return "@none"

        if self.type == LinkType.ID:
            return "@id" + self.data
        elif self.type == LinkType.USERNAME:
            return "@" + self.data
        elif self.type == LinkType.INVITE:
            return "https://t.me/+" + self.data

        return "@none"


RANDOM_MESSAGES = [
    "Привет",
    "Приветствую",
    "Доброго дня",
    "Хай",
    "Здраствуйте",
    "Дарова",
    "Здарова",
    "Приветик",
    "Как ты?",
    "Как дела?",
    "Как твой день?",
    "Privet",
    "Здравия желаю",
    "здрасте",
    "салют",
    "физкульт-привет",
    "доброго здоровья",
    "мое почтение",
    "здорово живёшь",
    "хаюшки",
    "доброго времени суток",
    "добрый час",
    "превед",
    "рад видеть",
    "подумать только",
    "как поживаешь",
    "салам",
    "поклон",
    "как поживаешь",
    "хой",
    "вишь ты",
    "приветливость",
    "что за диво",
    "смотри пожалуйста",
    "саламчик",
    "йоу",
    "шелом",
    "ку",
    "бонжур",
    "трям",
    "задрова",
    "приветец",
    "хола",
    "здрасти-мордасти",
    "хелло",
    "батушки-светы",
]


def sha256(data: bytes) -> str:
    hash = hashlib.sha256()

    hash.update(data)

    return hash.hexdigest()


def get_random_symbols() -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )


def get_random_message() -> str:
    return random.choice(RANDOM_MESSAGES)


def generate_variations(line: str, index: int = 0, current: str = ""):
    result: list[str] = []

    if index >= len(line):
        return [current]

    char = line[index]

    if char == "{":
        end_index = line.find("}", index)

        if end_index != -1:
            variations = line[index + 1 : end_index].split("|")

            for variation in variations:
                result.extend(
                    generate_variations(line, end_index + 1, current + variation)
                )

    else:
        result.extend(generate_variations(line, index + 1, current + char))

    return result


def get_session_string(auth_key: bytes, dc_id: int):
    packed = struct.pack(">BI?256sQ?", dc_id, 2040, False, auth_key, 1, False)

    return base64.urlsafe_b64encode(packed).decode().rstrip("=")


def parse_proxy(url: str):
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    return {
        "scheme": parsed.scheme,  # "socks4", "socks5" and "http" are supported
        "hostname": parsed.hostname,
        "port": parsed.port,
        "username": parsed.username,
        "password": parsed.password,
    }


def get_additional_error_info(exception: Exception):
    if not isinstance(exception, RPCError):
        print(exception)

        return None

    value = None

    if isinstance(exception, Flood) and isinstance(exception.value, int):
        value = exception.value

    return dict(id=exception.ID, value=value)


def format_additional_error_info(exception: Exception):
    additional_error_info = get_additional_error_info(exception)

    if not additional_error_info:
        return ""

    error_id = additional_error_info["id"]

    if not isinstance(error_id, str):
        return ""

    error_description = TELEGRAM_ERROR_CODES.get(error_id, "")

    if error_description != "":
        error_description = "; " + error_description

    result = f"[{error_id}{error_description}]"

    if additional_error_info["value"] is not None:
        result = result.replace("X", str(additional_error_info["value"]))

    return result


async def handle_exception(exception):
    if isinstance(exception, Flood) and isinstance(exception.value, int):
        await asyncio.sleep(exception.value)
