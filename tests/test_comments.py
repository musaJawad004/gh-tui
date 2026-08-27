"""Focusable local comment drafts for PR and issue workspaces."""

import asyncio

from rich.console import Console

from app import GhTuiApp
from widgets.terminal_charts import contribution_calendar, donut_chart, line_plot


def test_pr_and_issue_comment_editors_are_focusable_and_keep_separate_drafts(tmp_path):
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace", drafts_path=tmp_path / "drafts.yml")
        async with app.run_test(size=(140, 40)) as pilot:
            editor = app.screen.query_one("#comment-editor")
            assert editor.display
            assert not editor.has_focus

            await pilot.press("e")
            await pilot.press("h", "e", "l", "l", "o")
            assert editor.has_focus
            assert editor.text == "hello"

            await pilot.press("ctrl+m")
            assert "@musa" in editor.text

            await pilot.press("escape")
            await pilot.press("2")
            await pilot.pause(0.7)
            await pilot.press("e")
            await pilot.press("r", "e", "p", "l", "y")
            assert editor.text == "reply"

            await pilot.press("escape")
            await pilot.press("1")
            await pilot.pause(0.7)
            assert editor.text == "hello@musa"

        restored = GhTuiApp(start_screen="workspace", drafts_path=tmp_path / "drafts.yml")
        async with restored.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            assert restored.screen.query_one("#comment-editor").text == "hello@musa"

    asyncio.run(run())


def test_terminal_charts_have_real_axes_and_multiple_rows():
    console = Console(width=80, record=True)
    console.print(line_plot((5, 14, 8, 21, 13), "21 peak", "cyan", width=30, height=6))
    line_output = console.export_text(clear=True)
    console.print(
        donut_chart((4, 18, 3), "4 open · 18 merged · 3 closed", ("cyan", "green", "yellow"))
    )
    donut_output = console.export_text(clear=True)

    assert "┤" in line_output
    assert "└" in line_output
    assert line_output.count("\n") >= 8
    assert "25" in donut_output
    assert donut_output.count("●") >= 15

    console.print(contribution_calendar("57 commits", "yellow", width=60, height=16))
    calendar_output = console.export_text(clear=True)
    assert "Mon" in calendar_output
    assert "Sun" in calendar_output
    assert "Less" in calendar_output
    assert "More" in calendar_output


def test_mention_shortcut_replaces_partial_mention_without_trailing_space(tmp_path):
    async def run() -> None:
        app = GhTuiApp(start_screen="workspace", drafts_path=tmp_path / "drafts.yml")
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press("e", "@", "d", "l", "ctrl+m")
            editor = app.screen.query_one("#comment-editor")
            assert editor.text == "@dlvhdr"
            assert not editor.text.endswith(" ")

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
