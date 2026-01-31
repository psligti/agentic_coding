"""Tests for EnhancedCommandPalette"""

import pytest
from pathlib import Path
from textual.app import App
from textual.widgets import Input, ListView, Static

from opencode_python.tui.palette.enhanced_command_palette import (
    EnhancedCommandPalette,
    FuzzyMatcher,
    PaletteItem,
    SCOPE_PREFIXES,
    PREFIX_FROM_SCOPE,
)


@pytest.mark.asyncio
async def test_enhanced_command_palette_instantiation():
    """Test that EnhancedCommandPalette can be instantiated"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    assert palette is not None
    assert isinstance(palette, EnhancedCommandPalette)


@pytest.mark.asyncio
async def test_enhanced_command_palette_compose():
    """Test that palette composes correctly"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)
        assert palette is not None


@pytest.mark.asyncio
async def test_enhanced_command_palette_has_search_input():
    """Test that palette has search input"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)
        search_input = palette.query_one("#palette_search", Input)
        assert search_input is not None


@pytest.mark.asyncio
async def test_enhanced_command_palette_has_list_view():
    """Test that palette has list view"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)
        list_view = palette.query_one("#palette_list", ListView)
        assert list_view is not None


@pytest.mark.asyncio
async def test_fuzzy_matcher_exact_match():
    """Test that fuzzy matcher finds exact matches"""
    matches, score = FuzzyMatcher.match("gpt-4", "gpt-4")
    assert matches is True
    assert score == 1000


@pytest.mark.asyncio
async def test_fuzzy_matcher_starts_with():
    """Test that fuzzy matcher finds prefix matches"""
    matches, score = FuzzyMatcher.match("gpt", "gpt-4")
    assert matches is True
    assert score == 800


@pytest.mark.asyncio
async def test_fuzzy_matcher_contains():
    """Test that fuzzy matcher finds substring matches"""
    matches, score = FuzzyMatcher.match("4", "gpt-4")
    assert matches is True
    assert score == 600


@pytest.mark.asyncio
async def test_fuzzy_matcher_fuzzy():
    """Test that fuzzy matcher finds character sequence matches"""
    matches, score = FuzzyMatcher.match("g4", "gpt-4")
    assert matches is True
    assert score == 400


@pytest.mark.asyncio
async def test_fuzzy_matcher_no_match():
    """Test that fuzzy matcher returns false for no match"""
    matches, score = FuzzyMatcher.match("xyz", "gpt-4")
    assert matches is False
    assert score == 0


@pytest.mark.asyncio
async def test_fuzzy_matcher_empty_query():
    """Test that fuzzy matcher returns true for empty query"""
    matches, score = FuzzyMatcher.match("", "gpt-4")
    assert matches is True
    assert score == 0


@pytest.mark.asyncio
async def test_scope_prefixes():
    """Test that scope prefixes are defined"""
    assert "p" in SCOPE_PREFIXES
    assert "a" in SCOPE_PREFIXES
    assert "m" in SCOPE_PREFIXES
    assert "g" in SCOPE_PREFIXES
    assert "s" in SCOPE_PREFIXES

    assert SCOPE_PREFIXES["p"] == "providers"
    assert SCOPE_PREFIXES["a"] == "accounts"
    assert SCOPE_PREFIXES["m"] == "models"
    assert SCOPE_PREFIXES["g"] == "agents"
    assert SCOPE_PREFIXES["s"] == "sessions"


@pytest.mark.asyncio
async def test_prefix_from_scope():
    """Test that reverse scope mapping works"""
    assert PREFIX_FROM_SCOPE["providers"] == "p"
    assert PREFIX_FROM_SCOPE["accounts"] == "a"
    assert PREFIX_FROM_SCOPE["models"] == "m"
    assert PREFIX_FROM_SCOPE["agents"] == "g"
    assert PREFIX_FROM_SCOPE["sessions"] == "s"


@pytest.mark.asyncio
async def test_parse_query_no_prefix():
    """Test that query parser handles no prefix"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    scope, search_term = palette._parse_query("gpt-4")

    assert scope is None
    assert search_term == "gpt-4"


@pytest.mark.asyncio
async def test_parse_query_with_prefix():
    """Test that query parser extracts scope prefix"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    scope, search_term = palette._parse_query("p:openai")

    assert scope == "providers"
    assert search_term == "openai"


@pytest.mark.asyncio
async def test_parse_query_with_invalid_prefix():
    """Test that query parser handles invalid prefix"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    scope, search_term = palette._parse_query("x:test")

    assert scope is None
    assert search_term == "x:test"


@pytest.mark.asyncio
async def test_parse_query_with_whitespace():
    """Test that query parser handles whitespace"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    scope, search_term = palette._parse_query("  p:  gpt-4  ")

    assert scope == "providers"
    assert search_term == "gpt-4"


