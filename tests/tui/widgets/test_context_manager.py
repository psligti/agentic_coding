"""Tests for ContextManager"""

import pytest

from opencode_python.tui.context_manager import ContextManager, RunState


def test_context_manager_instantiation():
    """Test that ContextManager can be instantiated"""
    manager = ContextManager()
    assert manager is not None
    assert isinstance(manager, ContextManager)


def test_context_manager_initial_state():
    """Test that ContextManager initializes with empty state"""
    manager = ContextManager()
    assert manager.provider_id == ""
    assert manager.account_id == ""
    assert manager.model_id == ""
    assert manager.agent == ""
    assert manager.session_id == ""
    assert manager.run_state == RunState.IDLE


def test_context_manager_switch_provider():
    """Test that switch_provider updates provider_id"""
    manager = ContextManager()
    manager.switch_provider("openai")

    assert manager.provider_id == "openai"


def test_context_manager_switch_provider_clears_dependent():
    """Test that switch_provider clears dependent states"""
    manager = ContextManager()
    manager.account_id = "account1"
    manager.model_id = "gpt-4"

    manager.switch_provider("anthropic")

    assert manager.provider_id == "anthropic"
    assert manager.account_id == ""
    assert manager.model_id == ""


def test_context_manager_switch_account():
    """Test that switch_account updates account_id"""
    manager = ContextManager()
    manager.switch_account("default")

    assert manager.account_id == "default"


def test_context_manager_switch_model():
    """Test that switch_model updates model_id"""
    manager = ContextManager()
    manager.switch_model("gpt-4")

    assert manager.model_id == "gpt-4"


def test_context_manager_switch_agent():
    """Test that switch_agent updates agent"""
    manager = ContextManager()
    manager.switch_agent("assistant")

    assert manager.agent == "assistant"


def test_context_manager_switch_session():
    """Test that switch_session updates session_id"""
    manager = ContextManager()
    manager.switch_session("session-123")

    assert manager.session_id == "session-123"


def test_context_manager_undo_stack_initially_empty():
    """Test that undo stack is initially empty"""
    manager = ContextManager()
    assert len(manager._undo_stack) == 0


def test_context_manager_undo_stack_tracks_provider():
    """Test that undo stack tracks provider changes"""
    manager = ContextManager()
    manager.switch_provider("openai")
    manager.switch_provider("anthropic")

    assert len(manager._undo_stack) == 2


def test_context_manager_undo_stack_tracks_account():
    """Test that undo stack tracks account changes"""
    manager = ContextManager()
    manager.switch_account("account1")
    manager.switch_account("account2")

    assert len(manager._undo_stack) == 2


def test_context_manager_undo_stack_tracks_model():
    """Test that undo stack tracks model changes"""
    manager = ContextManager()
    manager.switch_model("gpt-4")
    manager.switch_model("gpt-3.5-turbo")

    assert len(manager._undo_stack) == 2


def test_context_manager_undo_stack_tracks_agent():
    """Test that undo stack tracks agent changes"""
    manager = ContextManager()
    manager.switch_agent("assistant")
    manager.switch_agent("builder")

    assert len(manager._undo_stack) == 2


def test_context_manager_undo_stack_tracks_session():
    """Test that undo stack tracks session changes"""
    manager = ContextManager()
    manager.switch_session("session-1")
    manager.switch_session("session-2")

    assert len(manager._undo_stack) == 2


def test_context_manager_undo_last_empty_stack():
    """Test that undo_last returns None when stack is empty"""
    manager = ContextManager()
    result = manager.undo_last()

    assert result is None


def test_context_manager_undo_last_returns_entry():
    """Test that undo_last returns the last undo entry"""
    manager = ContextManager()
    manager.switch_provider("openai")
    manager.switch_provider("anthropic")

    undo_entry = manager.undo_last()

    assert undo_entry is not None
    assert undo_entry[0] == "provider"
    assert undo_entry[1] == "openai"
    assert undo_entry[2] == "anthropic"


