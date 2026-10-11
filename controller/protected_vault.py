from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_user_repository
from model.user import UserCreate
from repository.user import UserRepository


protected_vault_router = APIRouter(
    prefix="/vault"
)

@protected_vault_router.get("/{user_id}")
def get_protected_vault(
    username: str,
    repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return repo.get_one_user(username)

@protected_vault_router.post("/{user_id}")
def update_protected_vault_contents(
    user_data: UserCreate,
    repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return repo.create_user(user_data)

