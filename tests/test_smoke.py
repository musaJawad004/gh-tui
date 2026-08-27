"""End-to-end smoke checks for the terminal workspace and theme registry."""

import asyncio

from app import GhTuiApp
from screens.main import MainScreen
from screens.overview import OverviewScreen
from themes import THEME_NAMES


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


def test_all_25_themes_register():
    async def run() -> None:
        app = GhTuiApp(theme="papercolor-light", start_screen="workspace")
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            assert len(THEME_NAMES) == 25
            assert set(THEME_NAMES) <= set(app.available_themes)
            assert app.theme == "papercolor-light"

    asyncio.run(run())


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
            assert not app.screen.query_one("#navigator").display
            assert app.screen.query_one("#detail").display

    asyncio.run(run())
