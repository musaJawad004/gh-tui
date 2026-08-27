"""Focused split-pane workspaces for pull requests, issues, CI/CD and commits.

These screens are intentionally presentation-only for now. They establish the complete
information architecture and visual hierarchy before GitHub mutations are connected.
"""

from __future__ import annotations

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key, Resize
from textual.screen import Screen
from textual.widgets import Static, TextArea

from core.github_data import relative_time
from themes.palettes import active_colors
from widgets.spinner import indeterminate_bar, inline_loader, spinner_frame
from widgets.terminal_charts import (
    contribution_calendar,
    donut_chart,
    horizontal_bars,
    line_plot,
    vertical_bars,
)

SECTIONS = ["Pull Requests", "Issues", "CI / CD", "Repo Manager", "Commits"]
PR_IDS = ("#142", "#141", "#140", "#139")
ISSUE_IDS = ("#87", "#85", "#84", "#80", "#78")
LOCAL_MENTIONS = ("@musa", "@dlvhdr", "@sarah", "@reviewers")


def _grid(*ratios: int, padding: tuple[int, int] = (0, 1)) -> Table:
    table = Table.grid(expand=True, padding=padding)
    for ratio in ratios:
        table.add_column(ratio=ratio)
    return table


class CommentEditor(TextArea):
    """A text editor that opts into focus only when clicked or explicitly opened."""

    can_focus = False

    def on_click(self) -> None:
        self.can_focus = True
        self.focus()

    def on_blur(self) -> None:
        self.can_focus = False

    def on_key(self, event: Key) -> None:
        # Standard terminals encode Ctrl+M as Enter. When an @mention fragment is
        # active, consume that carriage return as completion instead of a newline.
        if event.key == "enter" and self.screen._complete_mention(self):
            event.prevent_default()
            event.stop()