def test_context_manager_undo_removes_entry():
    """Test that undo_last removes entry from stack"""
    manager = ContextManager()
    manager.switch_provider("openai")
    manager.switch_provider("anthropic")

    assert len(manager._undo_stack) == 2

    undo_entry = manager.undo_last()

    assert len(manager._undo_stack) == 1


def test_context_manager_undo_stack_max_10():
    """Test that undo stack is limited to 10 entries"""
    manager = ContextManager()

    # Add 15 changes
    for i in range(15):
        manager.switch_provider(f"provider-{i}")

    # Stack should only have 10 entries
    assert len(manager._undo_stack) == 10


def test_context_manager_multiple_changes():
    """Test that multiple changes are tracked"""
    manager = ContextManager()
    manager.switch_provider("openai")
    manager.switch_account("default")
    manager.switch_model("gpt-4")
    manager.switch_agent("assistant")
    manager.switch_session("session-123")

    assert len(manager._undo_stack) == 5


def test_context_manager_undo_order():
    """Test that undo maintains correct order"""
    manager = ContextManager()
    manager.switch_provider("openai")
    manager.switch_provider("anthropic")
    manager.switch_provider("cohere")

    # First undo should be the most recent change
    undo1 = manager.undo_last()
    assert undo1[1] == "anthropic"
    assert undo1[2] == "cohere"

    # Second undo should be the previous change
    undo2 = manager.undo_last()
    assert undo2[1] == "openai"
    assert undo2[2] == "anthropic"


def test_context_manager_state_after_multiple_changes():
    """Test that state is correct after multiple changes"""
    manager = ContextManager()
    manager.switch_provider("openai")
    manager.switch_account("default")
    manager.switch_model("gpt-4")

    assert manager.provider_id == "openai"
    assert manager.account_id == "default"
    assert manager.model_id == "gpt-4"


def test_context_manager_undo_structure():
    """Test that undo entry has correct structure"""
    manager = ContextManager()
    manager.switch_provider("openai")

    undo_entry = manager.undo_last()

    assert isinstance(undo_entry, tuple)
    assert len(undo_entry) == 3
    assert isinstance(undo_entry[0], str)
    assert isinstance(undo_entry[1], str)
    assert isinstance(undo_entry[2], str)


def test_context_manager_context_types():
    """Test that all context types are tracked"""
    manager = ContextManager()

    manager.switch_provider("p1")
    undo1 = manager.undo_last()
    assert undo1[0] == "provider"

    manager.switch_account("a1")
    undo2 = manager.undo_last()
    assert undo2[0] == "account"

    manager.switch_model("m1")
    undo3 = manager.undo_last()
    assert undo3[0] == "model"

    manager.switch_agent("agent1")
    undo4 = manager.undo_last()
    assert undo4[0] == "agent"

    manager.switch_session("s1")
    undo5 = manager.undo_last()
    assert undo5[0] == "session"


def test_context_manager_empty_string_handling():
    """Test that empty strings are handled correctly"""
    manager = ContextManager()
    manager.switch_provider("")
    manager.switch_account("")
    manager.switch_model("")

    # Should work without errors
    assert manager.provider_id == ""
    assert manager.account_id == ""
    assert manager.model_id == ""


def test_context_manager_special_characters():
    """Test that special characters in IDs are handled"""
    manager = ContextManager()
    manager.switch_provider("provider@domain.com")
    manager.switch_account("account:123")
    manager.switch_session("session-2024_Q1")

    assert manager.provider_id == "provider@domain.com"
    assert manager.account_id == "account:123"
    assert manager.session_id == "session-2024_Q1"


def test_context_manager_long_ids():
    """Test that long IDs are handled"""
    long_id = "very-long-id-" + "a" * 100
    manager = ContextManager()
    manager.switch_provider(long_id)

    assert manager.provider_id == long_id
