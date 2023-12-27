from urllib.parse import urlparse, urlunsplit


def validate_proxy_urls(schema: str, urls: list[str]):
    result = []

    for url in urls:
        url = validate_proxy_url(schema + "://" + url)

        if url:
            result.append(url)

    return result


def validate_proxy_url(url: str):
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "socks4", "socks5"]:
        return None

    if not parsed.hostname or not parsed.port:
        return None

    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
