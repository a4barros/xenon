from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_protected_master_key_repository
from model.protected_vault import ProtectedVaultUpdate
from model.user import UserCreate
from repository.protected_master_key import ProtectedMasterKeyRepository


protected_master_key_router = APIRouter(
    prefix="/master",
    tags=["masterkey"]
)

@protected_master_key_router.get("/{user_id}")
def get_protected_master_key(
    user_id: str,
    repo: Annotated[ProtectedMasterKeyRepository, Depends(get_protected_master_key_repository)]):
    return repo.get_one_master_key(user_id)

@protected_master_key_router.post("/{user_id}")
def change_protected_master_key(
    vault_new_data: ProtectedVaultUpdate,
    repo: Annotated[ProtectedMasterKeyRepository, Depends(get_protected_master_key_repository)]):
    return repo.change_master_key(vault_new_data)

