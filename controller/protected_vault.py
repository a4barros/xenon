from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_protected_vault_repository
from model.protected_vault import ProtectedVaultUpdate
from repository.protected_vault import ProtectedVaultRepository
from security.jwtToken import authenticate_jwt_or_fail


protected_vault_router = APIRouter(
    prefix="/vault",
    tags=["vault"]
)

@protected_vault_router.get("/")
def get_protected_vault(
    repo: Annotated[ProtectedVaultRepository, Depends(get_protected_vault_repository)],
    user_id: Annotated[str, Depends(authenticate_jwt_or_fail)],):
    return repo.get_one_protected_vault(user_id)

@protected_vault_router.post("/")
def update_protected_vault_contents(
    vault_new_data: ProtectedVaultUpdate,
    repo: Annotated[ProtectedVaultRepository, Depends(get_protected_vault_repository)],
    user_id: Annotated[str, Depends(authenticate_jwt_or_fail)]
):
    return repo.update_protected_vault_contents(user_id, vault_new_data)
