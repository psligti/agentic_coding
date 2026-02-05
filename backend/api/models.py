"""Model listing endpoints for WebApp API."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from api.sessions import get_sdk_client


router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_models() -> List[Dict[str, Any]]:
    """List models from configured accounts.

    Returns:
        List of model summaries from provider configurations.
    """
    try:
        client = await get_sdk_client()
        providers = await client.list_providers()

        models: List[Dict[str, Any]] = []
        for provider in providers:
            config = provider.get("config", {})
            models.append({
                "name": provider.get("name"),
                "provider_id": config.get("provider_id"),
                "model": config.get("model"),
                "is_default": provider.get("is_default", False),
            })

        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}",
        )
