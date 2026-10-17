from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    workspace_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    workspace_id: uuid.UUID
    workspace: Optional[WorkspaceResponse] = None
    
    class Config:
        from_attributes = True

# Service schemas
class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    environment: str = "production"
    version: Optional[str] = None

class ServiceResponse(BaseModel):
    id: uuid.UUID
    name: str
    environment: str
    version: Optional[str]
    last_telemetry_at: Optional[datetime]
    health_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ServiceListResponse(BaseModel):
    services: list[ServiceResponse]
    total: int
    limit: int
    offset: int
