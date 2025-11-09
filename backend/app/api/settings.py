from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_admin_user
from app.models.user import User
from app.models.settings import SystemSettings
from app.schemas.settings import SystemSettingUpdate, SystemSettingResponse, LLMProviderConfig, GitConfig

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=List[SystemSettingResponse])
def list_settings(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all system settings (admin only)"""
    settings = db.query(SystemSettings).all()

    # Mask sensitive values
    for setting in settings:
        if setting.is_encrypted or "key" in setting.key.lower() or "token" in setting.key.lower():
            setting.value = "***"

    return settings


@router.put("/llm-provider", response_model=dict)
def configure_llm_provider(
    config: LLMProviderConfig,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Configure LLM provider (admin only)"""
    # Update or create provider setting
    provider_setting = db.query(SystemSettings).filter(
        SystemSettings.key == "llm_provider"
    ).first()

    if provider_setting:
        provider_setting.value = config.provider
    else:
        provider_setting = SystemSettings(
            key="llm_provider",
            value=config.provider,
            description="Active LLM provider"
        )
        db.add(provider_setting)

    # Update or create API key
    api_key_setting = db.query(SystemSettings).filter(
        SystemSettings.key == f"{config.provider}_api_key"
    ).first()

    if api_key_setting:
        api_key_setting.value = config.api_key
    else:
        api_key_setting = SystemSettings(
            key=f"{config.provider}_api_key",
            value=config.api_key,
            is_encrypted=True,
            description=f"API key for {config.provider}"
        )
        db.add(api_key_setting)

    # For Azure, store additional settings
    if config.provider == "azure":
        if config.endpoint:
            endpoint_setting = db.query(SystemSettings).filter(
                SystemSettings.key == "azure_endpoint"
            ).first()
            if endpoint_setting:
                endpoint_setting.value = config.endpoint
            else:
                endpoint_setting = SystemSettings(
                    key="azure_endpoint",
                    value=config.endpoint,
                    description="Azure OpenAI endpoint"
                )
                db.add(endpoint_setting)

        if config.deployment_name:
            deployment_setting = db.query(SystemSettings).filter(
                SystemSettings.key == "azure_deployment_name"
            ).first()
            if deployment_setting:
                deployment_setting.value = config.deployment_name
            else:
                deployment_setting = SystemSettings(
                    key="azure_deployment_name",
                    value=config.deployment_name,
                    description="Azure OpenAI deployment name"
                )
                db.add(deployment_setting)

    db.commit()

    return {"message": f"LLM provider '{config.provider}' configured successfully"}


@router.put("/git-config", response_model=dict)
def configure_git(
    config: GitConfig,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Configure Git provider token (admin only)"""
    token_key = f"{config.source}_token"

    token_setting = db.query(SystemSettings).filter(
        SystemSettings.key == token_key
    ).first()

    if token_setting:
        token_setting.value = config.token
    else:
        token_setting = SystemSettings(
            key=token_key,
            value=config.token,
            is_encrypted=True,
            description=f"Access token for {config.source}"
        )
        db.add(token_setting)

    db.commit()

    return {"message": f"{config.source} token configured successfully"}


@router.get("/current-llm-provider")
def get_current_llm_provider(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get current LLM provider"""
    provider_setting = db.query(SystemSettings).filter(
        SystemSettings.key == "llm_provider"
    ).first()

    return {
        "provider": provider_setting.value if provider_setting else "not_configured"
    }
