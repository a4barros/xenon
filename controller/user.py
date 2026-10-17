import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import get_user_repository, get_protected_master_key_repository, \
get_protected_vault_repository
from model.user import UserCreate
from repository.user import UserRepository
from repository.protected_master_key import ProtectedMasterKeyRepository
from repository.protected_vault import ProtectedVaultRepository
from security.jwtToken import (
    TokenResponse,
    authenticate_jwt_or_fail,
    create_access_token,
    fail,
)

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@user_router.get("/{username}/salt")
def get_user_salt(
    username: str,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    return repo.get_user_salt(username)


@user_router.post("/token", response_model=TokenResponse)
def authenticate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    try:
        user = repo.get_one_user(form_data.username)
    except:
        fail()

    if not hmac.compare_digest(
        user.authentication_key.encode("utf-8"),
        form_data.password.encode("utf-8"),
    ):
        fail()

    return TokenResponse(access_token=create_access_token(str(user.id)))


@user_router.get("/")
def get_user(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    user_id: Annotated[str, Depends(authenticate_jwt_or_fail)],
):
    user = repo.get_one_user_by_id(user_id)
    return user

@user_router.post("/")
def create_user(
    user_data: UserCreate,
    repo_user: Annotated[UserRepository, Depends(get_user_repository)],
    repo_master_key: Annotated[ProtectedMasterKeyRepository, Depends(get_protected_master_key_repository)],
    repo_vault_key: Annotated[ProtectedVaultRepository, Depends(get_protected_vault_repository)]):
    
    created_user = atomic_user_create(user_data, repo_user, repo_master_key, repo_vault_key)

    return created_user

@user_router.delete("/")
def delete_user(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    user_id: Annotated[str, Depends(authenticate_jwt_or_fail)],
):
    return repo.delete_user_cascade(user_id)

def atomic_user_create(
    user_data: UserCreate,
    repo_user: UserRepository,
    repo_master_key: ProtectedMasterKeyRepository,
    repo_vault_key: ProtectedVaultRepository
):
    created_user = repo_user.create_user(user_data)

    creation_completed = False
    try:
        repo_master_key.create_master_key(created_user.id, user_data.protected_master_key)
        repo_vault_key.create_protected_vault(created_user.id, user_data.protected_vault)
        creation_completed = True
    finally:
        if not creation_completed:
            repo_user.delete_user_cascade(user_data.username)

    return created_user