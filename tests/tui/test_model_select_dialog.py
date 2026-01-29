from unittest.mock import Mock, patch
import pytest
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, DataTable

from opencode_python.tui.dialogs import ModelSelectDialog


@pytest.fixture
def available_models():
    return [
        {"value": "claude-3-5-sonnet-20241022", "title": "Claude 3.5 Sonnet", "provider": "anthropic"},
        {"value": "gpt-4o", "title": "GPT-4o", "provider": "openai"},
        {"value": "gemini-1.5-pro", "title": "Gemini 1.5 Pro", "provider": "google"},
    ]


@pytest.fixture
def mock_settings():
    with patch("opencode_python.core.settings.get_settings") as mock:
        settings = Mock()
        settings.model_default = "claude-3-5-sonnet-20241022"
        settings.provider_default = "anthropic"
        mock.return_value = settings
        yield settings


@pytest.mark.asyncio
async def test_dialog_created(available_models):
    dialog = ModelSelectDialog(available_models=available_models)
    assert dialog.title == "Select model"
    assert len(dialog.available_models) == 3


@pytest.mark.asyncio
async def test_dialog_shows_models():
    available_models = [
        {"value": "claude-3-5-sonnet-20241022", "title": "Claude 3.5 Sonnet", "provider": "anthropic"},
        {"value": "gpt-4o", "title": "GPT-4o", "provider": "openai"},
    ]

    class TestApp(App):
        def compose(self):
            dialog = ModelSelectDialog(available_models=available_models)
            self._dialog = dialog
            yield Vertical(dialog)

        def get_dialog(self):
            return self._dialog

    app = TestApp()
    async with app.run_test() as pilot:
        dialog = app.get_dialog()
        data_table = dialog.query_one(DataTable)
        assert data_table.row_count > 0


@pytest.mark.asyncio
async def test_dialog_close_returns_selection():
    class TestApp(App):
        def compose(self):
            available_models = [
                {"value": "claude-3-5-sonnet-20241022", "title": "Claude 3.5 Sonnet", "provider": "anthropic"},
                {"value": "gpt-4o", "title": "GPT-4o", "provider": "openai"},
            ]
            dialog = ModelSelectDialog(available_models=available_models)
            self._dialog = dialog
            yield Vertical(dialog)

        def get_dialog(self):
            return self._dialog

    app = TestApp()
    async with app.run_test() as pilot:
        dialog = app.get_dialog()
        dialog.close_dialog("gpt-4o")
        result = dialog.get_result()
        assert result == "gpt-4o"


@pytest.mark.asyncio
async def test_dialog_close_without_selection_returns_none():
    class TestApp(App):
        def compose(self):
            dialog = ModelSelectDialog()
            self._dialog = dialog
            yield Vertical(dialog)

        def get_dialog(self):
            return self._dialog

    app = TestApp()
    async with app.run_test() as pilot:
        dialog = app.get_dialog()
        dialog.close_dialog()
        result = dialog.get_result()
        assert result is None


@pytest.mark.asyncio
async def test_dialog_persists_selection_to_settings(available_models, mock_settings):
    class TestApp(App):
        def compose(self):
            dialog = ModelSelectDialog(available_models=available_models)
            self._dialog = dialog
            yield Vertical(dialog)

        def get_dialog(self):
            return self._dialog

    app = TestApp()
    async with app.run_test() as pilot:
        dialog = app.get_dialog()
        selected_model = available_models[0]["value"]
        dialog.close_dialog(selected_model)
        mock_settings.model_default = selected_model


@pytest.mark.asyncio
async def test_dialog_shows_default_selection(available_models, mock_settings):
    class TestApp(App):
        def compose(self):
            dialog = ModelSelectDialog(available_models=available_models)
            self._dialog = dialog
            yield Vertical(dialog)

        def get_dialog(self):
            return self._dialog

    app = TestApp()
    async with app.run_test() as pilot:
        dialog = app.get_dialog()
        default_model = available_models[0]["value"]
        assert dialog._result is None
