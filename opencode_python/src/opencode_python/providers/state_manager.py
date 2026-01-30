"""OpenCode Python - Provider State Manager

Manages active provider/account/model selection with persistence and event emission.
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from pathlib import Path
import json
import asyncio
import logging

from opencode_python.core.event_bus import bus


logger = logging.getLogger(__name__)


# Event constants
PROVIDER_CHANGED = "provider:changed"
ACCOUNT_CHANGED = "account:changed"
MODEL_CHANGED = "model:changed"


class ProviderStateManager:
    """Manages active provider/account/model selection with persistence

    Tracks the currently active provider, account, and model, persists
    the selection to ~/.opencode/provider_selection.json, and emits
    events when state changes occur.
    """

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize provider state manager

        Args:
            config_dir: Directory for storing state (default: ~/.opencode/)
        """
        if config_dir is None:
            config_dir = Path.home() / ".opencode"

        self.config_dir = Path(config_dir)
        self.state_file = self.config_dir / "provider_selection.json"

        # Current active selections
        self._provider_id: Optional[str] = None
        self._account_id: Optional[str] = None
        self._model_id: Optional[str] = None

        # Lock for thread-safe state updates
        self._lock = asyncio.Lock()

    async def load_selection(self) -> Dict[str, Optional[str]]:
        """Load saved selection from disk

        Returns:
            Dictionary with current provider_id, account_id, and model_id
        """
        try:
            if self.state_file.exists():
                data = await asyncio.to_thread(self._load_file)
                self._provider_id = data.get("provider_id")
                self._account_id = data.get("account_id")
                self._model_id = data.get("model_id")
                logger.info(
                    f"Loaded provider selection: "
                    f"provider={self._provider_id}, "
                    f"account={self._account_id}, "
                    f"model={self._model_id}"
                )
            else:
                logger.info("No saved provider selection found, using defaults")
        except Exception as e:
            logger.error(f"Error loading provider selection: {e}")

        return {
            "provider_id": self._provider_id,
            "account_id": self._account_id,
            "model_id": self._model_id
        }

    def _load_file(self) -> Dict[str, Any]:
        """Load JSON file (sync, called within asyncio.to_thread)"""
        with open(self.state_file, "r") as f:
            return json.load(f)

    def _save_file(self, data: Dict[str, Any]) -> None:
        """Save JSON file (sync, called within asyncio.to_thread)"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    async def _persist(self) -> None:
        """Persist current state to disk"""
        data = {
            "provider_id": self._provider_id,
            "account_id": self._account_id,
            "model_id": self._model_id
        }
        try:
            await asyncio.to_thread(self._save_file, data)
            logger.debug(f"Persisted provider selection: {data}")
        except Exception as e:
            logger.error(f"Error persisting provider selection: {e}")

    @property
    def provider_id(self) -> Optional[str]:
        """Get current provider ID"""
        return self._provider_id

    @property
    def account_id(self) -> Optional[str]:
        """Get current account ID"""
        return self._account_id

    @property
    def model_id(self) -> Optional[str]:
        """Get current model ID"""
        return self._model_id

    def get_state(self) -> Dict[str, Optional[str]]:
        """Get current state

        Returns:
            Dictionary with provider_id, account_id, and model_id
        """
        return {
            "provider_id": self._provider_id,
            "account_id": self._account_id,
            "model_id": self._model_id
        }

    async def set_provider(self, provider_id: str) -> None:
        """Set active provider

        Emits PROVIDER_CHANGED event when provider changes.

        Args:
            provider_id: Provider ID to set as active
        """
        async with self._lock:
            if self._provider_id == provider_id:
                return  # No change

            old_provider_id = self._provider_id
            self._provider_id = provider_id

            await self._persist()

            await bus.publish(PROVIDER_CHANGED, {
                "old_provider_id": old_provider_id,
                "new_provider_id": provider_id
            })

            logger.info(f"Provider changed: {old_provider_id} -> {provider_id}")

    async def set_account(self, account_id: str) -> None:
        """Set active account

        Emits ACCOUNT_CHANGED event when account changes.

        Args:
            account_id: Account ID to set as active
        """
        async with self._lock:
            if self._account_id == account_id:
                return  # No change

            old_account_id = self._account_id
            self._account_id = account_id

            await self._persist()

            await bus.publish(ACCOUNT_CHANGED, {
                "old_account_id": old_account_id,
                "new_account_id": account_id,
                "provider_id": self._provider_id
            })

            logger.info(f"Account changed: {old_account_id} -> {account_id}")

    async def set_model(self, model_id: str) -> None:
        """Set active model

        Emits MODEL_CHANGED event when model changes.

        Args:
            model_id: Model ID to set as active
        """
        async with self._lock:
            if self._model_id == model_id:
                return  # No change

            old_model_id = self._model_id
            self._model_id = model_id

            await self._persist()

            await bus.publish(MODEL_CHANGED, {
                "old_model_id": old_model_id,
                "new_model_id": model_id,
                "provider_id": self._provider_id,
                "account_id": self._account_id
            })

            logger.info(f"Model changed: {old_model_id} -> {model_id}")

    async def clear_provider(self) -> None:
        """Clear active provider

        Emits PROVIDER_CHANGED event when provider is cleared.
        """
        async with self._lock:
            if self._provider_id is None:
                return  # Already cleared

            old_provider_id = self._provider_id
            self._provider_id = None
            self._account_id = None
            self._model_id = None

            await self._persist()

            await bus.publish(PROVIDER_CHANGED, {
                "old_provider_id": old_provider_id,
                "new_provider_id": None
            })

            logger.info(f"Provider cleared: {old_provider_id}")

    async def clear_account(self) -> None:
        """Clear active account

        Emits ACCOUNT_CHANGED event when account is cleared.
        """
        async with self._lock:
            if self._account_id is None:
                return  # Already cleared

            old_account_id = self._account_id
            self._account_id = None
            self._model_id = None

            await self._persist()

            await bus.publish(ACCOUNT_CHANGED, {
                "old_account_id": old_account_id,
                "new_account_id": None,
                "provider_id": self._provider_id
            })

            logger.info(f"Account cleared: {old_account_id}")

    async def clear_model(self) -> None:
        """Clear active model

        Emits MODEL_CHANGED event when model is cleared.
        """
        async with self._lock:
            if self._model_id is None:
                return  # Already cleared

            old_model_id = self._model_id
            self._model_id = None

            await self._persist()

            await bus.publish(MODEL_CHANGED, {
                "old_model_id": old_model_id,
                "new_model_id": None,
                "provider_id": self._provider_id,
                "account_id": self._account_id
            })

            logger.info(f"Model cleared: {old_model_id}")

    async def reset(self) -> None:
        """Reset all selections to None

        Emits appropriate events for each cleared value.
        """
        provider_id = self._provider_id
        account_id = self._account_id
        model_id = self._model_id

        self._provider_id = None
        self._account_id = None
        self._model_id = None

        await self._persist()

        # Emit events for each cleared value
        if provider_id is not None:
            await bus.publish(PROVIDER_CHANGED, {
                "old_provider_id": provider_id,
                "new_provider_id": None
            })

        if account_id is not None:
            await bus.publish(ACCOUNT_CHANGED, {
                "old_account_id": account_id,
                "new_account_id": None,
                "provider_id": None
            })

        if model_id is not None:
            await bus.publish(MODEL_CHANGED, {
                "old_model_id": model_id,
                "new_model_id": None,
                "provider_id": None,
                "account_id": None
            })

        logger.info("Provider state reset")


# Global instance (can be overridden for testing)
_state_manager: Optional[ProviderStateManager] = None


def get_state_manager(config_dir: Optional[Path] = None) -> ProviderStateManager:
    """Get or create the global state manager instance

    Args:
        config_dir: Directory for storing state (only used on first call)

    Returns:
        ProviderStateManager instance
    """
    global _state_manager
    if _state_manager is None:
        _state_manager = ProviderStateManager(config_dir=config_dir)
    return _state_manager


__all__ = [
    "PROVIDER_CHANGED",
    "ACCOUNT_CHANGED",
    "MODEL_CHANGED",
    "ProviderStateManager",
    "get_state_manager",
]