class MainScreen(Screen):
    """A dense terminal workspace with a navigator and contextual detail pane."""

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
        background: $background;
        color: $foreground;
    }
    MainScreen #header {
        height: 4;
        padding: 0 1;
        border-bottom: solid $border-dim;
        background: $background;
    }
    MainScreen #workspace { height: 1fr; }
    MainScreen #navigator {
        width: 42%;
        height: 1fr;
        padding: 1;
        border-right: solid $border-dim;
        overflow: hidden hidden;
        background: $background;
    }
    MainScreen #navigator-content { height: 1fr; overflow-y: auto; overflow-x: hidden; }
    MainScreen #navigator-analytics { height: 14; min-height: 14; overflow: hidden hidden; }
    MainScreen #detail {
        width: 58%;
        height: 1fr;
        padding: 1 2;
        overflow: hidden hidden;
        background: $background;
    }
    MainScreen #detail-content { height: 1fr; overflow: hidden hidden; }
    MainScreen #comment-editor {
        display: none;
        height: 6;
        margin: 0 0 1 0;
        border: round $border-dim;
        background: $background;
        color: $foreground;
    }
    MainScreen #comment-editor:focus { border: round $primary; }
    MainScreen #comment-hint {
        display: none;
        height: 1;
        color: $text-muted;
    }
    MainScreen #loader {
        display: none;
        height: 1fr;
        padding: 4 5;
        color: $text-muted;
        background: $background;
    }
    MainScreen #status {
        height: 2;
        padding: 0 1;
        border-top: solid $border-dim;
        color: $text-muted;
        background: $surface;
    }
    MainScreen #too-small {
        display: none;
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
    }
    MainScreen.huge #navigator { width: 36%; }
    MainScreen.huge #detail { width: 64%; }
    MainScreen.large #navigator { width: 40%; }
    MainScreen.large #detail { width: 60%; }
    MainScreen.single-pane.list-pane #navigator {
        display: block; width: 100%; border-right: none;
    }
    MainScreen.single-pane.list-pane #detail { display: none; }
    MainScreen.single-pane.detail-pane #navigator { display: none; }
    MainScreen.single-pane.detail-pane #detail { display: block; width: 100%; }
    MainScreen.compact #header { height: 3; }
    MainScreen.compact #status { height: 1; }
    MainScreen.compact #navigator,
    MainScreen.compact #detail { padding: 0 1; }
    MainScreen.compact #comment-editor { height: 4; margin-bottom: 0; }
    MainScreen.compact #navigator-analytics { display: none; }
    MainScreen.too-small #header,
    MainScreen.too-small #workspace,
    MainScreen.too-small #status { display: none; }
    MainScreen.too-small #too-small { display: block; }
    """

    BINDINGS = [
        ("1", "section_1", ""),
        ("2", "section_2", ""),
        ("3", "section_3", ""),
        ("4", "section_4", ""),
        ("5", "section_5", ""),
        ("tab", "next_section", "Next"),
        ("shift+tab", "prev_section", "Prev"),
        ("right", "focus_right", ""),
        ("left", "focus_left", ""),
        ("j", "selection_down", "Down"),
        ("k", "selection_up", "Up"),
        ("down", "selection_down", ""),
        ("up", "selection_up", ""),
        ("enter", "open_detail", "Open"),
        ("e", "focus_comment", "Comment"),
        ("escape", "back_to_list", "Back"),
        ("o", "overview", "Overview"),
        ("g", "settings", "Settings"),
        Binding("ctrl+s", "save_comment", "Save local", priority=True),
        Binding("ctrl+m", "insert_mention", "Mention", priority=True),
    ]

    def __init__(self, section: int = 0) -> None:
        super().__init__()
        self._initial_section = section % len(SECTIONS)

    def compose(self) -> ComposeResult:
        yield Static(id="header")
        yield Static(id="loader")
        with Horizontal(id="workspace"):
            with Vertical(id="navigator"):
                yield Static(id="navigator-content")
                yield Static(id="navigator-analytics")
            with Vertical(id="detail"):
                yield Static(id="detail-content")
                yield CommentEditor(
                    placeholder="Write a Markdown comment…",
                    soft_wrap=True,
                    show_line_numbers=False,
                    id="comment-editor",
                )
                yield Static(
                    "[e/click] edit · [esc] done · [ctrl+s] save local · [ctrl+m] @mention",
                    id="comment-hint",
                )
        yield Static(id="status")
        yield Static(id="too-small")

    def on_mount(self) -> None:
        self._section = self._initial_section
        self._load_frame = 0
        self._load_timer = None
        self._compact = False
        self._selected = [0] * len(SECTIONS)
        self._item_counts = [4, 5, 6, 5, 8]
        self._pane = "list"
        self._animation_frame = 0
        self._mention_index = 0
        self.add_class("list-pane")
        self._apply_breakpoints(self.size.width, self.size.height)
        self._render_workspace()
        self.set_interval(0.12, self._tick_ambient_animation)

    def on_resize(self, event: Resize) -> None:
        self._apply_breakpoints(event.size.width, event.size.height)
        if self.is_mounted and self._load_timer is None:
            self._render_workspace()

    def _apply_breakpoints(self, width: int, height: int) -> None:
        self._compact = height < 34
        states = {
            "huge": width >= 180 and height >= 50,
            "large": 140 <= width < 180 and height >= 40,
            "single-pane": width < 110 or height < 30,
            "narrow": width < 90 or height < 26,
            "compact": self._compact,
            "too-small": width < 60 or height < 18,
        }
        for class_name, active in states.items():
            if active:
                self.add_class(class_name)
            else:
                self.remove_class(class_name)
        message = Text("Terminal too small\n", style=f"bold {self._c('warning')}")
        message.append("resize to at least 60 columns × 18 rows", style="dim")
        self.query_one("#too-small", Static).update(message)

    def _tick_ambient_animation(self) -> None:
        self._animation_frame += 1
        if self._section == 2 and self._load_timer is None and self.is_mounted:
            self._render_workspace()

    def on_screen_resume(self) -> None:
        self.refresh_theme()

    def refresh_theme(self) -> None:
        self._render_workspace()

    def refresh_data(self) -> None:
        """Refresh visible renderables after the read-only gh worker completes."""
        if hasattr(self, "_section") and self.is_mounted:
            self._render_workspace()

    def _c(self, name: str) -> str:
        return active_colors(self.app)[name]

    def _selection(self) -> int:
        return self._selected[self._section]

    def _render_workspace(self) -> None:
        self._render_header()
        renderers = [
            self._pull_requests,
            self._issues,
            self._pipelines,
            self._repositories,
            self._commits,
        ]
        left, right, status = renderers[self._section]()
        snapshot = self.app.github_snapshot
        if snapshot is not None and not self.app.data_error:
            counts = [len(snapshot.pull_requests), len(snapshot.issues), len(snapshot.workflows), 1, len(snapshot.commits)]
            if counts[self._section] > 0:
                self._item_counts[self._section] = counts[self._section]
        self.query_one("#navigator-content", Static).update(left)
        self.query_one("#navigator-analytics", Static).update(self._section_analytics())
        self.query_one("#detail-content", Static).update(right)
        self.query_one("#status", Static).update(status)
        self._configure_comment_editor()

    def _draft_key(self) -> str:
        """Use repository + GitHub number so drafts survive sorting and restarts."""
        identifiers = PR_IDS if self._section == 0 else ISSUE_IDS
        identifier = identifiers[min(self._selection(), len(identifiers) - 1)]
        kind = "pr" if self._section == 0 else "issue"
        return f"{kind}:musa/my-app:{identifier}"

    def _save_comment_draft(self) -> None:
        if self._section in {0, 1}:
            editor = self.query_one("#comment-editor", TextArea)
            key = self._draft_key()
            if editor.text:
                self.app.comment_drafts[key] = editor.text
            else:
                self.app.comment_drafts.pop(key, None)
            self.app.persist_comment_drafts()

    def _configure_comment_editor(self) -> None:
        editor = self.query_one("#comment-editor", TextArea)
        hint = self.query_one("#comment-hint", Static)
        supports_comments = self._section in {0, 1}
        editor.display = supports_comments
        hint.display = supports_comments
        if supports_comments:
            editor.placeholder = (
                "Write a PR review comment…"
                if self._section == 0
                else "Write an issue reply…"
            )
            draft = self.app.comment_drafts.get(self._draft_key(), "")
            if editor.text != draft:
                editor.load_text(draft)
            self._update_comment_hint(editor.text)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id == "comment-editor" and self._section in {0, 1}:
            key = self._draft_key()
            if event.text_area.text:
                self.app.comment_drafts[key] = event.text_area.text
            else:
                self.app.comment_drafts.pop(key, None)
            self.app.persist_comment_drafts()
            self._update_comment_hint(event.text_area.text)

    def _update_comment_hint(self, text: str) -> None:
        hint = self.query_one("#comment-hint", Static)
        prefix = text.rsplit("@", 1)[-1].lower() if "@" in text else ""
        matches = [name for name in LOCAL_MENTIONS if not prefix or name[1:].startswith(prefix)]
        if "@" in text and matches:
            hint.update("local mentions: " + "  ".join(matches) + "  ·  [ctrl+m] insert")
        else:
            hint.update(
                "[e/click] edit · [esc] done · [ctrl+s] save local · [ctrl+m] @mention"
            )

    def _render_header(self) -> None:
        line = Text()
        line.append(" gh-flow ", style=f"bold {self._c('background')} on {self._c('success')}")
        line.append(f"  {self.app.repository or 'no repository'}", style=self._c("primary"))
        line.append("  main ↑2", style=self._c("success"))
        line.append("  ·  clean\n", style="dim")
        labels = ["PRs", "Issues", "CI", "Repo", "Commits"] if self.size.width < 90 else SECTIONS
        for index, name in enumerate(labels):
            if index:
                line.append("  │  ", style="dim")
            if index == self._section:
                line.append(f" {index + 1} {name} ", style=f"bold on {self._c('row_selected')}")
            else:
                line.append(f" {index + 1} {name} ", style="dim")
        self.query_one("#header", Static).update(line)

    def _search(self, value: str, hint: str) -> Panel:
        content = Text("⌕  ", style=self._c("primary"))
        content.append(value)
        content.append(f"   {hint}", style="dim")
        return Panel(content, border_style=self._c("border"), padding=(0, 1))

    def _analytics(self, first: tuple, second: tuple) -> Panel:
        plot_width = 28
        donut_width = 21
        plot_height = 7
        table = _grid(3, 2, padding=(0, 2))
        first_title, first_values, first_summary, first_color = first
        second_title, second_values, second_summary, second_color = second
        left = Group(
            Text(first_title, style=f"bold {self._c('primary')}"),
            line_plot(
                first_values,
                first_summary,
                self._c(first_color),
                width=plot_width,
                height=plot_height,
                legend="7-day trend",
            ),
        )
        legend_labels = tuple(
            part.strip().split(" ", 1)[1]
            for part in second_summary.split("·")
            if " " in part.strip()
        )
        right = Group(
            Text(second_title, style=f"bold {self._c('primary')}"),
            donut_chart(
                second_values,
                f"{sum(second_values)} total",
                (
                    self._c(second_color),
                    self._c("success"),
                    self._c("warning"),
                    self._c("error"),
                ),
                width=donut_width,
                height=9,
                labels=legend_labels,
            ),
        )
        table.add_row(left, right)
        return Panel(table, title="analytics", border_style=self._c("border"), padding=(0, 1))

    def _section_analytics(self):
        """Return a distinct bottom-anchored visualization for the active section."""
        snapshot = self.app.github_snapshot
        if snapshot is not None:
            if self._section == 0:
                count = len(snapshot.pull_requests)
                return self._analytics(("open pull requests", (count,), f"{count} open", "primary"), ("pull request state", (count, 0, 0), f"{count} open · 0 merged · 0 closed", "primary"))
            if self._section == 1:
                count = len(snapshot.issues)
                return Panel(donut_chart((count, 0, 0), f"{count} tracked issues", (self._c("warning"), self._c("success"), self._c("error")), width=25, height=11, labels=("open", "closed", "blocked")), title="issue distribution", border_style=self._c("border"))
            if self._section == 2:
                passed = sum((item.get("conclusion") or "").lower() == "success" for item in snapshot.workflows)
                failed = sum((item.get("conclusion") or "").lower() in {"failure", "cancelled"} for item in snapshot.workflows)
                running = max(0, len(snapshot.workflows) - passed - failed)
                return Panel(horizontal_bars(("passed", "failed", "running"), (passed, failed, running), (self._c("success"), self._c("error"), self._c("warning")), f"{len(snapshot.workflows)} workflow runs", width=42, row_spacing=1), title="workflow outcomes", border_style=self._c("border"), padding=(0, 1))
            if self._section == 3:
                return Panel(Text(f"{len(snapshot.branches)} branches\n{len(snapshot.repositories)} repositories\n{len(snapshot.releases)} releases", style=self._c("primary")), title="repository activity", border_style=self._c("border"), padding=(1, 2))
            return Panel(Text(f"{len(snapshot.commits)} commits fetched\nread-only activity", style=self._c("success")), title="commit contributions", border_style=self._c("border"), padding=(1, 2))
        navigator_ratio = 0.36 if self.size.width >= 180 and self.size.height >= 50 else 0.40
        width = max(30, int(self.size.width * navigator_ratio) - 6)
        if self._section == 0:
            return self._analytics(
                ("merge rate", (42, 56, 51, 68, 72, 81, 76), "76% · last 7 days", "success"),
                ("pull request state", (4, 18, 3), "4 open · 18 merged · 3 closed", "primary"),
            )
        if self._section == 1:
            chart = donut_chart(
                (7, 24, 5),
                "36 tracked issues",
                (self._c("warning"), self._c("success"), self._c("error")),
                width=min(31, width - 4),
                height=11,
                labels=("open", "closed", "blocked"),
            )
            centered = Table.grid(expand=True)
            centered.add_column(justify="center")
            centered.add_row(chart)
            return Panel(centered, title="issue distribution", border_style=self._c("border"))
        if self._section == 2:
            return Panel(
                horizontal_bars(
                    ("passed", "failed", "running"),
                    (19, 3, 1),
                    (self._c("success"), self._c("error"), self._c("warning")),
                    "23 workflow runs · 95% success",
                    width=width - 4,
                    row_spacing=1,
                ),
                title="workflow outcomes",
                border_style=self._c("border"),
                padding=(0, 1),
            )
        if self._section == 3:
            return Panel(
                vertical_bars(
                    (4, 7, 3, 9, 12, 8, 14),
                    ("M", "T", "W", "T", "F", "S", "S"),
                    "57 commits · repository activity",
                    self._c("primary"),
                    width=width - 4,
                    height=6,
                ),
                title="repository activity",
                border_style=self._c("border"),
                padding=(0, 1),
            )
        return Panel(
            contribution_calendar(
                "57 commits · main ↑2",
                self._c("success"),
                width=width - 4,
                height=9,
            ),
            title="commit contributions",
            border_style=self._c("border"),
            padding=(0, 1),
        )

    def _pull_requests(self):
        rows = [
            ("#142", "Add Google OAuth login", "feat/oauth", "✓", "2/2", "+391  -4", "4m"),
            ("#141", "Improve dashboard charts", "feat/dashboard", "✓", "6/6", "+120  -18", "1h"),
            ("#140", "Fix mobile layout issues", "fix/mobile", "✓", "6/6", "+48  -12", "18m"),
            ("#139", "Payment retry mechanism", "fix/payment", "✓", "6/6", "+92  -31", "3h"),
        ]
        if self.app.github_snapshot is not None:
            rows = self.app.github_snapshot.pr_rows()
            if not rows:
                rows = [("—", "No open pull requests", "—", "·", "0/0", "+0  -0", "now")]
        selected = min(self._selection(), len(rows) - 1)
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=6)
        table.add_column(ratio=1)
        table.add_column(width=5, justify="center")
        table.add_column(width=12, justify="right")
        table.add_row(
            Text("PR", style="bold"),
            Text("Title / branch", style="bold"),
            Text("CI", style="bold"),
            Text("Changes", style="bold", justify="right"),
        )
        for index, (number, title, branch, ci, checks, changes, age) in enumerate(rows):
            title_cell = Text(title, style="bold" if index == 0 else "")
            title_cell.append(f"\n{branch} → main", style="dim")
            ci_cell = Text(f"{ci}\n{checks}", style=self._c("success"), justify="center")
            change_cell = Text(changes, justify="right")
            change_cell.stylize(self._c("success"), 0, changes.index("-") - 2)
            change_cell.stylize(self._c("error"), changes.index("-"))
            change_cell.append(f"\n{age} ago", style="dim")
            style = f"on {self._c('row_selected')}" if index == selected else None
            table.add_row(Text(number, style=self._c("primary")), title_cell, ci_cell, change_cell, style=style)

        left = Group(
            self._search("is:pr is:open author:@me", "4 open"),
            Text("\n"),
            table,
        )

        number, title, branch, _ci, checks, changes, age = rows[selected]
        meta = Text()
        meta.append(f"{self.app.repository or 'repository'}  ·  {number}\n", style=self._c("primary"))
        meta.append(f"{title}\n", style="bold")
        meta.append("\n OPEN ", style=f"bold {self._c('background')} on {self._c('primary')}")
        meta.append(f"  {branch} → main  ·  by @musa  ·  {age} ago\n", style="dim")
        meta.append(f"\n▣ Overview   ✓ Checks {checks}   ◇ Files changed 8   ◌ Activity", style="bold")

        summary = Text()
        summary.append("Ready for review\n", style=f"bold {self._c('success')}")
        summary.append(f"{title} is ready for a focused review before merge.\n\n")
        added, removed = changes.split("  ")
        summary.append(f"{added} additions   ", style=self._c("success"))
        summary.append(f"{removed} deletions   ", style=self._c("error"))
        files_changed = next((item.get("changedFiles") for item in (self.app.github_snapshot.pull_requests if self.app.github_snapshot else []) if f"#{item.get('number')}" == number), 0)
        summary.append(f"{files_changed or 0} files changed", style="dim")

        comment = Text()
        if self.app.github_snapshot is not None:
            comment.append("No review activity loaded for this pull request.\n", style="dim")
            comment.append("Read-only loading does not invent conversation data.", style="dim")
        else:
            comment.append("@sarah  ·  reviewer  ·  2m\n", style="bold")
            comment.append("The callback flow looks clean. One small question about token expiry, ")
            comment.append("otherwise this is ready to merge.", style="dim")

        right = Group(
            meta,
            Text("\n"),
            Panel(summary, title="review summary", border_style=self._c("border")),
            Text("\n conversation", style=self._c("primary")),
            Panel(comment, border_style=self._c("border")),
        )
        return left, right, self._status(
            f"PR {selected + 1}/{len(rows)}", "2 approvals", f"{checks} checks", "8 files"
        )

    def _issues(self):
        rows = [
            ("#87", "OAuth redirect fails on Safari", "bug · auth", "4", "2h"),
            ("#85", "Dark theme contrast on tables", "ui", "1", "5h"),
            ("#84", "Add pagination to PR list", "enhancement", "0", "8h"),
            ("#80", "Document the config file", "docs · good first issue", "3", "1d"),
            ("#78", "Flaky E2E on checkout step", "bug · ci", "6", "1d"),
        ]
        if self.app.github_snapshot is not None:
            rows = self.app.github_snapshot.issue_rows()
            if not rows:
                rows = [("—", "No open issues", "—", "0", "now")]
        selected = min(self._selection(), len(rows) - 1)
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=6)
        table.add_column(ratio=1)
        table.add_column(width=8, justify="right")
        for index, (number, title, labels, comments, age) in enumerate(rows):
            body = Text(title, style="bold" if index == 0 else "")
            body.append(f"\n{labels}", style=self._c("warning"))
            tail = Text(f"◌ {comments}\n{age}", style="dim", justify="right")
            style = f"on {self._c('row_selected')}" if index == selected else None
            table.add_row(Text(number, style=self._c("warning")), body, tail, style=style)
        left = Group(
            self._search("is:issue is:open", "7 open"),
            Text("\n"),
            table,
        )

        number, title, labels, comments, age = rows[selected]
        header = Text()
        header.append(f"{self.app.repository or 'repository'}  ·  Issue {number}\n", style=self._c("primary"))
        header.append(f"{title}\n", style="bold")
        header.append("\n OPEN ", style=f"bold {self._c('background')} on {self._c('success')}")
        header.append(f"  opened by @dlvhdr {age} ago  ·  {labels}\n", style="dim")
        header.append("\n▣ Conversation   ◉ Timeline   ◇ Related PRs", style="bold")

        first = Text()
        reply = Text()
        if self.app.github_snapshot is not None:
            first.append("No issue conversation was returned by the read-only query.\n", style="dim")
            reply.append("Comments are not fabricated; refresh to query the repository again.", style="dim")
        else:
            first.append("@dlvhdr  ·  author  ·  2h\n", style="bold")
            first.append(f"Discussion for “{title}”. ")
            first.append("This thread captures the current context and reproduction details.\n\n", style="dim")
            first.append("macOS 15.6  ·  Safari 18.6  ·  production", style=self._c("warning"))
            reply.append("@musa  ·  maintainer  ·  38m\n", style="bold")
            reply.append("Confirmed. The SameSite policy looks like the likely cause. ")
            reply.append("I’m tracing the callback cookie now.", style="dim")
        right = Group(
            header,
            Text("\n"),
            Panel(first, border_style=self._c("border")),
            Panel(reply, border_style=self._c("border")),
        )
        return left, right, self._status(
            f"Issue {selected + 1}/{len(rows)}",
            f"{comments} comments",
            "2 participants",
            f"updated {age}",
        )

    def _pipelines(self):
        rows = [
            ("×", "backend-tests", "main", "failed", "4m 12s", "4m"),
            ("✓", "lint & format", "main", "passed", "1m 03s", "6m"),
            ("✓", "e2e tests", "feat/oauth", "passed", "5m 41s", "12m"),
            ("✓", "build & package", "main", "passed", "2m 21s", "16m"),
            ("○", "deploy preview", "feat/oauth", "running", "3m 11s", "now"),
            ("✓", "security scan", "main", "passed", "1m 34s", "18m"),
        ]
        if self.app.github_snapshot is not None:
            rows = self.app.github_snapshot.workflow_rows()
            if not rows:
                rows = [("·", "No workflow runs", "—", "queued", "—", "now")]
        selected = min(self._selection(), len(rows) - 1)
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=3)
        table.add_column(ratio=1)
        table.add_column(width=11, justify="right")
        for index, (icon, name, branch, state, duration, age) in enumerate(rows):
            color = "error" if state == "failed" else "warning" if state == "running" else "success"
            if state == "running":
                icon = spinner_frame("dots", self._animation_frame)
            body = Text(name, style="bold" if index == 0 else "")
            body.append(f"\n{branch}", style="dim")
            tail = Text(state, style=self._c(color), justify="right")
            tail.append(f"\n{duration} · {age}", style="dim")
            style = f"on {self._c('row_selected')}" if index == selected else None
            table.add_row(Text(icon, style=self._c(color)), body, tail, style=style)
        left = Group(
            self._search("branch:main event:push", "23 runs"),
            Text("\n"),
            table,
        )

        _icon, name, branch, state, duration, age = rows[selected]
        state_color = "error" if state == "failed" else "warning" if state == "running" else "success"
        header = Text()
        header.append(f"{name}  ·  run #{9182 - selected}\n", style=self._c("primary"))
        header.append(f"{branch}  ·  981dad2  ·  push by @musa\n", style="dim")
        header.append(
            f"\n {state.upper()} ",
            style=f"bold {self._c('background')} on {self._c(state_color)}",
        )
        header.append(f"  {duration}  ·  {age} ago\n")
        header.append("\n▣ Summary   ◉ Jobs 3   ≡ Logs   ⇧ Artifacts 2", style="bold")

        steps = Table.grid(expand=True, padding=(0, 1))
        steps.add_column(width=3)
        steps.add_column(ratio=1)
        steps.add_column(width=10, justify="right")
        for icon, label, value, color in (
            ("✓", "checkout", "8s", "success"),
            ("✓", "setup python 3.12", "12s", "success"),
            ("✓", "install dependencies", "42s", "success"),
            ("×", "pytest", "3m 02s", "error"),
            ("–", "upload coverage", "skipped", "muted"),
        ):
            steps.add_row(Text(icon, style=self._c(color)), Text(label), Text(value, style="dim"))
        logs = Text()
        logs.append(f"workflow/{name.replace(' ', '-')} ", style="dim")
        logs.append(f"{state.upper()}\n", style=self._c(state_color))
        logs.append(
            "AssertionError: state cookie was not restored\n"
            if state == "failed"
            else "All configured steps completed without errors.\n",
            style=self._c(state_color),
        )
        logs.append(f"selected run finished in {duration}", style="dim")
        right = Group(
            header,
            Text("\n pipeline", style=self._c("primary")),
            Panel(steps, border_style=self._c("border")),
            Text("\n failure log", style=self._c("error")),
            Panel(logs, border_style=self._c("error")),
            Text("\n deployments  production ✓   staging ✓   preview ○ running", style="dim"),
        )
        return left, right, self._status(
            f"Run {selected + 1}/{len(rows)}", "3 jobs", state, "2 artifacts"
        )

    def _repositories(self):
        rows = [
            ("musa/my-app", "Python", "public", "42", "2h"),
            ("musa/gh-tui", "Python", "public", "128", "1d"),
            ("musa/portfolio", "TypeScript", "public", "17", "3d"),
            ("musa/emberflow", "Go", "public", "64", "5d"),
            ("musa/job-agent", "Python", "private", "0", "1w"),
        ]
        if self.app.github_snapshot is not None:
            repo = self.app.github_snapshot.repository
            rows = [(
                repo.get("nameWithOwner") or self.app.repository or "—",
                "—", repo.get("visibility", "—"),
                str(repo.get("stargazerCount", 0)), "now",
            )]
        selected = min(self._selection(), len(rows) - 1)
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(width=13)
        table.add_column(width=8, justify="right")
        for index, (name, lang, visibility, stars, age) in enumerate(rows):
            body = Text(name, style=f"bold {self._c('primary')}")
            body.append(f"\n{lang} · {visibility}", style="dim")
            tail = Text(f"★ {stars}\n{age}", style=self._c("warning"), justify="right")
            table.add_row(
                body,
                "",
                tail,
                style=f"on {self._c('row_selected')}" if index == selected else None,
            )
        left = Group(
            self._search("owner:musa", "6 repos"),
            Text("\n"),
            table,
        )
        name, lang, visibility, stars, age = rows[selected]
        info = Text()
        info.append(f"{name}\n", style=f"bold {self._c('primary')}")
        info.append("GitHub workflow dashboard and deployment toolkit.\n\n", style="dim")
        info.append("main  ↑2   clean\n", style=self._c("success"))
        info.append(f"{lang}  ·  MIT  ·  {visibility}  ·  ★ {stars}\n\n", style="dim")
        snapshot = self.app.github_snapshot
        if snapshot is not None:
            info.append(f"{len(snapshot.pull_requests)} pull requests   {len(snapshot.issues)} issues   {len(snapshot.releases)} releases\n")
            info.append(f"{len(snapshot.workflows)} workflow runs   {len(snapshot.commits)} commits", style=self._c("success"))
            branches = ", ".join(
                branch.get("name", "") for branch in snapshot.branches[:5]
            )
            if branches:
                info.append(f"\n\nbranches  {branches}", style="dim")
        else:
            info.append("Repository data is still loading…", style="dim")
        tree = Text("▾ src\n  ▾ screens\n    overview.py\n    main.py\n  ▾ widgets\n    spinner.py\n  app.py\n▸ tests\nREADME.md", style="dim")
        actions = Text()
        actions.append("read-only loading phase\n", style=self._c("warning"))
        actions.append("○ create repository\n○ create branch\n○ commit & push\n○ open pull request\n○ open issue", style="dim")
        right = Group(
            info,
            Text("\n repository tree", style=self._c("primary")),
            Panel(tree, border_style=self._c("border")),
            Text("\n planned actions", style=self._c("primary")),
            Panel(actions, border_style=self._c("border")),
        )
        return left, right, self._status(
            f"Repo {selected + 1}/{len(rows)}", "main ↑2", "clean", f"updated {age}"
        )

    def _commits(self):
        snapshot_commits = self.app.github_snapshot.commit_rows() if self.app.github_snapshot else []
        if snapshot_commits:
            selected = min(self._selection(), len(snapshot_commits) - 1)
            tree = Text()
            tree.append(f"⌕  {len(snapshot_commits)} recent commits\n\n", style="dim")
            for index, item in enumerate(snapshot_commits):
                commit = item.get("commit") or {}
                message = (commit.get("message") or "commit").splitlines()[0]
                sha = (item.get("sha") or "unknown")[:7]
                author = (commit.get("author") or {}).get("name") or "unknown"
                row = Text(f"{sha}  {message}")
                row.append(f"  ·  {author}", style="dim")
                if index == selected:
                    row.stylize(f"bold on {self._c('row_selected')}")
                tree.append_text(row)
                tree.append("\n")
            selected_item = snapshot_commits[selected]
            selected_commit = selected_item.get("commit") or {}
            sha = (selected_item.get("sha") or "unknown")[:7]
            message = (selected_commit.get("message") or "commit").splitlines()[0]
            author = (selected_commit.get("author") or {}).get("name") or "unknown"
            files = selected_item.get("files") or []
            file_text = Text("Files changed\n", style=f"bold {self._c('primary')}")
            if files:
                for file in files:
                    file_text.append(f"{file.get('status', 'M'):>8}  {file.get('filename', 'unknown')}\n", style="dim")
            else:
                file_text.append("No file details returned by GitHub.\n", style="dim")
            right = Group(
                Text(f"Commit {sha}\n", style=self._c("primary")),
                Text(f"{message}\n", style="bold"),
                Text(f"@{author}  ·  {relative_time(selected_commit.get('committer', {}).get('date'))}  ·  {self.app.repository}\n", style="dim"),
                Panel(file_text, border_style=self._c("border")),
            )
            return Group(tree, Text(f"\n  {len(snapshot_commits)} commits loaded", style="dim")), right, self._status(
                f"Commit {selected + 1}/{len(snapshot_commits)}", "read-only", "loaded", self.app.repository or ""
            )
        tree = Text()
        tree.append("⌕  Filter files                         8 changed\n\n", style="dim")
        file_rows = [
            ("▾", "src", "", "primary", False),
            ("  ▾", "screens", "", "primary", False),
            ("    ", "main.py", "M  +84 -21", "warning", True),
            ("    ", "overview.py", "M  +31 -12", "warning", False),
            ("  ▾", "widgets", "", "primary", False),
            ("    ", "spinner.py", "M  +198 -46", "warning", False),
            ("    ", "app.py", "M  +16 -4", "warning", False),
            ("▾", "tests", "", "primary", False),
            ("    ", "test_loaders.py", "A  +41", "success", False),
            ("    ", "test_smoke.py", "M  +16 -0", "warning", False),
            ("  ", "README.md", "M  +12 -3", "warning", False),
            ("  ", "pyproject.toml", "M  +4 -1", "warning", False),
        ]
        selectable = [2, 3, 5, 6, 8, 9, 10, 11]
        selected = min(self._selection(), len(selectable) - 1)
        selected_row = selectable[selected]
        for index, (prefix, name, change, color, _initially_selected) in enumerate(file_rows):
            row = Text(f"{prefix} ")
            row.append(name, style=self._c("primary") if "▾" in prefix else "")
            if change:
                row.append(f"  {change}", style=self._c(color))
            if index == selected_row:
                row.stylize(f"bold on {self._c('row_selected')}")
            tree.append_text(row)
            tree.append("\n")
        left = Group(
            tree,
            Text("\n  8 files   +386 additions   -83 deletions", style="dim"),
        )

        head = Text()
        head.append("Commit 981dad2\n", style=self._c("primary"))
        head.append("feat: rebuild terminal workspaces\n", style="bold")
        head.append("@musa  ·  4m ago  ·  main  ·  signed ✓\n", style="dim")
        head.append("\n AHEAD 2 ", style=f"bold {self._c('background')} on {self._c('success')}")
        head.append("   behind 0   │   Files 8   │   +386 ", style="dim")
        head.append("-83\n", style=self._c("error"))
        head.append("\n◀ previous commit   1 / 8 files   next file ▶", style="dim")

        _prefix, filename, change, _color, _initially_selected = file_rows[selected_row]
        path = filename
        if selected_row in {2, 3}:
            path = f"src/screens/{filename}"
        elif selected_row in {5}:
            path = f"src/widgets/{filename}"
        elif selected_row == 6:
            path = f"src/{filename}"
        elif selected_row in {8, 9}:
            path = f"tests/{filename}"
        change_parts = change.split()
        additions = next((part for part in change_parts if part.startswith("+")), "+0")
        deletions = next((part for part in change_parts if part.startswith("-")), "-0")
        diff_header = Text(f"▣ {path}     ", style="bold")
        diff_header.append(additions, style=self._c("success"))
        diff_header.append(f"  {deletions}", style=self._c("error"))
        old = Text()
        new = Text()
        for number, code, style in (
            (26, "class MainScreen(Screen):", ""),
            (27, "    layout: vertical", ""),
            (28, f"    old implementation: {filename}", "error"),
            (29, "", ""),
            (30, "    def _load_section():", ""),
            (31, "        table.clear()", "error"),
            (32, "", ""),
        ):
            old.append(f"{number:>3}  {code}\n", style=self._c(style) if style else "dim")
        for number, code, style in (
            (26, "class MainScreen(Screen):", ""),
            (27, "    layout: vertical", ""),
            (28, f"    selected file: {filename}", "success"),
            (29, "    VerticalScroll(id='detail')", "success"),
            (30, "    def _render_workspace():", ""),
            (31, "        left, right = renderer()", "success"),
            (32, "        detail.update(right)", "success"),
        ):
            new.append(f"{number:>3}  {code}\n", style=self._c(style) if style else "dim")
        if self.size.width < 120:
            diff = Text()
            diff.append(f"@@ selected change in {filename} @@\n", style=self._c("primary"))
            diff.append("-     old implementation\n", style=self._c("error"))
            diff.append(f"+     selected file: {filename}\n", style=self._c("success"))
            diff.append("+     render responsive detail pane\n", style=self._c("success"))
            diff.append("      preserve keyboard selection\n", style="dim")
        else:
            side_by_side = _grid(1, 1, padding=(0, 1))
            side_by_side.add_row(old, new)
            diff = side_by_side
        right = Group(
            head,
            Text("\n"),
            Panel(diff, title=diff_header, border_style=self._c("border")),
        )
        status = self._status(
            "Commit 981dad2",
            "ahead 2 · behind 0",
            f"file {selected + 1}/{len(selectable)}",
            f"{additions} {deletions}",
        )
        return left, right, status

    def _status(self, *items: str) -> Text:
        result = Text()
        visible_items = items[:2] if self.size.width < 110 else items
        for index, item in enumerate(visible_items):
            if index:
                result.append("  ·  ", style="dim")
            result.append(item, style=self._c("primary") if index == 0 else "dim")
        controls = (
            "   [j/k] select  [enter] detail  [e] edit  [esc] done  [q] quit"
            if self.size.width < 110
            else "     [j/k] select  [enter] detail  [e] edit  [esc] done  [ctrl+s] local save  [tab] section  [o] overview  [q] quit"
        )
        result.append(controls, style="dim")
        if self.app.data_loading:
            result.append("   ·   loading GitHub…", style=self._c("primary"))
        elif self.app.data_error:
            result.append("   ·   gh unavailable (local preview)", style=self._c("warning"))
        return result

    def _set_section(self, section: int) -> None:
        self._save_comment_draft()
        editor = self.query_one("#comment-editor", CommentEditor)
        if editor.has_focus:
            editor.blur()
        self._section = section % len(SECTIONS)
        if self.has_class("single-pane"):
            self._show_pane("list")
        self._render_header()
        self._begin_section_load()

    def _begin_section_load(self) -> None:
        if self._load_timer is not None:
            self._load_timer.stop()
        self._load_frame = 0
        self._render_section_loader()
        self._load_timer = self.set_interval(0.08, self._tick_section_load)

    def _tick_section_load(self) -> None:
        self._load_frame += 1
        self._render_section_loader()
        if self._load_frame >= 7:
            self._load_timer.stop()
            self._load_timer = None
            self._render_workspace()

    def _render_section_loader(self) -> None:
        tasks = [
            ("Fetching pull requests", "fetch", "gh-flow prs"),
            ("Loading issue conversation", "fetch", "gh-flow issues"),
            ("Reading workflow runs", "sync", "gh-flow ci"),
            ("Syncing repositories", "sync", "gh-flow repos"),
            ("Building file diff", "build", "gh-flow commits"),
        ]
        label, kind, command = tasks[self._section]
        content = inline_loader(
            label,
            self._load_frame,
            kind=kind,
            color=self._c("primary"),
            command=command,
        )
        content.append("  ")
        bar_width = min(28, max(8, self.size.width - content.cell_len - 4))
        content.append_text(
            indeterminate_bar(self._load_frame, width=bar_width, color=self._c("primary"))
        )
        self.query_one("#status", Static).update(content)

    def action_next_section(self) -> None:
        self._set_section(self._section + 1)

    def action_prev_section(self) -> None:
        self._set_section(self._section - 1)

    def action_selection_down(self) -> None:
        self._save_comment_draft()
        count = self._item_counts[self._section]
        self._selected[self._section] = (self._selection() + 1) % count
        self._render_workspace()

    def action_selection_up(self) -> None:
        self._save_comment_draft()
        count = self._item_counts[self._section]
        self._selected[self._section] = (self._selection() - 1) % count
        self._render_workspace()

    def _show_pane(self, pane: str) -> None:
        self._pane = pane
        self.remove_class("list-pane", "detail-pane")
        self.add_class(f"{pane}-pane")

    def action_open_detail(self) -> None:
        self._show_pane("detail")

    def action_focus_comment(self) -> None:
        if self._section not in {0, 1}:
            return
        self._show_pane("detail")
        editor = self.query_one("#comment-editor", CommentEditor)
        editor.can_focus = True
        editor.focus()

    def action_save_comment(self) -> None:
        if self._section not in {0, 1}:
            return
        self._save_comment_draft()
        self.notify("Draft saved locally · nothing sent to GitHub", timeout=1.5)

    def action_insert_mention(self) -> None:
        if self._section not in {0, 1}:
            return
        self.action_focus_comment()
        editor = self.query_one("#comment-editor", CommentEditor)
        if self._complete_mention(editor):
            return
        mention = LOCAL_MENTIONS[self._mention_index % len(LOCAL_MENTIONS)]
        self._mention_index += 1
        editor.insert(mention)

    def _complete_mention(self, editor: TextArea) -> bool:
        """Replace the @fragment at the cursor, returning whether one was found."""
        row, column = editor.cursor_location
        line = editor.document.get_line(row)
        start = column
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_-"):
            start -= 1
        has_fragment = start > 0 and line[start - 1] == "@"
        if has_fragment:
            start -= 1
            fragment = line[start:column].lower()
            matches = [mention for mention in LOCAL_MENTIONS if mention.startswith(fragment)]
            mention = matches[0] if matches else LOCAL_MENTIONS[0]
            editor.replace(mention, (row, start), (row, column))
            return True
        return False

    def action_back_to_list(self) -> None:
        editor = self.query_one("#comment-editor", TextArea)
        if editor.has_focus:
            editor.blur()
            editor.can_focus = False
            return
        if self.has_class("single-pane") and self._pane == "detail":
            self._show_pane("list")

    def action_focus_right(self) -> None:
        if self.has_class("single-pane") and self._pane == "list":
            self._show_pane("detail")
        else:
            self.action_next_section()

    def action_focus_left(self) -> None:
        if self.has_class("single-pane") and self._pane == "detail":
            self._show_pane("list")
        else:
            self.action_prev_section()

    def action_section_1(self) -> None:
        self._set_section(0)

    def action_section_2(self) -> None:
        self._set_section(1)

    def action_section_3(self) -> None:
        self._set_section(2)

    def action_section_4(self) -> None:
        self._set_section(3)

    def action_section_5(self) -> None:
        self._set_section(4)

    def action_overview(self) -> None:
        from screens.overview import OverviewScreen

        self.app.push_screen(OverviewScreen())

    def action_settings(self) -> None:
        from screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())
