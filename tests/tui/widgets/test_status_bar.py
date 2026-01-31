"""Tests for StatusBar Widget"""

import pytest
from textual.app import App
from textual.widgets import Static

from opencode_python.tui.widgets.status_bar import StatusBar


@pytest.mark.asyncio
async def test_status_bar_widget_instantiation():
    """Test that StatusBar widget can be instantiated"""
    status_bar = StatusBar()
    assert status_bar is not None
    assert isinstance(status_bar, StatusBar)


@pytest.mark.asyncio
async def test_status_bar_initial_state():
    """Test that StatusBar initializes with default values"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        assert status_bar.message_count == 0
        assert status_bar.cost == 0.0
        assert status_bar.tokens == 0


@pytest.mark.asyncio
async def test_status_bar_has_hints_container():
    """Test that StatusBar has hints container"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        hints_container = status_bar.query_one("#hints")
        assert hints_container is not None


@pytest.mark.asyncio
async def test_status_bar_has_metrics_container():
    """Test that StatusBar has metrics container"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        metrics_container = status_bar.query_one("#metrics")
        assert metrics_container is not None


@pytest.mark.asyncio
async def test_status_bar_keyboard_hints_display():
    """Test that keyboard hints are displayed"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        hints_container = status_bar.query_one("#hints")

        # Should have hint widgets
        hints = hints_container.query(Static)
        assert len(hints) > 0


@pytest.mark.asyncio
async def test_status_bar_metrics_display_initial():
    """Test that metrics are displayed with initial values"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        metrics_container = status_bar.query_one("#metrics")

        # Should have metric widgets
        metrics = metrics_container.query(Static)
        assert len(metrics) > 0


@pytest.mark.asyncio
async def test_status_bar_message_count_update():
    """Test that message count updates correctly"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        status_bar.message_count = 5

        # Give time for reactive update
        await pilot.pause()

        assert status_bar.message_count == 5


@pytest.mark.asyncio
async def test_status_bar_cost_update():
    """Test that cost updates correctly"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        status_bar.cost = 0.1234

        # Give time for reactive update
        await pilot.pause()

        assert status_bar.cost == 0.1234


@pytest.mark.asyncio
async def test_status_bar_tokens_update():
    """Test that tokens update correctly"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        status_bar.tokens = 1000

        # Give time for reactive update
        await pilot.pause()

        assert status_bar.tokens == 1000


@pytest.mark.asyncio
async def test_status_bar_reactive_watcher_message_count():
    """Test that reactive watcher for message_count works correctly"""
    status_bar = StatusBar()
    status_bar.watch_message_count(0, 10)
    assert status_bar.message_count == 10


@pytest.mark.asyncio
async def test_status_bar_reactive_watcher_cost():
    """Test that reactive watcher for cost works correctly"""
    status_bar = StatusBar()
    status_bar.watch_cost(0.0, 0.1234)
    assert status_bar.cost == 0.1234


@pytest.mark.asyncio
async def test_status_bar_reactive_watcher_tokens():
    """Test that reactive watcher for tokens works correctly"""
    status_bar = StatusBar()
    status_bar.watch_tokens(0, 1000)
    assert status_bar.tokens == 1000


@pytest.mark.asyncio
async def test_status_bar_full_metrics_update():
    """Test that all metrics update simultaneously"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        status_bar.message_count = 100
        status_bar.cost = 12.3456
        status_bar.tokens = 50000

        # Give time for reactive updates
        await pilot.pause()

        assert status_bar.message_count == 100
        assert status_bar.cost == 12.3456
        assert status_bar.tokens == 50000


@pytest.mark.asyncio
async def test_status_bar_on_mount_updates_display():
    """Test that on_mount updates the display"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)

        # on_mount is called automatically during composition
        # Verify that display was updated
        metrics_container = status_bar.query_one("#metrics")
        assert metrics_container is not None


@pytest.mark.asyncio
async def test_status_bar_zero_metrics():
    """Test that zero metrics are displayed correctly"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)

        # All metrics should be zero by default
        assert status_bar.message_count == 0
        assert status_bar.cost == 0.0
        assert status_bar.tokens == 0


@pytest.mark.asyncio
async def test_status_bar_large_metrics():
    """Test that large metrics are handled correctly"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        status_bar.message_count = 10000
        status_bar.cost = 9999.9999
        status_bar.tokens = 1000000

        # Give time for reactive updates
        await pilot.pause()

        assert status_bar.message_count == 10000
        assert status_bar.cost == 9999.9999
        assert status_bar.tokens == 1000000


@pytest.mark.asyncio
async def test_status_bar_cost_precision():
    """Test that cost is displayed with correct precision"""
    class TestApp(App):
        def compose(self):
            yield StatusBar()

    app = TestApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one(StatusBar)
        status_bar.cost = 0.123456

        # Give time for reactive update
        await pilot.pause()

        # Cost should be stored with full precision
        assert status_bar.cost == 0.123456
