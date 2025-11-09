from pydantic import BaseModel
from typing import Optional


class LLMProviderConfig(BaseModel):
    provider: str  # "claude", "openai", "azure"
    api_key: str
    model: Optional[str] = None
    endpoint: Optional[str] = None  # For Azure
    deployment_name: Optional[str] = None  # For Azure


class GitConfig(BaseModel):
    source: str  # "github" or "gitlab"
    token: str


class SystemSettingUpdate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemSettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str]

    class Config:
        from_attributes = True
