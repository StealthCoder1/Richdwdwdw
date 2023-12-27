from enum import StrEnum, auto

from pydantic import BaseModel


class Service(StrEnum):
    TELEGRAM = auto()


class ProxyType(StrEnum):
    SOCKS5 = auto()


class ProxiesUploadRequest(BaseModel):
    service: Service
    type: ProxyType
    proxies: list[str]


class ProxiesUploadResponse(BaseModel):
    count: int


class ProxySchema(BaseModel):
    id: int
    url: str
    latency: int | None


class ProxiesGet(BaseModel):
    service: Service
