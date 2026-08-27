"""Focusable local comment drafts for PR and issue workspaces."""

import asyncio

from app import GhTuiApp


def test_pr_and_issue_comment_editors_are_focusable_and_keep_separate_drafts():
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace")
        async with app.run_test(size=(140, 40)) as pilot:
            editor = app.screen.query_one("#comment-editor")
            assert editor.display
            assert not editor.has_focus

            await pilot.press("e")
            await pilot.press("h", "e", "l", "l", "o")
            assert editor.has_focus
            assert editor.text == "hello"

            await pilot.press("escape")
            await pilot.press("2")
            await pilot.pause(0.7)
            await pilot.press("e")
            await pilot.press("r", "e", "p", "l", "y")
            assert editor.text == "reply"

            await pilot.press("escape")
            await pilot.press("1")
            await pilot.pause(0.7)
            assert editor.text == "hello"

    asyncio.run(run())


def test_home_dashboard_exposes_all_analytics_panels():
    async def run() -> None:
        app = GhTuiApp(start_screen="overview")
        async with app.run_test(size=(160, 48)) as pilot:
            await pilot.pause()
            assert app.screen.query_one("#analytics").display
            assert app.screen.query_one("#success-chart")
            assert app.screen.query_one("#state-chart")
            assert app.screen.query_one("#commit-chart")

    asyncio.run(run())
