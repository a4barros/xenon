import base64
from typing import Any, Callable

from fastapi import HTTPException

from model.protected_master_key import (
    ProtectedMasterKey,
    ProtectedMasterKeyCreate,
    ProtectedMasterKeyGet,
)
from repository.base import RepositoryBase # type: ignore


class ProtectedMasterKeyRepository(RepositoryBase):
    CREATE_MASTER_KEY_QUERY = """
        INSERT INTO protected_master_key (user_id, encrypted_master_key, iv, salt)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, encrypted_master_key, iv, salt, created_at, updated_at
    """

    UPDATE_MASTER_KEY_QUERY = """
        UPDATE protected_master_key
        SET encrypted_master_key = %s,
            iv = %s,
            salt = %s,
            updated_at = NOW()
        WHERE user_id = %s
        RETURNING id, user_id, encrypted_master_key, iv, salt, created_at, updated_at
    """

    def __init__(self, connect: Callable[[], Any]):
        super().__init__(connect)

    def create_master_key(self, master_key_data: ProtectedMasterKeyCreate) -> ProtectedMasterKeyGet:
        row = self.fetch_one(
            self.CREATE_MASTER_KEY_QUERY,
            params=(
                master_key_data.user_id,
                super()._to_bytes(master_key_data.encrypted_master_key),
                super()._to_bytes(master_key_data.iv),
                super()._to_bytes(master_key_data.salt),
            ),
        )
        if row is None:
            raise ValueError("Master key could not be created")
        return ProtectedMasterKeyGet.model_validate(row)

    def change_master_key(
        self,
        username: str,
        new_authentication_key: str,
        new_salt: str,
    ) -> ProtectedMasterKeyGet:
        current = self.fetch_one(
            """
            SELECT pmk.id, pmk.user_id, pmk.encrypted_master_key, pmk.iv, pmk.salt, pmk.created_at, pmk.updated_at
            FROM protected_master_key pmk
            JOIN users u ON u.id = pmk.user_id
            WHERE u.username = %s
            """,
            params=(username,),
        )
        if current is None:
            raise HTTPException(status_code=404, detail="Master key not found")

        row = self.fetch_one(
            self.UPDATE_MASTER_KEY_QUERY,
            params=(
                super()._to_bytes(new_authentication_key),
                current["iv"],
                super()._to_bytes(new_salt),
                current["user_id"],
            ),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Master key not found")
        return ProtectedMasterKeyGet.model_validate(row)

    def get_one_master_key(self, username: str) -> ProtectedMasterKeyGet:
        row = super().fetch_one(
            """
            SELECT pmk.id, pmk.user_id, pmk.encrypted_master_key, pmk.iv, pmk.salt, pmk.created_at, pmk.updated_at
            FROM protected_master_key pmk
            JOIN users u ON u.id = pmk.user_id
            WHERE u.username = %s
            """,
            params=(username,),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Master key not found")
        return ProtectedMasterKeyGet.model_validate(row)

    