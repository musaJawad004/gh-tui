"""PrTable — the two-line PR list (repo on top line, title below), with CI, diff, times.

Uses a DataTable with height-2 rows: the Title cell holds two lines, every other cell holds
one line (top-aligned to the repo line), matching the gh-dash layout.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import DataTable

import icons
from models.pull_request import PullRequest, humanize_count
from themes.palettes import active_colors


class PrTable(DataTable):
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = False
        self.show_cursor = True
        self.cell_padding = 1
        self._build_columns()

    def _build_columns(self) -> None:
        head = lambda g: Text(g, style="dim")
        self.add_column(head(icons.PR_HEADER), width=2, key="icon")
        self.add_column(head("Title"), width=30, key="title")
        self.add_column(head(icons.REVIEWERS), width=2, key="rev")
        self.add_column(head(icons.CHECKS), width=2, key="ci")
        self.add_column(head(icons.DIFF), width=9, key="diff")
        self.add_column(head(icons.UPDATED), width=3, key="upd")
        self.add_column(head(icons.CREATED), width=3, key="cre")

    def load(self, prs: list[PullRequest]) -> None:
        self.clear()  # keeps columns
        for pr in prs:
            self.add_row(*self._cells(pr), height=2, key=f"{pr.repo}#{pr.number}")

    def _cells(self, pr: PullRequest) -> list[Text]:
        colors = active_colors(self.app)
        icon = Text(icons.PR, style=colors["primary"])

        title = Text()
        title.append(pr.repo + "\n", style=colors["secondary"])
        title.append(pr.title)

        rev = Text(icons.APPROVED, style=colors["success"]) if pr.reviewers_ok else Text("")

        if pr.ci == "pass":
            ci = Text(icons.CI_PASS, style=colors["success"])
        elif pr.ci == "fail":
            ci = Text(icons.CI_FAIL, style=colors["error"])
        else:
            ci = Text(icons.CI_PENDING, style=colors["warning"])

        diff = Text()
        diff.append(f"+{humanize_count(pr.additions)} ", style=colors["success"])
        diff.append(f"-{humanize_count(pr.deletions)}", style=colors["error"])

        upd = Text(pr.updated, style="dim")
        cre = Text(pr.created, style="dim")
        return [icon, title, rev, ci, diff, upd, cre]
