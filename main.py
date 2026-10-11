import hmac
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from psycopg.rows import dict_row

from model.user import UserCreate
from repository.user import UserRepository
from controller.user import user_router


app = FastAPI()
app.include_router(user_router)