"""Drawer widget tests"""
import pytest
from textual.app import App, ComposeResult

try:
    from opencode_python.tui.widgets.drawer import (
        DrawerWidget,
        TabButton,
        TodoList,
        SubagentList,
        NavigatorTimeline,
    )
    from opencode_python.core.models import DrawerModel
    DRAWER_EXISTS = True
except ImportError:
    DRAWER_EXISTS = False
    DrawerWidget = None
    TabButton = None
    TodoList = None
    SubagentList = None
    NavigatorTimeline = None
    DrawerModel = None


class TestDrawerModel:
    """DrawerModel tests"""

    def test_model_exists(self):
        """DrawerModel should be importable"""
        assert DRAWER_EXISTS, "DrawerModel not found"
        assert DrawerModel is not None, "DrawerModel class not found"

    def test_model_has_visible_property(self):
        """DrawerModel should have visible property"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerModel not yet implemented")

        model = DrawerModel()
        assert model.visible is False

    def test_model_has_width_percent_property(self):
        """DrawerModel should have width_percent property with default"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerModel not yet implemented")

        model = DrawerModel()
        assert model.width_percent == 35

    def test_model_width_percent_validation(self):
        """DrawerModel should validate width_percent is between 30-45"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerModel not yet implemented")

        model = DrawerModel(width_percent=30)
        assert model.width_percent == 30

        model = DrawerModel(width_percent=45)
        assert model.width_percent == 45

    def test_model_has_active_tab_property(self):
        """DrawerModel should have active_tab property with default"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerModel not yet implemented")

        model = DrawerModel()
        assert model.active_tab == "todos"

    def test_model_has_has_focus_property(self):
        """DrawerModel should have has_focus property with default"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerModel not yet implemented")

        model = DrawerModel()
        assert model.has_focus is False

    def test_model_visible_can_be_true(self):
        """DrawerModel visible can be set to True"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerModel not yet implemented")

        model = DrawerModel(visible=True)
        assert model.visible is True


class TestDrawerWidget:
    """DrawerWidget tests"""

    def test_widget_exists(self):
        """DrawerWidget should be importable"""
        assert DRAWER_EXISTS, "DrawerWidget not found"
        assert DrawerWidget is not None, "DrawerWidget class not found"

    def test_widget_is_container(self):
        """DrawerWidget should be a Textual Container"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        from textual.containers import Container
        assert issubclass(DrawerWidget, Container)

    def test_widget_has_visible_property(self):
        """DrawerWidget should have visible reactive property"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        widget = DrawerWidget()
        assert widget.visible is False

    def test_widget_has_width_percent_property(self):
        """DrawerWidget should have width_percent reactive property"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        widget = DrawerWidget(width_percent=40)
        assert widget.width_percent == 40

    def test_widget_has_active_tab_property(self):
        """DrawerWidget should have active_tab reactive property"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        widget = DrawerWidget()
        assert widget.active_tab == "todos"

    @pytest.mark.asyncio
    async def test_widget_has_three_tabs(self):
        """DrawerWidget should have three tab buttons"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            tabs = drawer.query(TabButton)
            assert len(tabs) == 3

    @pytest.mark.asyncio
    async def test_widget_tabs_have_icons(self):
        """DrawerWidget tabs should have emoji icons"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            tabs = drawer.query(TabButton)

            tab_labels = [tab.label for tab in tabs]
            assert "📋" in str(tab_labels)
            assert "🤖" in str(tab_labels)
            assert "🧭" in str(tab_labels)

    @pytest.mark.asyncio
    async def test_widget_has_todo_list(self):
        """DrawerWidget should have TodoList component"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            todo_list = drawer.query_one("#tab-todos", TodoList)
            assert todo_list is not None

    @pytest.mark.asyncio
    async def test_widget_has_subagent_list(self):
        """DrawerWidget should have SubagentList component"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            subagent_list = drawer.query_one("#tab-subagents", SubagentList)
            assert subagent_list is not None

    @pytest.mark.asyncio
    async def test_widget_has_navigator_timeline(self):
        """DrawerWidget should have NavigatorTimeline component"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            navigator = drawer.query_one("#tab-navigator", NavigatorTimeline)
            assert navigator is not None

    @pytest.mark.asyncio
    async def test_toggle_visible_method(self):
        """DrawerWidget toggle_visible should change visibility state"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            assert drawer.visible is False

            drawer.toggle_visible()
            await pilot.pause()
            assert drawer.visible is True

            drawer.toggle_visible()
            await pilot.pause()
            assert drawer.visible is False

    @pytest.mark.asyncio
    async def test_switch_tab_method(self):
        """DrawerWidget switch_tab should change active tab"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            assert drawer.active_tab == "todos"

            drawer.switch_tab("subagents")
            await pilot.pause()
            assert drawer.active_tab == "subagents"

            drawer.switch_tab("navigator")
            await pilot.pause()
            assert drawer.active_tab == "navigator"

            drawer.switch_tab("todos")
            await pilot.pause()
            assert drawer.active_tab == "todos"

    @pytest.mark.asyncio
    async def test_switch_tab_invalid_raises_error(self):
        """DrawerWidget switch_tab with invalid tab_id should raise ValueError"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            with pytest.raises(ValueError) as exc_info:
                drawer.switch_tab("invalid")

            assert "Invalid tab_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_visible_class_toggled(self):
        """DrawerWidget should have -visible class when visible"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            assert not drawer.has_class("-visible")

            drawer.visible = True
            await pilot.pause()
            assert drawer.has_class("-visible")

            drawer.visible = False
            await pilot.pause()
            assert not drawer.has_class("-visible")

    @pytest.mark.asyncio
    async def test_active_tab_button_highlights(self):
        """Active tab button should have -active class"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            btn_todos = drawer.query_one("#btn-todos", TabButton)
            btn_subagents = drawer.query_one("#btn-subagents", TabButton)
            btn_navigator = drawer.query_one("#btn-navigator", TabButton)

            assert btn_todos.has_class("-active")
            assert not btn_subagents.has_class("-active")
            assert not btn_navigator.has_class("-active")

            drawer.switch_tab("subagents")
            await pilot.pause()

            assert not btn_todos.has_class("-active")
            assert btn_subagents.has_class("-active")
            assert not btn_navigator.has_class("-active")

            drawer.switch_tab("navigator")
            await pilot.pause()

            assert not btn_todos.has_class("-active")
            assert not btn_subagents.has_class("-active")
            assert btn_navigator.has_class("-active")

    @pytest.mark.asyncio
    async def test_only_active_tab_content_visible(self):
        """Only active tab content should be visible"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            todo_list = drawer.query_one("#tab-todos", TodoList)
            subagent_list = drawer.query_one("#tab-subagents", SubagentList)
            navigator = drawer.query_one("#tab-navigator", NavigatorTimeline)

            assert todo_list.display is True
            assert subagent_list.display is False
            assert navigator.display is False

            drawer.switch_tab("subagents")
            await pilot.pause()

            assert todo_list.display is False
            assert subagent_list.display is True
            assert navigator.display is False

    @pytest.mark.asyncio
    async def test_width_percent_range_validation(self):
        """set_width_percent should validate range 30-45"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer

            drawer.set_width_percent(30)
            assert drawer.width_percent == 30

            drawer.set_width_percent(45)
            assert drawer.width_percent == 45

            with pytest.raises(ValueError):
                drawer.set_width_percent(29)

            with pytest.raises(ValueError):
                drawer.set_width_percent(46)

    @pytest.mark.asyncio
    async def test_button_click_switches_tab(self):
        """Clicking a tab button should switch to that tab"""
        if not DRAWER_EXISTS:
            pytest.skip("DrawerWidget not yet implemented")

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._drawer = DrawerWidget()
                yield self._drawer

        app = TestApp()
        async with app.run_test() as pilot:
            drawer = app._drawer
            btn_subagents = drawer.query_one("#btn-subagents", TabButton)

            assert drawer.active_tab == "todos"

            btn_subagents.press()
            await pilot.pause()

            assert drawer.active_tab == "subagents"


