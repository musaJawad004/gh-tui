"""DetailPane — right side: repo·#num, title, Open badge, branch, author, tabs, summary,
and a Changes card. Populated from the highlighted PR via show().
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

import icons
from models.pull_request import PullRequest, humanize_count
from themes.palettes import active_colors


class DetailPane(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static(id="d-repo")
        yield Static(id="d-title")
        yield Static(id="d-badge")
        yield Static(id="d-meta")
        yield Static(id="d-tabs")
        yield Static(id="d-summary-h")
        yield Static(id="d-summary")
        yield Static(id="d-changes-h")
        yield Static(id="d-files", classes="card")
        yield Static(id="d-commits")

    def show(self, pr: PullRequest) -> None:
        colors = active_colors(self.app)
        self.query_one("#d-repo", Static).update(
            Text.assemble((pr.repo, "dim"), ("  ·  ", "dim"), (f"#{pr.number}", "dim"))
        )
        self.query_one("#d-title", Static).update(Text(pr.title, style="bold"))

        badge = Text()
        badge.append(f" {icons.PR} Open ", style=f"bold {colors['background']} on {colors['primary']}")
        badge.append(f"   {pr.base} ", style="dim")
        badge.append(f"{icons.ARROW} ", style="dim")
        badge.append(pr.head, style=colors["secondary"])
        self.query_one("#d-badge", Static).update(badge)

        meta = Text()
        meta.append("by ", style="dim")
        meta.append(f"@{pr.author}", style=colors["secondary"])
        meta.append(f"  ·  {pr.created} ago  ·  ", style="dim")
        meta.append("none", style="dim")
        self.query_one("#d-meta", Static).update(meta)

        tabs = Text()
        tabs.append(f"{icons.OVERVIEW} Overview", style="bold")
        tabs.append("     ")
        tabs.append(f"{icons.CHECKS_TAB} Checks", style="dim")
        tabs.append("     ")
        tabs.append(f"{icons.ACTIVITY} Activity", style="dim")
        self.query_one("#d-tabs", Static).update(tabs)

        self.query_one("#d-summary-h", Static).update(
            Text(f"{icons.SUMMARY} Summary", style="bold")
        )
        if pr.summary:
            self.query_one("#d-summary", Static).update(Text(pr.summary))
        else:
            self.query_one("#d-summary", Static).update(
                Text("No description provided.", style="italic dim")
            )

        self.query_one("#d-changes-h", Static).update(
            Text(f"{icons.CHANGES} Changes", style="bold")
        )

        files = Text()
        files.append(f"{icons.FILES} {pr.files_changed} files changed   ")
        files.append(f"+{humanize_count(pr.additions)} ", style=colors["success"])
        files.append(f"-{humanize_count(pr.deletions)}", style=colors["error"])
        self.query_one("#d-files", Static).update(files)

        self.query_one("#d-commits", Static).update(
            Text(f"{icons.COMMITS} {pr.commits} commits {pr.updated} ago", style="dim")
        )
