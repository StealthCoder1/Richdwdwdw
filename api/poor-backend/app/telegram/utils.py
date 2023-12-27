import re

REPLACE_REGEXP = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)"
)


def replace_telegram_url(string: str):
    return re.sub(REPLACE_REGEXP, "", string)
