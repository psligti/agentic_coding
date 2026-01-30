"""Tests for ProviderStateManager"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
import json

from opencode_python.providers.state_manager import (
    ProviderStateManager,
    get_state_manager,
    PROVIDER_CHANGED,
    ACCOUNT_CHANGED,
    MODEL_CHANGED,
)


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def state_manager(temp_config_dir):
    """Create ProviderStateManager with temporary config dir"""
    manager = ProviderStateManager(config_dir=temp_config_dir)
    return manager


@pytest.mark.asyncio
async def test_state_manager_initialization(state_manager):
    """Test that ProviderStateManager initializes with no selections"""
    assert state_manager.provider_id is None
    assert state_manager.account_id is None
    assert state_manager.model_id is None

    state = state_manager.get_state()
    assert state == {
        "provider_id": None,
        "account_id": None,
        "model_id": None
    }


@pytest.mark.asyncio
async def test_set_provider(state_manager):
    """Test setting active provider"""
    await state_manager.set_provider("anthropic")

    assert state_manager.provider_id == "anthropic"
    assert state_manager.get_state()["provider_id"] == "anthropic"


@pytest.mark.asyncio
async def test_set_account(state_manager):
    """Test setting active account"""
    await state_manager.set_account("account-123")

    assert state_manager.account_id == "account-123"
    assert state_manager.get_state()["account_id"] == "account-123"


@pytest.mark.asyncio
async def test_set_model(state_manager):
    """Test setting active model"""
    await state_manager.set_model("claude-sonnet-4")

    assert state_manager.model_id == "claude-sonnet-4"
    assert state_manager.get_state()["model_id"] == "claude-sonnet-4"


@pytest.mark.asyncio
async def test_persistence(state_manager, temp_config_dir):
    """Test that state persists to disk"""
    await state_manager.set_provider("openai")
    await state_manager.set_account("account-456")
    await state_manager.set_model("gpt-5")

    state_file = temp_config_dir / "provider_selection.json"
    assert state_file.exists()

    with open(state_file, "r") as f:
        data = json.load(f)

    assert data["provider_id"] == "openai"
    assert data["account_id"] == "account-456"
    assert data["model_id"] == "gpt-5"


@pytest.mark.asyncio
async def test_load_selection(state_manager, temp_config_dir):
    """Test loading saved selection on startup"""
    state_file = temp_config_dir / "provider_selection.json"
    temp_config_dir.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w") as f:
        json.dump({
            "provider_id": "anthropic",
            "account_id": "account-789",
            "model_id": "claude-sonnet-4"
        }, f)

    # Create new manager instance to test loading
    new_manager = ProviderStateManager(config_dir=temp_config_dir)
    await new_manager.load_selection()

    assert new_manager.provider_id == "anthropic"
    assert new_manager.account_id == "account-789"
    assert new_manager.model_id == "claude-sonnet-4"


@pytest.mark.asyncio
async def test_provider_changed_event(state_manager):
    """Test that PROVIDER_CHANGED event is emitted"""
    events = []

    async def capture_event(event):
        events.append(event.data)

    from opencode_python.core.event_bus import bus
    await bus.subscribe(PROVIDER_CHANGED, capture_event)

    await state_manager.set_provider("openai")

    assert len(events) == 1
    assert events[0]["new_provider_id"] == "openai"
    assert events[0]["old_provider_id"] is None


@pytest.mark.asyncio
async def test_account_changed_event(state_manager):
    """Test that ACCOUNT_CHANGED event is emitted"""
    events = []

    async def capture_event(event):
        events.append(event.data)

    from opencode_python.core.event_bus import bus
    await bus.subscribe(ACCOUNT_CHANGED, capture_event)

    await state_manager.set_account("account-123")

    assert len(events) == 1
    assert events[0]["new_account_id"] == "account-123"
    assert events[0]["old_account_id"] is None


@pytest.mark.asyncio
async def test_model_changed_event(state_manager):
    """Test that MODEL_CHANGED event is emitted"""
    events = []

    async def capture_event(event):
        events.append(event.data)

    from opencode_python.core.event_bus import bus
    await bus.subscribe(MODEL_CHANGED, capture_event)

    await state_manager.set_model("gpt-5")

    assert len(events) == 1
    assert events[0]["new_model_id"] == "gpt-5"
    assert events[0]["old_model_id"] is None


@pytest.mark.asyncio
async def test_clear_provider(state_manager):
    """Test clearing active provider"""
    await state_manager.set_provider("anthropic")
    assert state_manager.provider_id == "anthropic"

    await state_manager.clear_provider()
    assert state_manager.provider_id is None


@pytest.mark.asyncio
async def test_clear_account(state_manager):
    """Test clearing active account"""
    await state_manager.set_account("account-123")
    assert state_manager.account_id == "account-123"

    await state_manager.clear_account()
    assert state_manager.account_id is None


@pytest.mark.asyncio
async def test_clear_model(state_manager):
    """Test clearing active model"""
    await state_manager.set_model("claude-sonnet-4")
    assert state_manager.model_id == "claude-sonnet-4"

    await state_manager.clear_model()
    assert state_manager.model_id is None


@pytest.mark.asyncio
async def test_reset(state_manager):
    """Test resetting all selections"""
    await state_manager.set_provider("openai")
    await state_manager.set_account("account-456")
    await state_manager.set_model("gpt-5")

    await state_manager.reset()

    assert state_manager.provider_id is None
    assert state_manager.account_id is None
    assert state_manager.model_id is None


@pytest.mark.asyncio
async def test_setting_same_value_no_event(state_manager):
    """Test that setting the same value doesn't emit event"""
    events = []

    async def capture_event(event):
        events.append(event.data)

    from opencode_python.core.event_bus import bus
    await bus.subscribe(PROVIDER_CHANGED, capture_event)

    await state_manager.set_provider("openai")
    assert len(events) == 1

    await state_manager.set_provider("openai")
    assert len(events) == 1  # No new event


