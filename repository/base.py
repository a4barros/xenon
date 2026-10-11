import base64
from typing import Any, Callable

from fastapi import HTTPException
from psycopg.errors import UniqueViolation


class RepositoryBase:
    def __init__(self, connect: Callable[[], Any]):
        self.connect = connect

    @staticmethod
    def _to_bytes(value: str) -> bytes:
        return base64.b64decode(value.encode("utf-8"))

    @staticmethod
    def _to_base64(value: bytes) -> str:
        return base64.b64encode(value).decode("utf-8")

    def execute(self, query: str, params: tuple | list | None = None, **kwargs):
        try:
            with self.connect() as connection:
                return connection.execute(query, params=params, **kwargs)
        except UniqueViolation as error:
            raise HTTPException(status_code=409, detail="Already exists") from error

    def fetch_one(self, query: str, params: tuple | list | None = None) -> dict | None:
        try:
            with self.connect() as connection:
                return connection.execute(query, params=params).fetchone()
        except UniqueViolation as error:
            raise HTTPException(status_code=409, detail="Already exists") from error

    def fetch_many(self, query: str, params: tuple | list | None = None, **kwargs) -> list[dict]:
        try:
            with self.connect() as connection:
                return connection.execute(query, params=params, **kwargs).fetchall()
        except UniqueViolation as error:
            raise HTTPException(status_code=409, detail="Already exists") from error