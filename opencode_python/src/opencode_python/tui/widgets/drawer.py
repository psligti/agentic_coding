"""Drawer Widget for OpenCode TUI"""
from __future__ import annotations

from typing import Literal, Optional

from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Static


class TabButton(Button):
    """Tab button for drawer navigation

    Displays an icon and optional label for a drawer tab.
    Highlighted when active.
    """

    DEFAULT_CSS = """
    TabButton {
        width: 100%;
        height: 3;
        padding: 0 1;
        margin: 0 0 1 0;
        border: none;
        background: transparent;
        text-align: center;
    }

    TabButton:hover {
        background: $surface;
    }

    TabButton.-active {
        background: $primary;
        text-style: bold;
    }
    """

    def __init__(self, icon: str, label: Optional[str] = None, **kwargs):
        """Initialize TabButton

        Args:
            icon: Icon character to display
            label: Optional text label
            **kwargs: Additional Button widget arguments
        """
        content = f"{icon}"
        if label:
            content += f" {label}"
        super().__init__(content, **kwargs)


class TodoList(ScrollableContainer):
    """Todo list tab content

    Displays a list of todo items with completion status.
    Placeholder for now - will be connected to actual todo system.
    """

    DEFAULT_CSS = """
    TodoList {
        height: 1fr;
    }

    TodoList .todo-item {
        padding: 0 1;
        border-bottom: solid $primary;
    }

    TodoList .todo-completed {
        text-style: dim;
        color: $success;
    }
    """

    def compose(self):
        yield Static("[dim]No active todos[/dim]")


class SubagentList(ScrollableContainer):
    """Subagent list tab content

    Displays list of active subagent sessions with their status.
    Placeholder for now - will be connected to actual subagent system.
    """

    DEFAULT_CSS = """
    SubagentList {
        height: 1fr;
    }

    SubagentList .subagent-item {
        padding: 0 1;
        border-bottom: solid $primary;
    }

    SubagentList .status-running {
        color: $success;
    }

    SubagentList .status-pending {
        color: $warning;
    }
    """

    def compose(self):
        yield Static("[dim]No active subagents[/dim]")


class NavigatorTimeline(ScrollableContainer):
    """Navigator timeline tab content

    Displays a timeline of session events and navigation history.
    Placeholder for now - will be connected to actual timeline system.
    """

    DEFAULT_CSS = """
    NavigatorTimeline {
        height: 1fr;
    }

    NavigatorTimeline .timeline-item {
        padding: 0 1;
        border-bottom: solid $primary;
    }

    NavigatorTimeline .timestamp {
        color: $text-muted;
    }
    """

    def compose(self):
        yield Static("[dim]No timeline events[/dim]")


