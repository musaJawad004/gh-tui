"""End-to-end smoke checks for the terminal workspace and theme registry."""

import asyncio

from app import GhTuiApp
from screens.main import MainScreen
from themes import THEME_NAMES


def test_app_boots_into_workspace():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, MainScreen)
            assert app.screen.query_one("#list").row_count > 0

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
