import pytest
from typing import List, Dict, Any

from textual.app import App
from textual.containers import Vertical
from textual.widgets import Label

from opencode_python.tui.dialogs import ThemeSelectDialog


@pytest.fixture
def available_themes():
    return [
        {"value": "light", "name": "Light"},
        {"value": "dark", "name": "Dark"},
        {"value": "dracula", "name": "Dracula"},
    ]


@pytest.mark.asyncio
async def test_dialog_created(available_themes):
    dialog = ThemeSelectDialog(available_themes=available_themes)
    assert dialog.title == "Select theme"
    assert len(dialog.available_themes) == 3


@pytest.mark.asyncio
async def test_dialog_shows_themes(available_themes):
    dialog = ThemeSelectDialog(available_themes=available_themes)

    class TestApp(App):
        def compose(self):
            yield Vertical(dialog)

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        labels = [widget for widget in dialog.query(Label)]
        assert len(labels) > 0


@pytest.mark.asyncio
async def test_dialog_close_returns_selection(available_themes):
    app = App()
    dialog = ThemeSelectDialog(available_themes=available_themes)
    async with app.run_test() as pilot:
        app.push_screen(dialog)
        await pilot.pause()

        dialog.close_dialog("dark")
        result = dialog.get_result()
        assert result == "dark"


@pytest.mark.asyncio
async def test_dialog_close_without_selection_returns_none(available_themes):
    app = App()
    dialog = ThemeSelectDialog(available_themes=available_themes)
    async with app.run_test() as pilot:
        dialog.close_dialog()
        result = dialog.get_result()
        assert result is None
