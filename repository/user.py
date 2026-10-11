import base64
from typing import Any, Callable

from fastapi import HTTPException

from model.user import UserCreate, UserGet
from repository.base import RepositoryBase # type: ignore


class UserRepository(RepositoryBase):
    CREATE_USER_QUERY = """
        INSERT INTO users (username, authentication_key, salt)
        VALUES (%s, %s, %s)
        RETURNING id, username, authentication_key, salt, created_at, updated_at
    """

    UPDATE_USER_QUERY = """
        UPDATE users
        SET authentication_key = %s,
            salt = %s,
            updated_at = NOW()
        WHERE username = %s
        RETURNING id, username, authentication_key, salt, created_at, updated_at
    """

    DELETE_USER_QUERY = """
        DELETE FROM users
        WHERE username = %s
    """

    def __init__(self, connect: Callable[[], Any]):
        super().__init__(connect)

    def create_user(self, user_data: UserCreate) -> UserGet:
        row = self.fetch_one(
            self.CREATE_USER_QUERY,
            params=(
                user_data.username,
                super()._to_bytes(user_data.authentication_key),
                super()._to_bytes(user_data.salt),
            ),
        )
        if row is None:
            raise ValueError("User could not be created")
        return UserGet.model_validate(row)

    def change_password(
        self,
        username: str,
        new_authentication_key: str,
        new_salt: str,
    ) -> UserGet:
        row = self.fetch_one(
            self.UPDATE_USER_QUERY,
            params=(
                super()._to_bytes(new_authentication_key),
                super()._to_bytes(new_salt),
                username,
            ),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserGet.model_validate(row)

    def get_one_user(self, username: str) -> UserGet:
        row = super().fetch_one(
            """
            SELECT id, username, authentication_key, salt, created_at, updated_at
            FROM users
            WHERE username = %s
            """,
            params=(username,),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserGet.model_validate(row)

    def delete_user(self, username: str) -> None:
        row = super().fetch_one(
            self.DELETE_USER_QUERY,
            params=(username,),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        

