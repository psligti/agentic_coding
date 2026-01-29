"""Tests for Header widget using TDD approach."""

import pytest
from textual.widgets import Static
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal

from opencode_python.tui.widgets.header import HeaderWidget


class TestHeaderWidget:
    """Test HeaderWidget functionality."""

    def test_header_widget_initialization(self):
        """HeaderWidget should initialize with required attributes."""
        header = HeaderWidget()
        assert header.model_id == ""
        assert header.session_title == ""
        assert header.parent_session_path == ""

    def test_header_widget_with_model_and_title(self):
        """HeaderWidget should display session title and model."""
        header = HeaderWidget(
            model_id="gpt-4",
            session_title="Test Session",
            parent_session_path=""
        )
        assert header.model_id == "gpt-4"
        assert header.session_title == "Test Session"
        assert header.parent_session_path == ""

    def test_header_widget_with_parent_session(self):
        """HeaderWidget should display parent session breadcrumbs."""
        header = HeaderWidget(
            model_id="claude-3",
            session_title="Subagent Session",
            parent_session_path="Main Session"
        )
        assert header.parent_session_path == "Main Session"

    def test_header_widget_render_without_session(self):
        """HeaderWidget should render placeholder when no session selected."""
        header = HeaderWidget()
        rendered = header.render()
        assert "No active session" in rendered

    def test_header_widget_render_with_session_title(self):
        """HeaderWidget should render session title when selected."""
        header = HeaderWidget(
            model_id="gpt-4",
            session_title="Development Task",
            parent_session_path=""
        )
        rendered = header.render()
        assert "Development Task" in rendered

    def test_header_widget_render_with_model(self):
        """HeaderWidget should render model information."""
        header = HeaderWidget(
            model_id="gpt-4",
            session_title="Test Session",
            parent_session_path=""
        )
        rendered = header.render()
        assert "gpt-4" in rendered

    def test_header_widget_render_with_parent_breadcrumb(self):
        """HeaderWidget should render parent session breadcrumb."""
        header = HeaderWidget(
            model_id="claude-3",
            session_title="Subagent Task",
            parent_session_path="Parent Session"
        )
        rendered = header.render()
        assert "Parent Session" in rendered
        assert "Subagent Task" in rendered

    def test_header_widget_with_complex_parent_path(self):
        """HeaderWidget should handle complex parent session paths."""
        header = HeaderWidget(
            model_id="gpt-4-turbo",
            session_title="Nested Task",
            parent_session_path="Main / Planning / Implementation"
        )
        rendered = header.render()
        assert "Main" in rendered
        assert "Planning" in rendered
        assert "Implementation" in rendered
        assert "Nested Task" in rendered

    def test_header_widget_version_display(self):
        """HeaderWidget should display version information."""
        header = HeaderWidget(
            model_id="gpt-4",
            session_title="Test Session",
            parent_session_path=""
        )
        rendered = header.render()
        assert "v" in rendered.lower()

    def test_header_widget_css_applied(self):
        """HeaderWidget should have appropriate CSS styling."""
        header = HeaderWidget()
        css = header.css
        assert "background" in css.lower() or "bg" in css.lower()
        assert "text" in css.lower() or "color" in css.lower()


class TestHeaderIntegration:
    """Test HeaderWidget integration with Textual app."""

    class TestApp(App[None]):
        """Test application for Header integration."""

        def compose(self) -> ComposeResult:
            header = HeaderWidget(
                model_id="gpt-4",
                session_title="Integration Test Session",
                parent_session_path="Parent Session"
            )
            yield Vertical(
                header,
                Static("Test content below header")
            )

    async def test_header_in_container(self):
        """HeaderWidget should be mountable in Textual containers."""
        app = self.TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(HeaderWidget)
            assert header is not None
            assert header.model_id == "gpt-4"
            assert header.session_title == "Integration Test Session"
            assert header.parent_session_path == "Parent Session"

    async def test_header_rendered_text(self):
        """HeaderWidget rendered text should be accessible."""
        app = self.TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(HeaderWidget)
            rendered = header.plain
            assert "Integration Test Session" in rendered
            assert "gpt-4" in rendered
            assert "Parent Session" in rendered

    async def test_header_updates_when_attributes_change(self):
        """HeaderWidget should update when attributes are modified."""
        app = self.TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(HeaderWidget)

            header.model_id = "claude-3.5"
            assert header.model_id == "claude-3.5"

            header.session_title = "Updated Session"
            assert header.session_title == "Updated Session"

            header.parent_session_path = "New Parent"
            assert header.parent_session_path == "New Parent"


class TestHeaderEdgeCases:
    """Test HeaderWidget edge cases and error handling."""

    def test_header_with_empty_strings(self):
        """HeaderWidget should handle empty string attributes."""
        header = HeaderWidget(
            model_id="",
            session_title="",
            parent_session_path=""
        )
        rendered = header.render()
        assert "No active session" in rendered

    def test_header_with_only_model_id(self):
        """HeaderWidget should handle case with only model_id."""
        header = HeaderWidget(
            model_id="gpt-4",
            session_title="",
            parent_session_path=""
        )
        rendered = header.render()
        assert "gpt-4" in rendered

    def test_header_with_only_parent_path(self):
        """HeaderWidget should handle case with only parent path."""
        header = HeaderWidget(
            model_id="",
            session_title="",
            parent_session_path="Complex / Path / Here"
        )
        rendered = header.render()
        assert "Complex" in rendered
        assert "Path" in rendered
        assert "Here" in rendered

    def test_header_with_special_characters(self):
        """HeaderWidget should handle special characters in titles."""
        header = HeaderWidget(
            model_id="gpt-4",
            session_title="Test: Session #1 & Updates",
            parent_session_path="Parent / Special: chars"
        )
        rendered = header.render()
        assert "Test: Session #1 & Updates" in rendered
        assert "Special: chars" in rendered
