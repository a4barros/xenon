import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, NoReturn

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


def _signing_key() -> str:
    key = os.environ.get("JWT_SECRET_KEY")
    if key is None or len(key.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be set to at least 32 bytes")
    return key


def fail() -> NoReturn:
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(user_id: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": user_id, "exp": expires_at},
        _signing_key(),
        algorithm=ALGORITHM,
    )


async def authenticate_jwt_or_fail(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    try:
        payload = jwt.decode(
            token,
            _signing_key(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        fail()

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        fail()
    return subject
