from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field



class ProtectedVault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    user_id: str
    encrypted_vault: bytes
    iv: bytes

    created_at: datetime
    updated_at: datetime


class ProtectedVaultCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    encrypted_vault: str
    iv: str

class ProtectedVaultUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID4
    encrypted_vault: str
    iv: str

class ProtectedVaultGet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    user_id: UUID4
    encrypted_vault: str
    iv: str

    created_at: datetime
    updated_at: datetime
