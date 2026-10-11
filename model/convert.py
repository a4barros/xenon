
import base64


class Convert:
    @staticmethod
    def to_bytes(value: str) -> bytes:
        return base64.b64decode(value.encode("utf-8"))

    @staticmethod
    def to_base64(value: bytes) -> str:
        return base64.b64encode(value).decode("utf-8")