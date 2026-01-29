from typing import Any, Dict, List, Optional, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListView, ListItem


class ThemeSelectDialog(ModalScreen[str]):
    def __init__(
        self,
        title: str = "Select theme",
        available_themes: Optional[List[Dict[str, Any]]] = None,
        on_select: Optional[Callable[[str], None]] = None
    ):
        super().__init__()
        self.title = title
        self.available_themes = available_themes or []
        self.on_select = on_select
        self._result: Optional[str] = None
        self._selected_theme: Optional[str] = None

    def compose(self) -> ComposeResult:
        container = Vertical()

        if self.title:
            yield Label(self.title)

        list_view = ListView(id="theme_list")
        yield list_view

        for theme in self.available_themes:
            theme_name = theme.get("name", str(theme.get("value", "")))
            yield ListItem(Label(theme_name, id=f"theme_{theme['value']}"))

        yield container

    async def on_mount(self) -> None:
        list_view = self.query_one(ListView)
        list_view.focus()

    def close_dialog(self, value: Optional[str] = None) -> None:
        self._result = value
        self._selected_theme = value
        self.dismiss()

    def get_result(self) -> Optional[str]:
        return self._result

    def action_enter(self) -> None:
        list_view = self.query_one(ListView)
        if list_view.cursor_row is not None:
            theme_value = list_view.cursor_row.id.replace("theme_", "")
            self.close_dialog(theme_value)
            if self.on_select:
                self.on_select(theme_value)
        else:
            self.close_dialog(None)

    def action_escape(self) -> None:
        self.close_dialog(None)

    def action_cancel(self) -> None:
        self.action_escape()

    def action_select(self) -> None:
        self.action_enter()
