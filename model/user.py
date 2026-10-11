from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, UUID4



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


class UserGet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID4
    username: str = Field(max_length=255)
    authentication_key: str
    salt: str
    
    created_at: datetime
    updated_at: datetime

