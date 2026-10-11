from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_protected_vault_repository
from model.protected_vault import ProtectedVaultUpdate
from model.user import UserCreate
from repository.protected_vault import ProtectedVaultRepository


protected_vault_router = APIRouter(
    prefix="/vault",
    tags=["vault"]
)

@protected_vault_router.get("/{user_id}")
def get_protected_vault(
    user_id: str,
    repo: Annotated[ProtectedVaultRepository, Depends(get_protected_vault_repository)]):
    return repo.get_one_protected_vault(user_id)

@protected_vault_router.post("/{user_id}")
def update_protected_vault_contents(
    vault_new_data: ProtectedVaultUpdate,
    repo: Annotated[ProtectedVaultRepository, Depends(get_protected_vault_repository)]):
    return repo.update_protected_vault_contents(vault_new_data)

