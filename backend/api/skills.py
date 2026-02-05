"""Skill listing endpoints for WebApp API."""

from typing import Any, Dict, List
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from opencode_python.skills.loader import SkillLoader
from api.sessions import get_sdk_client


router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_skills() -> List[Dict[str, Any]]:
    """List all available skills.

    Returns:
        List of skill summaries with metadata.
    """
    try:
        client = await get_sdk_client()
        loader = SkillLoader(base_dir=Path(client.config.project_dir))
        skills = loader.discover_skills()
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "location": str(skill.location),
            }
            for skill in skills
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list skills: {str(e)}",
        )
