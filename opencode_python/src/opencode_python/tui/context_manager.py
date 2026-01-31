"""Context Manager for Vertical Stack TUI
Manages provider/account/model/agent/session state with validation.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from textual.reactive import reactive


class RunState(Enum):
    """Run state enum"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


class ContextManager:
    """Manages current context state with undo support"""
    
    def __init__(self):
        """Initialize ContextManager with empty state"""
        self.provider_id: ""
        self.account_id = ""
        self.model_id = ""
        self.agent = ""
        self.session_id = ""
        self.run_state = RunState.IDLE
        
        # Undo stack (max 10 entries)
        self._undo_stack: list[tuple[str, str, str]] = []
    
    def switch_provider(self, provider_id: str) -> None:
        """Switch provider"""
        old = self.provider_id
        self.provider_id = provider_id
        self._push_undo("provider", old, provider_id)
        # Clear dependent states when provider changes
        self.account_id = ""
        self.model_id = ""
    
    def switch_account(self, account_id: str) -> None:
        """Switch account"""
        old = self.account_id
        self.account_id = account_id
        self._push_undo("account", old, account_id)
    
    def switch_model(self, model_id: str) -> None:
        """Switch model"""
        old = self.model_id
        self.model_id = model_id
        self._push_undo("model", old, model_id)
    
    def switch_agent(self, agent: str) -> None:
        """Switch agent"""
        old = self.agent
        self.agent = agent
        self._push_undo("agent", old, agent)
    
    def switch_session(self, session_id: str) -> None:
        """Switch session"""
        old = self.session_id
        self.session_id = session_id
        self._push_undo("session", old, session_id)
    
    def undo_last(self) -> Optional[tuple[str, str, str]]:
        """Undo last context switch"""
        if not self._undo_stack:
            return None
        return self._undo_stack.pop()
    
    def _push_undo(self, context_type: str, old_value: str, new_value: str) -> None:
        """Push to undo stack"""
        self._undo_stack.append((context_type, old_value, new_value))
        # Keep only last 10
        if len(self._undo_stack) > 10:
            self._undo_stack = self._undo_stack[-10:]
