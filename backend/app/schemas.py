from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    sync_strategy: Optional[str] = "plugin"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    api_key: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# --- SCHEMAS FOR INBOX & CONTEXT ---

class LinkRequest(BaseModel):
    url: str

class ProcessResponse(BaseModel):
    title: str
    markdown: str

class IndexRequest(BaseModel):
    notes: List[str]

# --- SCHEMAS FOR PLUGIN SETTINGS ---

class ValidateGeminiRequest(BaseModel):
    api_key: str

class UserPrefsRequest(BaseModel):
    api_key: str
    model: str
    prompt_template: str
