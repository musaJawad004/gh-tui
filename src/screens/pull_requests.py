"""HomeScreen — the PR dashboard: tab bar, search, PR list + detail pane, status bar.

UI only. PRs are mock data (the ones from the design screenshot); highlighting a row
updates the detail pane on the right.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable

from models.pull_request import PullRequest
from widgets.detail_pane import DetailPane
from widgets.pr_table import PrTable
from widgets.search_bar import SearchBar
from widgets.status_bar import StatusBar
from widgets.tab_bar import TabBar


def mock_pull_requests() -> list[PullRequest]:
    return [
        PullRequest(
            repo="charmbracelet/bubbletea",
            number=1190,
            title="feat(examples): tree",
            author="dlvhdr",
            base="v2-exp",
            head="dlvhdr/tree-example",
            state="open",
            reviewers_ok=True,
            ci="fail",
            additions=391,
            deletions=4,
            updated="1h",
            created="1y",
            files_changed=6,
            commits=6,
            summary=None,
        ),
        PullRequest(
            repo="charmbracelet/bubbles",
            number=612,
            title="feat: tree bubble",
            author="dlvhdr",
            base="main",
            head="dlvhdr/tree",
            state="open",
            reviewers_ok=True,
            ci="fail",
            additions=1200,
            deletions=2,
            updated="1w",
            created="1y",
            files_changed=14,
            commits=9,
            summary="Adds a reusable tree component to bubbles.",
        ),
        PullRequest(
            repo="charmbracelet/lipgloss",
            number=304,
            title="feat(tree): support width",
            author="dlvhdr",
            base="master",
            head="dlvhdr/tree-width",
            state="open",
            reviewers_ok=True,
            ci="pass",
            additions=292,
            deletions=34,
            updated="1h",
            created="1y",
            files_changed=8,
            commits=4,
            summary="Lets tree nodes respect a fixed render width.",
        ),
    ]


class HomeScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

    def compose(self) -> ComposeResult:
        yield TabBar(
            [
                ("My Pull Requests", 3),
                ("Review Requested", 0),
                ("My Team", 2),
                ("Open Source", 367),
            ],
            active=0,
        )
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield SearchBar("is:pr is:open author:@me owner:charmbracelet")
                yield PrTable(id="pr-table")
            yield DetailPane(id="detail")
        yield StatusBar()

    def on_mount(self) -> None:
        self.prs = mock_pull_requests()
        self.query_one(PrTable).load(self.prs)
        self.query_one(DetailPane).show(self.prs[0])

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        idx = event.cursor_row
        if 0 <= idx < len(self.prs):
            self.query_one(DetailPane).show(self.prs[idx])

    def action_cursor_down(self) -> None:
        self.query_one(PrTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(PrTable).action_cursor_up()
