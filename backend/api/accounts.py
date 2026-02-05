"""Account (provider configuration) endpoints for WebApp API."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel

from api.sessions import get_sdk_client


class AccountCreateRequest(BaseModel):
    """Request model for creating an account."""

    name: str
    provider_id: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False


class AccountUpdateRequest(BaseModel):
    """Request model for updating an account."""

    provider_id: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False


router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


def _sanitize_provider(provider: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive fields from provider responses."""
    config = provider.get("config", {})
    sanitized_config = {
        "provider_id": config.get("provider_id"),
        "model": config.get("model"),
        "base_url": config.get("base_url"),
        "options": config.get("options", {}),
        "description": config.get("description"),
    }

    return {
        "name": provider.get("name"),
        "config": sanitized_config,
        "is_default": provider.get("is_default", False),
    }


@router.get("", response_model=List[Dict[str, Any]])
async def list_accounts() -> List[Dict[str, Any]]:
    """List configured provider accounts."""
    try:
        client = await get_sdk_client()
        providers = await client.list_providers()
        return [_sanitize_provider(provider) for provider in providers]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list accounts: {str(e)}",
        )


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_account(request: AccountCreateRequest = Body(...)) -> Dict[str, Any]:
    """Create a new provider account."""
    if not request.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account name is required",
        )

    try:
        client = await get_sdk_client()
        await client.register_provider(
            name=request.name,
            provider_id=request.provider_id,
            model=request.model,
            api_key=request.api_key,
            is_default=request.is_default,
        )

        if request.is_default:
            await client._provider_registry.set_default_provider(request.name)

        providers = await client.list_providers()
        for provider in providers:
            if provider.get("name") == request.name:
                return _sanitize_provider(provider)

        return {
            "name": request.name,
            "config": {
                "provider_id": request.provider_id,
                "model": request.model,
                "base_url": request.base_url,
                "description": request.description,
            },
            "is_default": request.is_default,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}",
        )


@router.put("/{account_name}", response_model=Dict[str, Any])
async def update_account(account_name: str, request: AccountUpdateRequest = Body(...)) -> Dict[str, Any]:
    """Update an existing provider account."""
    try:
        client = await get_sdk_client()
        await client.update_provider(
            name=account_name,
            provider_id=request.provider_id,
            model=request.model,
            api_key=request.api_key,
        )

        if request.is_default:
            await client._provider_registry.set_default_provider(account_name)

        providers = await client.list_providers()
        for provider in providers:
            if provider.get("name") == account_name:
                return _sanitize_provider(provider)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account not found: {account_name}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account: {str(e)}",
        )


@router.delete("/{account_name}", response_model=Dict[str, Any])
async def delete_account(account_name: str) -> Dict[str, Any]:
    """Delete a provider account."""
    try:
        client = await get_sdk_client()
        removed = await client.remove_provider(account_name)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account not found: {account_name}",
            )

        return {
            "message": "Account removed",
            "name": account_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}",
        )


@router.post("/{account_name}/default", response_model=Dict[str, Any])
async def set_default_account(account_name: str) -> Dict[str, Any]:
    """Set the default provider account."""
    try:
        client = await get_sdk_client()
        await client._provider_registry.set_default_provider(account_name)
        providers = await client.list_providers()
        for provider in providers:
            if provider.get("name") == account_name:
                return _sanitize_provider(provider)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account not found: {account_name}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default account: {str(e)}",
        )