class TestTabButton:
    """TabButton tests"""

    def test_tab_button_exists(self):
        """TabButton should be importable"""
        assert DRAWER_EXISTS, "TabButton not found"
        assert TabButton is not None, "TabButton class not found"

    def test_tab_button_is_button(self):
        """TabButton should extend Textual Button"""
        if not DRAWER_EXISTS:
            pytest.skip("TabButton not yet implemented")

        from textual.widgets import Button
        assert issubclass(TabButton, Button)

    def test_tab_button_displays_icon(self):
        """TabButton should display icon character"""
        if not DRAWER_EXISTS:
            pytest.skip("TabButton not yet implemented")

        button = TabButton(icon="📋")
        assert "📋" in str(button.label)

    def test_tab_button_displays_label(self):
        """TabButton should display optional label"""
        if not DRAWER_EXISTS:
            pytest.skip("TabButton not yet implemented")

        button = TabButton(icon="📋", label="Todos")
        assert "Todos" in str(button.label)


class TestTodoList:
    """TodoList tests"""

    def test_todo_list_exists(self):
        """TodoList should be importable"""
        assert DRAWER_EXISTS, "TodoList not found"
        assert TodoList is not None, "TodoList class not found"

    def test_todo_list_is_scrollable_container(self):
        """TodoList should extend ScrollableContainer"""
        if not DRAWER_EXISTS:
            pytest.skip("TodoList not yet implemented")

        from textual.containers import ScrollableContainer
        assert issubclass(TodoList, ScrollableContainer)


class TestSubagentList:
    """SubagentList tests"""

    def test_subagent_list_exists(self):
        """SubagentList should be importable"""
        assert DRAWER_EXISTS, "SubagentList not found"
        assert SubagentList is not None, "SubagentList class not found"

    def test_subagent_list_is_scrollable_container(self):
        """SubagentList should extend ScrollableContainer"""
        if not DRAWER_EXISTS:
            pytest.skip("SubagentList not yet implemented")

        from textual.containers import ScrollableContainer
        assert issubclass(SubagentList, ScrollableContainer)


class TestNavigatorTimeline:
    """NavigatorTimeline tests"""

    def test_navigator_timeline_exists(self):
        """NavigatorTimeline should be importable"""
        assert DRAWER_EXISTS, "NavigatorTimeline not found"
        assert NavigatorTimeline is not None, "NavigatorTimeline class not found"

    def test_navigator_timeline_is_scrollable_container(self):
        """NavigatorTimeline should extend ScrollableContainer"""
        if not DRAWER_EXISTS:
            pytest.skip("NavigatorTimeline not yet implemented")

        from textual.containers import ScrollableContainer
        assert issubclass(NavigatorTimeline, ScrollableContainer)
