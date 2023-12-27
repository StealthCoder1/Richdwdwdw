import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):
    def __init__(self, key: str):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, data: str, safe: bool = False):
        raw = self._pad(data)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        buffer = iv + cipher.encrypt(raw.encode())

        return base64.urlsafe_b64encode(buffer) if safe else base64.b64encode(buffer)

    def decrypt(self, data: str, safe: bool = False):
        enc = base64.urlsafe_b64decode(data) if safe else base64.b64decode(data)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s: str):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s: bytes):
        return s[: -ord(s[len(s) - 1 :])]
