"""Tool listing endpoints for WebApp API."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from opencode_python.tools import create_complete_registry


router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_tools() -> List[Dict[str, Any]]:
    """List all available tools.

    Returns:
        List of tool summaries with metadata.
    """
    try:
        registry = await create_complete_registry()
        tools = await registry.get_all()
        return [
            {
                "id": tool_id,
                "description": tool.description,
                "category": getattr(tool, "category", None),
                "tags": getattr(tool, "tags", None),
            }
            for tool_id, tool in tools.items()
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}",
        )
