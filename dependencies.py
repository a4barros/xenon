from database import connect
from repository.user import UserRepository


def get_user_repository() -> UserRepository:
    return UserRepository(connect)