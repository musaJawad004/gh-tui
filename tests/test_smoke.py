"""End-to-end smoke checks for the terminal workspace and theme registry."""

import asyncio

from app import GhTuiApp
from screens.main import MainScreen
from screens.overview import OverviewScreen
from themes import THEME_NAMES
from themes.palettes import palette_colors


def test_app_boots_into_workspace():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, MainScreen)
            assert app.screen.query_one("#workspace").display
            assert app.screen.query_one("#navigator-content")
            assert app.screen.query_one("#detail-content")

    asyncio.run(run())


def test_all_20_themes_register():
    async def run() -> None:
        app = GhTuiApp(theme="codex", start_screen="workspace")
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            assert len(THEME_NAMES) == 20
            assert set(THEME_NAMES) <= set(app.available_themes)
            assert app.theme == "codex"

    asyncio.run(run())


def test_theme_registry_matches_the_requested_palette_set():
    assert THEME_NAMES == [
        "gh-flow",
        "linear",
        "codex",
        "claude",
        "notion",
        "apple",
        "github-dark",
        "tokyo-night",
        "catppuccin-mocha",
        "gruvbox-dark",
        "dracula",
        "nord",
        "one-dark",
        "solarized-dark",
        "monokai",
        "ayu-dark",
        "rose-pine",
        "kanagawa",
        "matrix",
        "mono",
    ]
    assert palette_colors("gh-flow")["background"] == "#050706"
    assert palette_colors("gh-flow")["primary"] == "#3DDC84"
    assert palette_colors("codex")["primary"] == "#10A37F"
    assert palette_colors("mono")["error"] == "#FFFFFF"


def test_default_splash_opens_reference_dashboard():
    async def run() -> None:
        app = GhTuiApp()
        async with app.run_test(size=(154, 48)) as pilot:
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, OverviewScreen)
            assert app.screen.query_one("#activity-list")
            assert app.screen.query_one("#prs-panel")
            assert app.screen.query_one("#ci-panel")
            assert app.screen.query_one("#deploy-panel")

    asyncio.run(run())


def test_workspace_uses_compact_single_pane_at_cli_sizes():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            assert app.screen.has_class("narrow")
            assert app.screen.has_class("compact")
            assert app.screen.query_one("#navigator").display
            assert not app.screen.query_one("#detail").display
            await pilot.press("enter")
            await pilot.pause()
            assert not app.screen.query_one("#navigator").display
            assert app.screen.query_one("#detail").display
            await pilot.press("escape")
            await pilot.pause()
            assert app.screen.query_one("#navigator").display

    asyncio.run(run())


def test_every_workspace_item_is_keyboard_reachable():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(140, 40)) as pilot:
            for section, count in enumerate((4, 5, 6, 5, 8)):
                if section:
                    await pilot.press(str(section + 1))
                    await pilot.pause(0.7)
                visited = set()
                for _ in range(count):
                    visited.add(app.screen._selection())
                    await pilot.press("j")
                    await pilot.pause()
                assert visited == set(range(count))

    asyncio.run(run())


def test_overview_density_does_not_expand_activity_on_huge_terminals():
    async def run() -> None:
        app = GhTuiApp(start_screen="overview")
        async with app.run_test(size=(240, 70)) as pilot:
            await pilot.pause()
            activity = app.screen.query_one("#activity")
            panels = app.screen.query_one("#panels")
            assert activity.size.height <= 11
            assert panels.region.y <= 18

    asyncio.run(run())


def test_overview_collapses_to_one_card_on_narrow_terminals():
    async def run() -> None:
        app = GhTuiApp(start_screen="overview")
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            assert app.screen.has_class("compact")
            assert app.screen.has_class("narrow")
            assert app.screen.query_one("#prs-panel").display
            assert not app.screen.query_one("#ci-panel").display
            assert not app.screen.query_one("#deploy-panel").display

    asyncio.run(run())


def test_workspace_responsive_tiers_keep_content_reachable():
    async def check(size, expected_class: str) -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            assert app.screen.has_class(expected_class)
            assert app.screen.query_one("#workspace").display

    asyncio.run(check((240, 70), "huge"))
    asyncio.run(check((150, 44), "large"))
    asyncio.run(check((100, 30), "single-pane"))
    asyncio.run(check((80, 24), "narrow"))


def test_workspace_shows_resize_message_below_supported_size():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(50, 16)) as pilot:
            await pilot.pause()
            assert app.screen.has_class("too-small")
            assert app.screen.query_one("#too-small").display
            assert not app.screen.query_one("#workspace").display

    asyncio.run(run())