class DrawerWidget(Container):
    """Side drawer widget for accessing todos, subagents, and navigator

    Features:
    - 3 tabs: Todos (📋), Subagents (🤖), Navigator (🧭)
    - Slide animation when toggling visibility
    - Configurable width (30-45% of terminal)
    - Overlay mode - main content remains visible when open
    - Preserves tab state when hidden

    Default keyboard binding: Ctrl+D to toggle
    """

    visible: reactive[bool] = reactive(False)
    width_percent: reactive[int] = reactive(35)
    active_tab: reactive[Literal["todos", "subagents", "navigator"]] = reactive("todos")
    has_focus: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    DrawerWidget {
        dock: left;
        height: 100%;
        width: 35;
        offset-x: -35;
        transition: offset-x 150ms;
        background: $panel;
        border: thick $primary;
        display: block;
    }

    DrawerWidget.-visible {
        offset-x: 0;
    }

    DrawerWidget > Vertical {
        height: 100%;
    }

    DrawerWidget .drawer-header {
        padding: 1;
        background: $secondary;
        text-style: bold;
        text-align: center;
    }

    DrawerWidget .tab-buttons {
        height: 12;
        padding: 1;
        background: $surface;
    }

    DrawerWidget .tab-content {
        height: 1fr;
    }

    DrawerWidget ScrollableContainer {
        scrollbar-background: $surface;
        scrollbar-color: $primary;
    }
    """

    def __init__(
        self,
        width_percent: int = 35,
        **kwargs
    ) -> None:
        """Initialize DrawerWidget

        Args:
            width_percent: Width as percentage of terminal (30-45)
            **kwargs: Additional Container widget arguments
        """
        clamped_width = max(30, min(45, width_percent))
        self._width_percent = clamped_width
        super().__init__(**kwargs)
        self.width_percent = clamped_width

    def compose(self):
        """Build drawer UI"""
        with Vertical():
            yield Static("[bold]Drawer[/bold]", classes="drawer-header")

            with Horizontal(classes="tab-buttons"):
                self._btn_todos = TabButton("📋", "Todos", id="btn-todos")
                self._btn_subagents = TabButton("🤖", "Subagents", id="btn-subagents")
                self._btn_navigator = TabButton("🧭", "Navigator", id="btn-navigator")
                yield self._btn_todos
                yield self._btn_subagents
                yield self._btn_navigator

            with Container(classes="tab-content"):
                self._todo_list = TodoList(id="tab-todos")
                self._subagent_list = SubagentList(id="tab-subagents")
                self._navigator_timeline = NavigatorTimeline(id="tab-navigator")
                yield self._todo_list
                yield self._subagent_list
                yield self._navigator_timeline

    def on_mount(self) -> None:
        """Called when drawer is mounted"""
        self._update_active_tab()
        self._update_width()

    def _update_width(self) -> None:
        """Update drawer width based on width_percent"""
        if self.app is None:
            return

        terminal_width = self.app.size.width
        new_width = int(terminal_width * self._width_percent / 100)

        if not self.visible:
            self.styles.offset_x = (-1) * new_width

        self.styles.width = new_width

    def _update_active_tab(self) -> None:
        self._btn_todos.set_class(False, "-active")
        self._btn_subagents.set_class(False, "-active")
        self._btn_navigator.set_class(False, "-active")

        if self.active_tab == "todos":
            self._btn_todos.set_class(True, "-active")
        elif self.active_tab == "subagents":
            self._btn_subagents.set_class(True, "-active")
        elif self.active_tab == "navigator":
            self._btn_navigator.set_class(True, "-active")

        self._todo_list.display = (self.active_tab == "todos")
        self._subagent_list.display = (self.active_tab == "subagents")
        self._navigator_timeline.display = (self.active_tab == "navigator")

    def watch_visible(self, old_value: bool, new_value: bool) -> None:
        """Called when visibility changes"""
        if new_value:
            self.set_class(True, "-visible")
        else:
            self.set_class(False, "-visible")

    def watch_width_percent(self, old_value: int, new_value: int) -> None:
        """Called when width_percent changes"""
        clamped = max(30, min(45, new_value))
        self._width_percent = clamped
        if self.is_mounted:
            self._update_width()

    def watch_active_tab(self, old_value: str, new_value: str) -> None:
        if self.is_mounted:
            self._update_active_tab()

    def watch_has_focus(self, old_value: bool, new_value: bool) -> None:
        """Called when focus state changes"""
        if new_value:
            self.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab button presses"""
        button_id = event.button.id

        if button_id == "btn-todos":
            self.switch_tab("todos")
        elif button_id == "btn-subagents":
            self.switch_tab("subagents")
        elif button_id == "btn-navigator":
            self.switch_tab("navigator")

    def toggle_visible(self) -> None:
        """Toggle drawer visibility

        When toggling on, drawer slides in from left.
        When toggling off, drawer slides out to left.
        Tab state is preserved when hidden.
        """
        self.visible = not self.visible

    def switch_tab(self, tab_id: Literal["todos", "subagents", "navigator"]) -> None:
        """Switch to the specified tab

        Args:
            tab_id: Tab identifier ("todos", "subagents", or "navigator")

        Raises:
            ValueError: If tab_id is not a valid tab
        """
        valid_tabs = ["todos", "subagents", "navigator"]

        if tab_id not in valid_tabs:
            raise ValueError(f"Invalid tab_id: {tab_id}. Must be one of {valid_tabs}")

        self.active_tab = tab_id

    def set_width_percent(self, width_percent: int) -> None:
        """Set drawer width as percentage of terminal

        Args:
            width_percent: Width percentage (30-45)

        Raises:
            ValueError: If width_percent is not in range 30-45
        """
        if width_percent < 30 or width_percent > 45:
            raise ValueError(f"width_percent must be between 30 and 45, got {width_percent}")

        self.width_percent = width_percent
