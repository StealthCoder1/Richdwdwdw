def hash_password(password: str) -> bytes:
    return password.encode()


def check_password(password: str, password_in_db: bytes) -> bool:
    return password == password_in_db.decode()
