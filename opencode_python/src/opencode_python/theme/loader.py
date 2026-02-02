"""
Theme Loader - Load and resolve themes for opencode_python

Provides theme discovery, loading, and auto-detection of system dark/light mode.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, List
import json
import logging

try:
    import darkdetect
except ImportError:
    darkdetect = None

from opencode_python.theme.models import Theme


__all__ = [
    "load_theme",
    "get_available_themes",
    "resolve_theme",
]

THEMES_DIR = Path(__file__).parent / "themes"
BUNDLED_THEMES = ["dracula", "gruvbox", "catppuccin", "nord", "tokyonight", "onedarkpro"]
DEFAULT_THEME = "dracula"
DEFAULT_MODE = "dark"

logger = logging.getLogger(__name__)


def load_theme(theme_name: str) -> Optional[Theme]:
    """Load a theme by name from bundled theme files

    Args:
        theme_name: Name of the theme (e.g., "dracula", "gruvbox")

    Returns:
        Theme object if found and valid, None otherwise
    """
    try:
        theme_file = THEMES_DIR / f"{theme_name}.json"
        if not theme_file.exists():
            logger.warning(f"Theme file not found: {theme_file}")
            return None

        with open(theme_file, "r", encoding="utf-8") as f:
            theme_data = json.load(f)

        theme = Theme.model_validate(theme_data)
        logger.debug(f"Loaded theme: {theme.name}")
        return theme

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in theme file {theme_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load theme {theme_name}: {e}")
        return None


def get_available_themes() -> List[str]:
    """Get list of available bundled theme names

    Returns:
        List of theme identifiers (e.g., ["dracula", "gruvbox", ...])
    """
    available = []
    for theme_name in BUNDLED_THEMES:
        theme_file = THEMES_DIR / f"{theme_name}.json"
        if theme_file.exists():
            available.append(theme_name)
    return available


def detect_system_mode() -> str:
    """Detect system dark/light mode using darkdetect

    Returns:
        "dark" or "light" based on system preference
        Falls back to "dark" if darkdetect is unavailable or returns None
    """
    if darkdetect is None:
        logger.debug("darkdetect not available, defaulting to dark mode")
        return "dark"

    try:
        mode = darkdetect.theme()
        if mode == "Light":
            return "light"
        elif mode == "Dark":
            return "dark"
        else:
            logger.debug(f"darkdetect returned {mode}, defaulting to dark mode")
            return "dark"
    except Exception as e:
        logger.warning(f"Failed to detect system mode: {e}, defaulting to dark mode")
        return "dark"


def resolve_theme(theme_name: str) -> Theme:
    """Resolve a theme name to a Theme object

    Handles "auto" mode by detecting system dark/light mode.
    Falls back to default theme if requested theme is not found.

    Args:
        theme_name: Theme name (e.g., "dracula", "auto")

    Returns:
        Theme object (never None, always returns a valid theme)
    """
    # Auto mode: detect system theme
    if theme_name == "auto":
        mode = detect_system_mode()
        theme_name = f"{DEFAULT_THEME}-{mode}"
        logger.debug(f"Auto-resolved to theme: {theme_name}")

    # Try to load the requested theme
    theme = load_theme(theme_name)
    if theme is not None:
        return theme

    # Fallback to default dark theme
    logger.warning(f"Theme {theme_name} not found, falling back to {DEFAULT_THEME}-{DEFAULT_MODE}")
    fallback_theme = load_theme(f"{DEFAULT_THEME}-{DEFAULT_MODE}")
    if fallback_theme is not None:
        return fallback_theme

    # Ultimate fallback: if even default fails, raise error
    raise RuntimeError(f"Failed to load theme {theme_name} and fallback {DEFAULT_THEME}-{DEFAULT_MODE}")
