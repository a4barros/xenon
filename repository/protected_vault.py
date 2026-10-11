import base64
from typing import Any, Callable

from fastapi import HTTPException

from model.protected_vault import ProtectedVault, ProtectedVaultCreate, ProtectedVaultGet, ProtectedVaultUpdate
from repository.base import RepositoryBase # type: ignore


class ProtectedVaultRepository(RepositoryBase):
    CREATE_PROTECTED_VAULT = """
        INSERT INTO protected_vault (user_id, encrypted_vault, iv)
        VALUES (%(user_id)s, %(encrypted_vault)s, %(iv)s)
        RETURNING id, user_id, encrypted_vault, iv, created_at, updated_at
    """

    UPDATE_PROTECTED_VAULT_CONTENTS = """
        UPDATE protected_vault
        SET encrypted_vault = %(encrypted_vault)s,
            iv = %(iv)s,
            updated_at = NOW()
        WHERE user_id = %(user_id)s
        RETURNING id, user_id, encrypted_vault, iv, created_at, updated_at
    """

    def __init__(self, connect: Callable[[], Any]):
        super().__init__(connect)

    def create_protected_vault(self, user_id: str, protected_vault_create: ProtectedVaultCreate) -> ProtectedVaultGet:
        params = protected_vault_create.model_dump()
        params["user_id"] = user_id
        row = self.fetch_one(
            self.CREATE_PROTECTED_VAULT,
            params=params,
        )
        if row is None:
            raise ValueError("Protected vault could not be created")
        return ProtectedVaultGet.model_validate(row)

    def update_protected_vault_contents(
        self,
        user_id, 
        vault_new_data: ProtectedVaultUpdate,
    ) -> ProtectedVaultGet:

        row = self.fetch_one(
            self.UPDATE_PROTECTED_VAULT_CONTENTS,
            params={
                "encrypted_vault": super()._to_bytes(vault_new_data.encrypted_vault),
                "iv": super()._to_bytes(vault_new_data.iv),
                "user_id": user_id,
            },
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Protected vault not found")
        return ProtectedVaultGet.model_validate(row)

    def get_one_protected_vault(self, user_id: str) -> ProtectedVaultGet:
        row = super().fetch_one(
            """
            SELECT id, user_id, encrypted_vault, iv, created_at, updated_at
            FROM protected_vault
            WHERE user_id = %(user_id)s
            """,
            params={"user_id": user_id},
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Protected vault not found")
        return ProtectedVaultGet.model_validate(row)


    