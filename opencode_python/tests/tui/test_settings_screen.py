"""Test settings screen."""

from opencode_python.tui.screens.settings_screen import SettingsScreen
from opencode_python.agents.builtin import get_all_agents


def test_settings_screen_has_title():
    """Test that settings screen has title."""
    screen = SettingsScreen()
    assert screen.title == "Settings"


def test_settings_screen_has_themes():
    """Test that settings screen has all expected themes."""
    screen = SettingsScreen()

    # Check that all themes are present
    themes = screen.themes
    assert len(themes) == 8
    assert {"value": "light", "title": "Light"} in themes
    assert {"value": "dark", "title": "Dark"} in themes
    assert {"value": "dracula", "title": "Dracula"} in themes
    assert {"value": "gruvbox", "title": "Gruvbox"} in themes
    assert {"value": "catppuccin", "title": "Catppuccin"} in themes
    assert {"value": "nord", "title": "Nord"} in themes
    assert {"value": "tokyonight", "title": "Tokyo Night"} in themes
    assert {"value": "onedarkpro", "title": "One Dark Pro"} in themes


def test_settings_screen_has_agents():
    """Test that settings screen has all expected agents."""
    agents = get_all_agents()
    assert len(agents) == 4

    agent_names = [agent.name for agent in agents]
    assert "build" in agent_names
    assert "plan" in agent_names
    assert "general" in agent_names
    assert "explore" in agent_names


def test_settings_screen_select_theme():
    """Test that theme selection works."""
    screen = SettingsScreen()

    # Select a theme
    screen.select_theme("gruvbox")

    # Check that theme is selected
    assert screen._selected_theme == "gruvbox"


def test_settings_screen_select_agent():
    """Test that agent selection works."""
    screen = SettingsScreen()

    # Select an agent
    screen.select_agent("explore")

    # Check that agent is selected
    assert screen._selected_agent == "explore"


def test_settings_screen_select_model():
    """Test that model selection works (placeholder)."""
    screen = SettingsScreen()

    # Create a mock model
    class MockModel:
        def __init__(self, model_id):
            self.id = model_id

    mock_model = MockModel("claude-3-5-sonnet-20241022")

    # Select a model
    screen.select_model(mock_model)

    # Check that model is selected
    assert screen._selected_model == mock_model
    assert screen._selected_model.id == "claude-3-5-sonnet-20241022"


def test_settings_screen_has_callbacks():
    """Test that settings screen has proper callbacks."""
    screen = SettingsScreen()

    # Check for required callbacks
    assert hasattr(screen, 'on_save')
    assert hasattr(screen, 'on_cancel')


def test_settings_screen_has_actions():
    """Test that settings screen has proper actions."""
    screen = SettingsScreen()

    # Check for required actions
    assert hasattr(screen, 'action_save')
    assert hasattr(screen, 'action_cancel')
    assert hasattr(screen, 'action_enter')
    assert hasattr(screen, 'action_escape')


def test_settings_screen_get_result_initially_none():
    """Test that get_result returns None initially."""
    screen = SettingsScreen()
    result = screen.get_result()
    assert result is None


def test_settings_screen_has_settings_attribute():
    """Test that settings screen has settings attribute."""
    screen = SettingsScreen()
    assert hasattr(screen, '_settings')


def test_settings_screen_select_theme_preserves_other_selections():
    """Test that selecting a theme doesn't affect other selections."""
    screen = SettingsScreen()

    # Set all selections
    screen._selected_theme = "light"
    screen._selected_model = None
    screen._selected_agent = "general"

    # Select a theme
    screen.select_theme("dark")

    # Check that only theme changed
    assert screen._selected_theme == "dark"
    assert screen._selected_model is None
    assert screen._selected_agent == "general"


def test_settings_screen_select_agent_preserves_other_selections():
    """Test that selecting an agent doesn't affect other selections."""
    screen = SettingsScreen()

    # Set all selections
    screen._selected_theme = "light"
    screen._selected_model = None
    screen._selected_agent = "general"

    # Select an agent
    screen.select_agent("plan")

    # Check that only agent changed
    assert screen._selected_theme == "light"
    assert screen._selected_model is None
    assert screen._selected_agent == "plan"


def test_settings_screen_select_model_preserves_other_selections():
    """Test that selecting a model doesn't affect other selections."""
    screen = SettingsScreen()

    # Set all selections
    screen._selected_theme = "light"
    screen._selected_model = None
    screen._selected_agent = "general"

    # Create a mock model
    class MockModel:
        def __init__(self, model_id):
            self.id = model_id

    mock_model = MockModel("claude-3-5-sonnet-20241022")

    # Select a model
    screen.select_model(mock_model)

    # Check that only model changed
    assert screen._selected_theme == "light"
    assert screen._selected_model == mock_model
    assert screen._selected_agent == "general"