@pytest.mark.asyncio
async def test_build_all_items():
    """Test that all items are built from data sources"""
    from opencode_python.providers_mgmt.models import Provider, Account
    from opencode_python.providers.base import ModelInfo

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]
    accounts = [Account(id="default", name="Default", provider_id="openai", description="Default account")]
    models = [ModelInfo(id="gpt-4", name="GPT-4", provider_id="openai", family="gpt", api_id="gpt-4")]

    palette = EnhancedCommandPalette(
        storage_path=storage_path,
        providers=providers,
        accounts=accounts,
        models=models,
    )

    items = palette._all_items
    assert len(items) == 3  # 1 provider + 1 account + 1 model


@pytest.mark.asyncio
async def test_filter_items_no_scope():
    """Test that filter works without scope restriction"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [
        Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com"),
        Provider(id="anthropic", name="Anthropic", description="AI provider", base_url="https://api.anthropic.com"),
    ]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    palette._filter_items("openai")

    assert len(palette._filtered_items) > 0


@pytest.mark.asyncio
async def test_filter_items_with_scope():
    """Test that filter works with scope restriction"""
    from opencode_python.providers_mgmt.models import Provider, Account

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]
    accounts = [Account(id="default", name="Default", provider_id="openai", description="Default account")]

    palette = EnhancedCommandPalette(
        storage_path=storage_path,
        providers=providers,
        accounts=accounts,
    )
    palette._filter_items("p:")

    # Should only show providers
    assert len(palette._filtered_items) > 0
    assert all(item.scope == "providers" for item in palette._filtered_items)


@pytest.mark.asyncio
async def test_filter_items_empty_query():
    """Test that filter shows all items for empty query"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    palette._filter_items("")

    assert len(palette._filtered_items) > 0


@pytest.mark.asyncio
async def test_format_item():
    """Test that item formatting works"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    item = PaletteItem(
        id="openai",
        title="OpenAI",
        description="AI provider",
        scope="providers",
        metadata={}
    )

    formatted = palette._format_item(item, show_scope=True)
    assert "OpenAI" in formatted
    assert "p:" in formatted


@pytest.mark.asyncio
async def test_format_item_no_scope():
    """Test that item formatting works without scope"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    palette = EnhancedCommandPalette(storage_path=storage_path, providers=providers)
    item = PaletteItem(
        id="openai",
        title="OpenAI",
        description="AI provider",
        scope="providers",
        metadata={}
    )

    formatted = palette._format_item(item, show_scope=False)
    assert "OpenAI" in formatted
    assert "p:" not in formatted


@pytest.mark.asyncio
async def test_on_input_changed():
    """Test that input changes trigger filtering"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)
        search_input = palette.query_one("#palette_search", Input)

        # Simulate typing
        search_input.value = "openai"
        await pilot.pause()

        # Should filter items
        assert palette._filtered_items is not None


@pytest.mark.asyncio
async def test_action_escape():
    """Test that escape action closes palette"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)

        # Should close without error
        palette.action_escape()
        await pilot.pause()


@pytest.mark.asyncio
async def test_action_up():
    """Test that up action navigates up"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)
        list_view = palette.query_one(ListView)

        # Should navigate without error
        palette.action_up()
        await pilot.pause()


@pytest.mark.asyncio
async def test_action_down():
    """Test that down action navigates down"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)

        # Should navigate without error
        palette.action_down()
        await pilot.pause()


@pytest.mark.asyncio
async def test_palette_item_creation():
    """Test that PaletteItem can be created"""
    item = PaletteItem(
        id="test-id",
        title="Test Item",
        description="Test description",
        scope="providers",
        metadata={"key": "value"},
        score=100
    )

    assert item.id == "test-id"
    assert item.title == "Test Item"
    assert item.description == "Test description"
    assert item.scope == "providers"
    assert item.metadata == {"key": "value"}
    assert item.score == 100


@pytest.mark.asyncio
async def test_rebuild_list_view():
    """Test that list view is rebuilt correctly"""
    from opencode_python.providers_mgmt.models import Provider

    storage_path = Path("/tmp/test_palette.json")
    providers = [Provider(id="openai", name="OpenAI", description="AI provider", base_url="https://api.openai.com")]

    class TestApp(App):
        def compose(self):
            yield EnhancedCommandPalette(storage_path=storage_path, providers=providers)

    app = TestApp()
    async with app.run_test() as pilot:
        palette = app.query_one(EnhancedCommandPalette)
        recents_by_scope = {"providers": []}

        # Should rebuild without error
        palette._rebuild_list_view(recents_by_scope)
        await pilot.pause()

        list_view = palette.query_one(ListView)
        assert list_view is not None
