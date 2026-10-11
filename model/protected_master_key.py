from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field



class ProtectedMasterKey(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    user_id: UUID4
    encrypted_master_key: bytes
    iv: bytes
    salt: bytes

    created_at: datetime
    updated_at: datetime


class ProtectedMasterKeyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    encrypted_master_key: str
    iv: str
    salt: str

class ProtectedMasterKeyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID4
    encrypted_master_key: str
    iv: str
    salt: str


class ProtectedMasterKeyGet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    user_id: UUID4
    encrypted_master_key: str
    iv: str
    salt: str

    created_at: datetime
    updated_at: datetime