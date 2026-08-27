"""Terminal-size matrix for the focused workspaces."""

import asyncio

import pytest

from app import GhTuiApp


@pytest.mark.parametrize(
    ("size", "expected_class"),
    [
        ((240, 70), "huge"),
        ((180, 50), "huge"),
        ((160, 48), "large"),
        ((140, 40), "large"),
        ((120, 36), "list-pane"),
        ((110, 32), "compact"),
        ((100, 30), "single-pane"),
        ((90, 28), "single-pane"),
        ((80, 24), "narrow"),
        ((60, 20), "narrow"),
        ((50, 16), "too-small"),
    ],
)
def test_all_sections_render_at_terminal_size(size, expected_class):
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            screen = app.screen
            assert screen.has_class(expected_class)
            if screen.has_class("too-small"):
                assert screen.query_one("#too-small").display
                return
            for section in range(5):
                screen._section = section
                screen._render_workspace()
                assert screen.query_one("#navigator-content")
                assert screen.query_one("#detail-content")

    asyncio.run(run())
