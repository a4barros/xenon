import base64
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, UUID4

from model.protected_master_key import ProtectedMasterKeyCreate
from model.protected_vault import ProtectedVaultCreate



class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    username: str = Field(max_length=255)
    authentication_key: bytes
    salt: bytes
    
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(max_length=255)
    authentication_key: str
    salt: str

    protected_master_key: ProtectedMasterKeyCreate
    protected_vault: ProtectedVaultCreate

class UserGet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    username: str = Field(max_length=255)
    authentication_key: str
    salt: str
    
    created_at: datetime
    updated_at: datetime

