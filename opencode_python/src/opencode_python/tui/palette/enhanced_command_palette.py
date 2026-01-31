"""OpenCode Python - Enhanced Command Palette with Scoped Search

Extended command palette with:
- Scoped search with prefixes (p:, a:, m:, g:, s:)
- RecentsManager integration for LRU tracking
- Grouped display with recents first
- Fuzzy match scoring and ranking
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal
from textual.message import Message
from rich.text import Text

from opencode_python.tui.palette.recents_manager import RecentsManager

# Data model imports
from opencode_python.providers_mgmt.models import Provider, Account
from opencode_python.providers.base import ModelInfo
from opencode_python.agents.profiles import AgentProfile

logger = logging.getLogger(__name__)


class EnhancedCommandExecute(Message):
    """Emitted when a command should be executed."""

    def __init__(self, scope: str, item_id: str, data: dict) -> None:
        super().__init__()
        self.scope = scope
        self.item_id = item_id
        self.data = data


class PaletteOpen(Message):
    """Emitted when command palette is opened."""
    pass


# Scope prefixes
SCOPE_PREFIXES = {
    "p": "providers",
    "a": "accounts",
    "m": "models",
    "g": "agents",
    "s": "sessions",
}

# Reverse mapping
PREFIX_FROM_SCOPE = {v: k for k, v in SCOPE_PREFIXES.items()}


@dataclass
class PaletteItem:
    """Represents an item in the command palette."""

    id: str
    title: str
    description: str
    scope: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: int = 0


class FuzzyMatcher:
    """Fuzzy string matching with scoring."""

    @staticmethod
    def match(query: str, text: str) -> Tuple[bool, int]:
        """Check if query matches text with fuzzy matching.

        Args:
            query: Search query string.
            text: Text to match against.

        Returns:
            Tuple of (matches, score).
            Score is higher for better matches.
        """
        query = query.lower()
        text = text.lower()

        if not query:
            return True, 0

        # Exact match - highest score
        if query == text:
            return True, 1000

        # Starts with query - high score
        if text.startswith(query):
            return True, 800

        # Contains query - medium score
        if query in text:
            return True, 600

        # Fuzzy match - check if all characters appear in order
        query_chars = list(query)
        text_chars = list(text)
        query_idx = 0

        for char in text_chars:
            if query_idx < len(query_chars) and char == query_chars[query_idx]:
                query_idx += 1

        if query_idx == len(query_chars):
            # All characters found in order
            return True, 400

        # Substring match (lenient) - low score
        if len(query) >= 2:
            for i in range(len(text) - len(query) + 1):
                if text[i:i+len(query)] in query:
                    return True, 200

        return False, 0


class EnhancedCommandPalette(ModalScreen[str]):
    """Enhanced command palette with scoped search and recents."""

    def __init__(
        self,
        storage_path: Path,
        providers: Optional[List[Provider]] = None,
        accounts: Optional[List[Account]] = None,
        models: Optional[List[ModelInfo]] = None,
        agents: Optional[List[AgentProfile]] = None,
        sessions: Optional[List[Dict[str, Any]]] = None,
        on_execute: Optional[Callable[[str, str], None]] = None,
    ):
        """Initialize enhanced command palette.

        Args:
            storage_path: Path for recents storage.
            providers: List of available providers.
            accounts: List of available accounts.
            models: List of available models.
            agents: List of available agents.
            sessions: List of available sessions.
            on_execute: Callback when item is executed (scope, item_id).
        """
        super().__init__()
        self.storage_path = storage_path
        self.recents_manager = RecentsManager(storage_path)

        # Data sources
        self.providers = providers or []
        self.accounts = accounts or []
        self.models = models or []
        self.agents = agents or []
        self.sessions = sessions or []

        self.on_execute = on_execute

        # State
        self._result: Optional[str] = None
        self._filtered_items: List[PaletteItem] = []
        self._selected_index: int = 0
        self._current_scope: Optional[str] = None

        # Build item cache
        self._all_items: List[PaletteItem] = self._build_all_items()

    def _build_all_items(self) -> List[PaletteItem]:
        """Build list of all searchable items from data sources."""
        items = []

        # Providers
        for provider in self.providers:
            items.append(PaletteItem(
                id=provider.id,
                title=provider.name,
                description=provider.description or "AI provider",
                scope="providers",
                metadata={"base_url": provider.base_url}
            ))

        # Accounts
        for account in self.accounts:
            items.append(PaletteItem(
                id=account.id,
                title=account.name,
                description=account.description or f"Account for {account.provider_id}",
                scope="accounts",
                metadata={"provider_id": account.provider_id, "is_active": account.is_active}
            ))

        # Models
        for model in self.models:
            items.append(PaletteItem(
                id=model.id,
                title=model.name,
                description=f"{model.family} model",
                scope="models",
                metadata={"provider_id": model.provider_id.value, "api_id": model.api_id}
            ))

        # Agents
        for agent in self.agents:
            items.append(PaletteItem(
                id=agent.id,
                title=agent.name,
                description=agent.description or "AI agent",
                scope="agents",
                metadata={"category": agent.category, "tags": agent.tags}
            ))

        # Sessions
        for session in self.sessions:
            session_id = session.get("id", "unknown")
            objective = session.get("meta", {}).get("objective", "No objective")
            items.append(PaletteItem(
                id=session_id,
                title=session_id[:50],  # Truncate long IDs
                description=objective[:80] if objective else "No objective",
                scope="sessions",
                metadata=session
            ))

        return items

    def compose(self) -> ComposeResult:
        """Compose enhanced command palette UI."""
        with Vertical(id="palette_container"):
            yield Label("Command Palette")

            # Search input with scope hint
            with Horizontal():
                yield Static("Search: ", id="search_label")
                yield Input(placeholder="Type to search (use p:, a:, m:, g:, s: for scopes)", id="palette_search")

            # Results list
            yield ListView(id="palette_list")

            # Footer with hints
            yield Static("↑↓ Navigate | Enter Select | Escape Cancel", id="palette_footer")

    def on_mount(self) -> None:
        """Called when palette is mounted."""
        self._filter_items("")

        # Focus search input
        search_input = self.query_one(Input)
        search_input.focus()

        # Emit palette:open event
        self.post_message(PaletteOpen(self))

    def _parse_query(self, query: str) -> Tuple[Optional[str], str]:
        """Parse query to extract scope prefix and search term.

        Args:
            query: Raw query string.

        Returns:
            Tuple of (scope, search_term).
            Scope is None if no prefix.
        """
        query = query.strip()

        if not query:
            return None, ""

        # Check for scope prefix
        if ":" in query:
            prefix, search_term = query.split(":", 1)
            prefix = prefix.strip().lower()

            if prefix in SCOPE_PREFIXES:
                return SCOPE_PREFIXES[prefix], search_term.strip()

        return None, query

    def _filter_items(self, query: str) -> None:
        """Filter and rank items by search query.

        Args:
            query: Search query string (may include scope prefix).
        """
        scope, search_term = self._parse_query(query)
        self._current_scope = scope

        # Filter by scope if specified
        items = self._all_items
        if scope:
            items = [item for item in items if item.scope == scope]

        # Get recents for each scope
        recents_by_scope: Dict[str, List[str]] = {}
        for s in SCOPE_PREFIXES.values():
            recents_by_scope[s] = self.recents_manager.get_recents(s)

        # Filter by search term with fuzzy matching
        filtered_items: List[PaletteItem] = []
        for item in items:
            matches, score = FuzzyMatcher.match(search_term, item.title)
            if matches:
                item.score = score

                # Boost score if recent
                if item.id in recents_by_scope.get(item.scope, []):
                    # More recent = higher boost
                    recent_index = recents_by_scope[item.scope].index(item.id)
                    boost = 500 - (recent_index * 50)  # 500 boost for most recent, decreasing
                    item.score += boost

                filtered_items.append(item)

        # Sort by score (highest first), then by title
        filtered_items.sort(key=lambda x: (-x.score, x.title))

        self._filtered_items = filtered_items

        # Rebuild list view with grouping
        self._rebuild_list_view(recents_by_scope)

    def _rebuild_list_view(self, recents_by_scope: Dict[str, List[str]]) -> None:
        """Rebuild list view with grouped sections.

        Args:
            recents_by_scope: Map of scope to recent item IDs.
        """
        list_view = self.query_one(ListView)
        list_view.clear()

        if not self._filtered_items:
            list_view.append(ListItem(Static("[dim]No results[/dim]")))
            return

        # Group by: Recents first (across all scopes), then by scope
        recents_section: List[PaletteItem] = []
        grouped_by_scope: Dict[str, List[PaletteItem]] = {
            "providers": [],
            "accounts": [],
            "models": [],
            "agents": [],
            "sessions": [],
        }

        for item in self._filtered_items:
            # Check if recent
            if item.id in recents_by_scope.get(item.scope, []):
                recents_section.append(item)
            else:
                grouped_by_scope[item.scope].append(item)

        # Add recents section if any
        if recents_section:
            # Section header
            header = Text()
            header.append("★ Recent", style="bold yellow")
            list_view.append(ListItem(Static(header)))
            list_view.append(ListItem(Static("─" * 40)))

            for item in recents_section:
                list_view.append(ListItem(Static(self._format_item(item, show_scope=True))))

            list_view.append(ListItem(Static("")))  # Spacer

        # Add scope sections
        scope_order = ["providers", "accounts", "models", "agents", "sessions"]
        scope_labels = {
            "providers": "📦 Providers",
            "accounts": "🔑 Accounts",
            "models": "🤖 Models",
            "agents": "👤 Agents",
            "sessions": "📝 Sessions",
        }

        for scope in scope_order:
            items = grouped_by_scope[scope]
            if items:
                # Section header
                header = Text()
                header.append(scope_labels[scope], style="bold cyan")
                list_view.append(ListItem(Static(header)))
                list_view.append(ListItem(Static("─" * 40)))

                for item in items:
                    list_view.append(ListItem(Static(self._format_item(item, show_scope=False))))

                list_view.append(ListItem(Static("")))  # Spacer

        # Set initial selection
        self._selected_index = 0
        if list_view.children:
            # Skip headers, find first selectable item
            for i, child in enumerate(list_view.children):
                if isinstance(child, ListItem) and "Recent" not in str(child):
                    list_view.index = i
                    break

    def _format_item(self, item: PaletteItem, show_scope: bool) -> str:
        """Format item for display.

        Args:
            item: PaletteItem to format.
            show_scope: Whether to show scope badge.

        Returns:
            Formatted string with rich markup.
        """
        parts = []

        # Title (bold)
        parts.append(f"[bold]{item.title}[/bold]")

        # Scope badge
        if show_scope:
            scope_prefix = PREFIX_FROM_SCOPE.get(item.scope, "?")
            parts.append(f" [{scope_prefix}:{item.scope}]")

        # Description (dimmed)
        if item.description:
            parts.append(f"\n[dim]{item.description}[/dim]")

        return "".join(parts)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for filtering.

        Args:
            event: Input.Changed event.
        """
        self._filter_items(event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection.

        Args:
            event: ListView.Selected event.
        """
        if self._filtered_items:
            self._selected_index = event.list_view.index
            self._execute_item()

    def _execute_item(self) -> None:
        """Execute selected item."""
        if not self._filtered_items or self._selected_index >= len(self._filtered_items):
            return

        # Find actual item (accounting for headers/spacers)
        list_view = self.query_one(ListView)
        if not list_view.children:
            return

        # Map list index to filtered item index (skip headers)
        actual_index = 0
        selected_item: Optional[PaletteItem] = None

        for i, child in enumerate(list_view.children):
            if i < self._selected_index:
                if isinstance(child, ListItem) and "Recent" not in str(child) and "─" not in str(child):
                    actual_index += 1
            elif i == self._selected_index:
                if isinstance(child, ListItem) and "Recent" not in str(child) and "─" not in str(child):
                    if actual_index < len(self._filtered_items):
                        selected_item = self._filtered_items[actual_index]
                break

        if not selected_item:
            return

        # Track as recent
        self.recents_manager.add_recent(selected_item.scope, selected_item.id)
        self.recents_manager.save()

        # Emit execute event
        self.post_message(
            EnhancedCommandExecute(
                scope=selected_item.scope,
                item_id=selected_item.id,
                data=selected_item.metadata
            )
        )

        # Call callback
        if self.on_execute:
            self.on_execute(selected_item.scope, selected_item.id)

        self.dismiss(f"{selected_item.scope}:{selected_item.id}")

    def action_enter(self) -> None:
        """Handle Enter key - execute selected action."""
        self._execute_item()

    def action_escape(self) -> None:
        """Handle Escape key - close without execution."""
        self.dismiss(None)

    def action_up(self) -> None:
        """Handle Up arrow - navigate up."""
        list_view = self.query_one(ListView)
        if list_view.index > 0:
            # Skip headers
            for i in range(list_view.index - 1, -1, -1):
                child = list_view.children[i]
                if isinstance(child, ListItem) and "Recent" not in str(child) and "─" not in str(child) and str(child).strip():
                    list_view.index = i
                    self._selected_index = i
                    break

    def action_down(self) -> None:
        """Handle Down arrow - navigate down."""
        list_view = self.query_one(ListView)
        if list_view.index < len(list_view.children) - 1:
            # Skip headers
            for i in range(list_view.index + 1, len(list_view.children)):
                child = list_view.children[i]
                if isinstance(child, ListItem) and "Recent" not in str(child) and "─" not in str(child) and str(child).strip():
                    list_view.index = i
                    self._selected_index = i
                    break
