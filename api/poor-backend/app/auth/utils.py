import hashlib
import hmac
import time

from app.auth.config import auth_config


def check_telegram_authorization(auth_data: dict, bot_token: str) -> dict | None:
    if "hash" not in auth_data:
        return None

    check_hash = auth_data.pop("hash")

    data_check_array = []

    for _, (key, value) in enumerate(sorted(auth_data.items(), key=lambda x: x[0])):
        data_check_array.append(key + "=" + value)

    data_check_string = "\n".join(data_check_array)

    secret_key = hashlib.sha256(bot_token.encode()).digest()

    hash = hmac.new(
        secret_key, data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    if hash != check_hash or int(time.time()) - int(auth_data["auth_date"]) > 86_400:
        return None

    return auth_data


def get_refresh_token_cookie(refresh_token: str, reset: bool = False):
    cookie = {
        "key": "refresh_token",
        "httponly": True,
        "samesite": "none",
        "secure": auth_config.SECURE_COOKIES,
        "domain": "",
    }

    if reset:
        return cookie

    return {**cookie, "value": refresh_token, "max_age": auth_config.REFRESH_TOKEN_EXP}
