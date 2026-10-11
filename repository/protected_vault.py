import base64
from typing import Any, Callable

from fastapi import HTTPException

from model.protected_vault import ProtectedVault, ProtectedVaultCreate, ProtectedVaultGet
from repository.base import RepositoryBase # type: ignore


class ProtectedVaultRepository(RepositoryBase):
    CREATE_PROTECTED_VAULT = """
        INSERT INTO protected_vault (user_id, encrypted_vault, iv)
        VALUES (%s, %s, %s)
        RETURNING id, user_id, encrypted_vault, iv, created_at, updated_at
    """

    UPDATE_PROTECTED_VAULT_CONTENTS = """
        UPDATE protected_vault
        SET encrypted_vault = %s,
            iv = %s,
            updated_at = NOW()
        WHERE user_id = %s
        RETURNING id, user_id, encrypted_vault, iv, created_at, updated_at
    """

    def __init__(self, connect: Callable[[], Any]):
        super().__init__(connect)

    def create_protected_vault(self, protected_vault_create: ProtectedVaultCreate) -> ProtectedVaultGet:
        row = self.fetch_one(
            self.CREATE_PROTECTED_VAULT,
            params=(
                protected_vault_create.user_id,
                super()._to_bytes(protected_vault_create.encrypted_vault),
                super()._to_bytes(protected_vault_create.iv),
            ),
        )
        if row is None:
            raise ValueError("Protected vault could not be created")
        return ProtectedVaultGet.model_validate(row)

    def update_protected_vault_contents(
        self,
        new_contents: str,
        iv: str,
        user_id: str | None = None,
    ) -> ProtectedVaultGet:
        if user_id is None:
            raise ValueError("user_id is required to update the protected vault")

        row = self.fetch_one(
            self.UPDATE_PROTECTED_VAULT_CONTENTS,
            params=(
                super()._to_bytes(new_contents),
                super()._to_bytes(iv),
                user_id,
            ),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Protected vault not found")
        return ProtectedVaultGet.model_validate(row)

    def get_one_protected_vault(self, user_id: str) -> ProtectedVaultGet:
        row = super().fetch_one(
            """
            SELECT id, user_id, encrypted_vault, iv, created_at, updated_at
            FROM protected_vault
            WHERE user_id = %s
            """,
            params=(user_id,),
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Protected vault not found")
        return ProtectedVaultGet.model_validate(row)


    