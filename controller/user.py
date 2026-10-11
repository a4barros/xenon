from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_user_repository, get_protected_master_key_repository, \
get_protected_vault_repository
from model.user import UserCreate
from repository.user import UserRepository
from repository.protected_master_key import ProtectedMasterKeyRepository
from repository.protected_vault import ProtectedVaultRepository

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@user_router.get("/{username}")
def get_user(
    username: str,
    repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return repo.get_one_user(username)

@user_router.post("/")
def create_user(
    user_data: UserCreate,
    repo_user: Annotated[UserRepository, Depends(get_user_repository)],
    repo_master_key: Annotated[ProtectedMasterKeyRepository, Depends(get_protected_master_key_repository)],
    repo_vault_key: Annotated[ProtectedVaultRepository, Depends(get_protected_vault_repository)]):
    
    created_user = repo_user.create_user(user_data)
    repo_master_key.create_master_key(created_user.id, user_data.protected_master_key)
    repo_vault_key.create_protected_vault(created_user.id, user_data.protected_vault)

    return created_user

@user_router.delete("/{username}")
def delete_user(
    username: str,
    repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return repo.delete_user(username)