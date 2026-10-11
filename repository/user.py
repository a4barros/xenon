import base64
from typing import Any, Callable

from fastapi import HTTPException

from model.user import UserCreate, UserGet, UserUpdate
from repository.base import RepositoryBase # type: ignore


class UserRepository(RepositoryBase):
    CREATE_USER_QUERY = """
        INSERT INTO users (username, authentication_key, salt)
        VALUES (%(username)s, %(authentication_key)s, %(salt)s)
        RETURNING id, username, authentication_key, salt, created_at, updated_at
    """

    UPDATE_USER_QUERY = """
        UPDATE users
        SET authentication_key = %(authentication_key)s,
            salt = %(salt)s,
            updated_at = NOW()
        WHERE username = %(id)s
        RETURNING id, username, authentication_key, salt, created_at, updated_at
    """

    DELETE_USER_QUERY = """
        DELETE FROM users
        WHERE username = %(id)s
    """

    def __init__(self, connect: Callable[[], Any]):
        super().__init__(connect)

    def create_user(self, user_data: UserCreate) -> UserGet:
        row = self.fetch_one(
            self.CREATE_USER_QUERY,
            params=user_data.model_dump(),
        )
        if row is None:
            raise ValueError("User could not be created")
        return UserGet.model_validate(row)

    def change_password(
        self,
        user_id: str,
        user_update: UserUpdate,
    ) -> UserGet:
        params = user_update.model_dump()
        params["user_id"] = user_id
        row = self.fetch_one(
            self.UPDATE_USER_QUERY,
            params=params,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserGet.model_validate(row)

    def get_one_user(self, username: str) -> UserGet:
        row = super().fetch_one(
            """
                SELECT id, username, authentication_key, salt, created_at, updated_at
                FROM users
                WHERE username = %(username)s
            """,
            params={"username": username},
        )
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserGet.model_validate(row)

    def delete_user_cascade(self, username: str) -> None:
        row = super().fetch_one(
            self.DELETE_USER_QUERY,
            params={"username": username},
        )
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        

