from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_user_repository
from model.user import UserCreate
from repository.user import UserRepository


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
    repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return repo.create_user(user_data)

@user_router.delete("/{username}")
def delete_user(
    username: str,
    repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return repo.delete_user(username)