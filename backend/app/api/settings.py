from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_admin_user
from app.models.user import User
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import SystemSettingUpdate, SystemSettingResponse, LLMProviderConfig, GitConfig

router = APIRouter(prefix="/settings", tags=["Settings"])


def _get_settings_repo(db: Session = Depends(get_db)) -> SettingsRepository:
    return SettingsRepository(db)


@router.get("/", response_model=List[SystemSettingResponse])
def list_settings(
    current_user: User = Depends(get_current_admin_user),
    repo: SettingsRepository = Depends(_get_settings_repo),
):
    """List all system settings (admin only)"""
    settings = repo.get_all()

    # Mask sensitive values
    for setting in settings:
        if setting.is_encrypted or "key" in setting.key.lower() or "token" in setting.key.lower():
            setting.value = "***"

    return settings


@router.put("/llm-provider", response_model=dict)
def configure_llm_provider(
    config: LLMProviderConfig,
    current_user: User = Depends(get_current_admin_user),
    repo: SettingsRepository = Depends(_get_settings_repo),
    db: Session = Depends(get_db),
):
    """Configure LLM provider (admin only)"""
    repo.upsert("llm_provider", config.provider, description="Active LLM provider")
    repo.upsert(
        f"{config.provider}_api_key",
        config.api_key,
        description=f"API key for {config.provider}",
        is_encrypted=True,
    )

    if config.provider == "azure":
        if config.endpoint:
            repo.upsert("azure_endpoint", config.endpoint, description="Azure OpenAI endpoint")
        if config.deployment_name:
            repo.upsert("azure_deployment_name", config.deployment_name, description="Azure OpenAI deployment name")

    db.commit()

    return {"message": f"LLM provider '{config.provider}' configured successfully"}


@router.put("/git-config", response_model=dict)
def configure_git(
    config: GitConfig,
    current_user: User = Depends(get_current_admin_user),
    repo: SettingsRepository = Depends(_get_settings_repo),
    db: Session = Depends(get_db),
):
    """Configure Git provider token (admin only)"""
    repo.upsert(
        f"{config.source}_token",
        config.token,
        description=f"Access token for {config.source}",
        is_encrypted=True,
    )
    db.commit()

    return {"message": f"{config.source} token configured successfully"}


@router.get("/current-llm-provider")
def get_current_llm_provider(
    current_user: User = Depends(get_current_admin_user),
    repo: SettingsRepository = Depends(_get_settings_repo),
):
    """Get current LLM provider"""
    provider_setting = repo.get_by_key("llm_provider")

    return {
        "provider": provider_setting.value if provider_setting else "not_configured"
    }


class TestConnectionResponse(BaseModel):
    success: bool
    message: str


@router.post("/test-llm-connection", response_model=TestConnectionResponse)
def test_llm_connection(
    current_user: User = Depends(get_current_admin_user),
    repo: SettingsRepository = Depends(_get_settings_repo),
):
    """Test that the configured LLM API key works (admin only)"""
    provider_setting = repo.get_by_key("llm_provider")

    if not provider_setting:
        return TestConnectionResponse(
            success=False,
            message="No LLM provider configured. Please configure one first."
        )

    provider = provider_setting.value
    api_key_setting = repo.get_by_key(f"{provider}_api_key")

    if not api_key_setting:
        return TestConnectionResponse(
            success=False,
            message=f"No API key found for provider '{provider}'."
        )

    # Build kwargs for Azure
    kwargs = {}
    if provider == "azure":
        endpoint_setting = repo.get_by_key("azure_endpoint")
        deployment_setting = repo.get_by_key("azure_deployment_name")
        if not endpoint_setting or not deployment_setting:
            return TestConnectionResponse(
                success=False,
                message="Azure requires endpoint and deployment name to be configured."
            )
        kwargs["endpoint"] = endpoint_setting.value
        kwargs["deployment_name"] = deployment_setting.value

    try:
        from app.services.llm_service import LLMService
        service = LLMService(
            provider=provider,
            api_key=api_key_setting.value,
            **kwargs
        )
        from langchain.schema import HumanMessage
        response = service.client.invoke([HumanMessage(content="Reply with OK")])
        return TestConnectionResponse(
            success=True,
            message=f"Connection to {provider} successful."
        )
    except Exception as e:
        return TestConnectionResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )
