from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field



class ProtectedMasterKey(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    encrypted_master_key: bytes
    iv: bytes
    salt: bytes

    created_at: datetime
    updated_at: datetime


class ProtectedMasterKeyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    encrypted_master_key: str
    iv: str
    salt: str


class ProtectedMasterKeyGet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    encrypted_master_key: str
    iv: str
    salt: str

    created_at: datetime
    updated_at: datetime