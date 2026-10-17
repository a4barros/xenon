from datetime import datetime, timedelta, timezone
import hmac
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ConfigDict
from psycopg.rows import dict_row

from model.user import UserCreate
from repository.user import UserRepository
from controller.user import user_router
from controller.protected_vault import protected_vault_router
from controller.master_key import protected_master_key_router


app = FastAPI(title="Xenon", version="0.0.1")

origins = [
    "http://localhost:9000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(protected_vault_router)
app.include_router(protected_master_key_router)