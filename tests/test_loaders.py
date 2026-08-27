"""Loader component and task-transition checks."""

import asyncio

from app import GhTuiApp
from widgets.spinner import (
    indeterminate_bar,
    inline_loader,
    progress_bar,
    spinner_frame,
    step_loader,
)


def test_loader_renderables_cover_each_task_shape():
    assert spinner_frame("connect", 0) != spinner_frame("connect", 1)
    assert "Syncing with GitHub" in inline_loader("Syncing with GitHub", 2).plain
    assert "50%" in progress_bar(0.5).plain
    assert "connect" in step_loader(["init", "connect", "complete"], 1, 2).plain
    assert "[" in indeterminate_bar(3).plain


def test_section_switch_uses_task_loader():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("2")
            await pilot.pause(0.12)
            assert app.screen.query_one("#loader").display
            assert not app.screen.query_one("#workspace").display
            await pilot.pause(0.7)
            assert not app.screen.query_one("#loader").display
            assert app.screen.query_one("#workspace").display

    asyncio.run(run())
