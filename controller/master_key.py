from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_protected_master_key_repository
from model.protected_master_key import ProtectedMasterKeyUpdate
from repository.protected_master_key import ProtectedMasterKeyRepository
from security.jwtToken import authenticate_jwt_or_fail

protected_master_key_router = APIRouter(
    prefix="/master",
    tags=["masterkey"]
)

@protected_master_key_router.get("/")
def get_protected_master_key(
    repo: Annotated[ProtectedMasterKeyRepository, Depends(get_protected_master_key_repository)],
    user_id: Annotated[str, Depends(authenticate_jwt_or_fail)],
):
    return repo.get_one_master_key(user_id)

@protected_master_key_router.post("/")
def change_protected_master_key(
    vault_new_data: ProtectedMasterKeyUpdate,
    repo: Annotated[ProtectedMasterKeyRepository, Depends(get_protected_master_key_repository)],
    user_id: Annotated[str, Depends(authenticate_jwt_or_fail)],
):
    return repo.change_master_key(user_id, vault_new_data)