@pytest.mark.asyncio
async def test_clearing_already_clear_no_event(state_manager):
    """Test that clearing already cleared value doesn't emit event"""
    events = []

    async def capture_event(event):
        events.append(event.data)

    from opencode_python.core.event_bus import bus
    await bus.subscribe(ACCOUNT_CHANGED, capture_event)

    await state_manager.clear_account()
    assert len(events) == 0

    await state_manager.clear_account()
    assert len(events) == 0  # Still no event


@pytest.mark.asyncio
async def test_clear_provider_clears_related(state_manager):
    """Test that clearing provider also clears account and model"""
    await state_manager.set_provider("openai")
    await state_manager.set_account("account-456")
    await state_manager.set_model("gpt-5")

    await state_manager.clear_provider()

    assert state_manager.provider_id is None
    assert state_manager.account_id is None
    assert state_manager.model_id is None


@pytest.mark.asyncio
async def test_clear_account_clears_model(state_manager):
    """Test that clearing account also clears model"""
    await state_manager.set_provider("openai")
    await state_manager.set_account("account-456")
    await state_manager.set_model("gpt-5")

    await state_manager.clear_account()

    assert state_manager.provider_id == "openai"
    assert state_manager.account_id is None
    assert state_manager.model_id is None


@pytest.mark.asyncio
async def test_global_state_manager_singleton():
    """Test that get_state_manager returns singleton instance"""
    manager1 = get_state_manager()
    manager2 = get_state_manager()

    assert manager1 is manager2


@pytest.mark.asyncio
async def test_load_nonexistent_file(state_manager):
    """Test loading when state file doesn't exist"""
    state = await state_manager.load_selection()

    assert state == {
        "provider_id": None,
        "account_id": None,
        "model_id": None
    }


@pytest.mark.asyncio
async def test_changing_provider_emits_old_and_new(state_manager):
    """Test that changing provider emits both old and new values"""
    events = []

    async def capture_event(event):
        events.append(event.data)

    from opencode_python.core.event_bus import bus
    await bus.subscribe(PROVIDER_CHANGED, capture_event)

    await state_manager.set_provider("openai")
    await state_manager.set_provider("anthropic")

    assert len(events) == 2
    assert events[0]["old_provider_id"] is None
    assert events[0]["new_provider_id"] == "openai"
    assert events[1]["old_provider_id"] == "openai"
    assert events[1]["new_provider_id"] == "anthropic"


@pytest.mark.asyncio
async def test_state_manager_creates_config_dir(temp_config_dir):
    """Test that state manager creates config directory if needed"""
    manager = ProviderStateManager(config_dir=temp_config_dir / "nested" / "dir")

    await manager.set_provider("openai")

    state_file = temp_config_dir / "nested" / "dir" / "provider_selection.json"
    assert state_file.exists()
    assert state_file.parent.exists()
