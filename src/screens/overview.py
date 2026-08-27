"""Reference-style gh-flow dashboard.

This is the default landing view: a dense, terminal-native repository overview with
activity, pull requests, CI and deployment status visible at once.
"""

from __future__ import annotations

from datetime import datetime

from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from themes.palettes import active_colors
from widgets.spinner import indeterminate_bar, inline_loader


def _grid(*ratios: int, padding: tuple[int, int] = (0, 1)) -> Table:
    table = Table.grid(expand=True, padding=padding)
    for ratio in ratios:
        table.add_column(ratio=ratio)
    return table


class DashboardPanel(Vertical):
    """A compact bordered dashboard panel with title text in its top rule."""

    def __init__(self, title: str, renderable, subtitle: str | None = None, **kwargs) -> None:
        self._title = title
        self._subtitle = subtitle
        self._renderable = renderable
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Static(self._renderable)

    def on_mount(self) -> None:
        self.border_title = self._title
        if self._subtitle:
            self.border_subtitle = self._subtitle


class OverviewScreen(Screen):
    DEFAULT_CSS = """
    OverviewScreen {
        layout: vertical;
        background: $background;
        color: $foreground;
        padding: 0 1;
    }

    OverviewScreen #masthead {
        height: 3;
        padding: 0 1;
        content-align: left middle;
        border-bottom: solid $border-dim;
    }
    OverviewScreen #repo-summary {
        height: 3;
        padding: 0 1;
        content-align: left middle;
        border-bottom: solid $border-dim;
    }

    OverviewScreen #activity {
        height: 1fr;
        min-height: 11;
        padding: 1 1 0 1;
    }
    OverviewScreen #activity-title { height: 2; }
    OverviewScreen #activity-list { height: 1fr; }

    OverviewScreen #panels {
        height: 15;
        min-height: 11;
    }
    OverviewScreen .dashboard-panel {
        height: 100%;
        border: round $border-dim;
        border-title-color: $primary;
        border-title-align: left;
        border-subtitle-color: $text-muted;
        border-subtitle-align: right;
        padding: 0 1;
    }
    OverviewScreen .dashboard-panel Static { height: 1fr; }
    OverviewScreen #prs-panel { width: 43%; margin-right: 1; }
    OverviewScreen #ci-panel { width: 27%; margin-right: 1; }
    OverviewScreen #deploy-panel { width: 30%; }

    OverviewScreen #quick-panel {
        height: 4;
        min-height: 3;
        margin-top: 1;
    }
    OverviewScreen #command-line {
        height: 3;
        margin-top: 1;
        border: round $border-dim;
        padding: 0 1;
        content-align: left middle;
    }
    OverviewScreen #footer {
        height: 2;
        padding: 0 1;
        color: $text-muted;
        content-align: left middle;
    }
    """

    BINDINGS = [
        ("p", "goto_pull_requests", ""),
        ("i", "goto_issues", ""),
        ("c", "goto_actions", ""),
        ("d", "goto_deployments", ""),
        ("b", "goto_branches", ""),
        ("l", "goto_releases", ""),
        ("s", "goto_settings", ""),
        ("r", "refresh_dashboard", "Refresh"),
        ("slash", "commands", "Commands"),
        ("j", "noop", ""),
        ("k", "noop", ""),
    ]

    def compose(self) -> ComposeResult:
        yield Static(self._masthead(), id="masthead")
        yield Static(self._repo_summary(), id="repo-summary")
        with Vertical(id="activity"):
            yield Static(self._activity_title(), id="activity-title")
            yield Static(self._activity(), id="activity-list")
        with Horizontal(id="panels"):
            yield DashboardPanel(
                "pull requests (4 open)", self._pull_requests(), "(p) view all",
                id="prs-panel", classes="dashboard-panel",
            )
            yield DashboardPanel(
                "ci / workflows", self._workflows(), "(c) view all",
                id="ci-panel", classes="dashboard-panel",
            )
            yield DashboardPanel(
                "deployments", self._deployments(), "(d) view all",
                id="deploy-panel", classes="dashboard-panel",
            )
        yield DashboardPanel(
            "quick commands", self._quick_commands(),
            id="quick-panel", classes="dashboard-panel",
        )
        yield Static(self._command_line(), id="command-line")
        yield Static(self._footer(), id="footer")

    def on_mount(self) -> None:
        self._refresh_frame = 0
        self._refresh_timer = None

    def _c(self, name: str) -> str:
        return active_colors(self.app)[name]

    def refresh_theme(self) -> None:
        self.refresh(recompose=True)

    def _masthead(self) -> Table:
        table = _grid(3, 2)
        left = Text()
        left.append("gh-flow", style=f"bold {self._c('success')}")
        left.append("  v0.1.0        ", style="dim")
        left.append("⑂  ", style="bold")
        left.append("musa/my-app", style=self._c("primary"))
        left.append("      main", style=self._c("success"))
        left.append("  ↑2", style="dim")

        now = datetime.now().astimezone()
        right = Text(justify="right")
        right.append("clean", style=f"bold {self._c('success')}")
        right.append("   │   ", style="dim")
        right.append(now.strftime("%a %d %b %Y  %I:%M %p"), style="dim")
        table.add_row(left, right)
        return table

    def _repo_summary(self) -> Table:
        table = _grid(3, 3, 3, 9)
        repo = Text("repo:  ", style="dim")
        repo.append("musa/my-app", style=self._c("primary"))
        branch = Text("branch:  ", style="dim")
        branch.append("main", style=self._c("success"))
        branch.append("  ↑2", style="dim")
        status = Text("status:  ", style="dim")
        status.append("clean", style=self._c("success"))

        counts = Text(justify="right")
        for label, value, color in (
            ("PR", "4 open", "primary"), ("Issues", "7", "warning"),
            ("CI", "✕ 1", "error"), ("Deploy", "2", "success"),
            ("Releases", "3", "primary"),
        ):
            if counts:
                counts.append("  ·  ", style="dim")
            counts.append(f"{label} ", style="dim")
            counts.append(value, style=self._c(color))
        table.add_row(repo, branch, status, counts)
        return table

    def _activity_title(self) -> Table:
        table = _grid(1, 1, padding=(0, 0))
        table.add_row(
            Text("recent activity  ───", style=self._c("primary")),
            Text("(r) refresh", style="dim", justify="right"),
        )
        return table

    def _activity(self) -> Table:
        rows = [
            ("×", "error", "4m", "backend-tests workflow failed", "#9182", "workflow"),
            ("✓", "success", "18m", "merge pull request #140 from feat/dashboard", "main", ""),
            ("✓", "success", "38m", "update README.md", "main", ""),
            ("!", "warning", "1h", "database migration: add user_sessions table", "#141", "develop"),
            ("→", "success", "2h", "deploy to production", "main", "deploy"),
            ("✓", "success", "3h", "fix payment retry logic", "#139", "feat/payments"),
            ("✓", "success", "5h", "bump dependencies", "main", ""),
            ("✓", "success", "6h", "feat: add usage analytics", "#138", "feat/analytics"),
        ]
        table = _grid(1, 2, 13, 2, 3, padding=(0, 1))
        for icon, color, age, event, ref, kind in rows:
            table.add_row(
                Text(icon, style=self._c(color)), Text(age, style="dim"),
                Text(event, overflow="ellipsis", no_wrap=True),
                Text(ref, style="dim", justify="right"), Text(kind, style="dim"),
            )
        return table

    def _pull_requests(self) -> Table:
        rows = [
            ("#142", "Add Google OAuth login", "feat/oauth", "2/2 ✓", "4m ago"),
            ("#141", "Improve dashboard charts", "feat/dashboard", "6/6 ✓", "1h ago"),
            ("#140", "Fix mobile layout issues", "fix/mobile", "6/6 ✓", "18m ago"),
            ("#139", "Payment retry mechanism", "fix/payment", "6/6 ✓", "3h ago"),
        ]
        table = _grid(6, 2, 3, padding=(0, 0))
        for number, title, branch, checks, age in rows:
            left = Text(no_wrap=True, overflow="ellipsis")
            left.append(f"{number}  ", style=self._c("primary"))
            left.append(title)
            right = Text(justify="right", no_wrap=True, overflow="ellipsis")
            right.append(checks + "  ", style=self._c("success"))
            right.append(age, style="dim")
            table.add_row(
                left,
                Text(branch, style="dim", no_wrap=True, overflow="ellipsis"),
                right,
            )
        table.add_row(Text("› more...", style="dim"), "", "")
        return table

    def _workflows(self) -> Table:
        rows = [
            ("×", "error", "backend-tests", "4m 12s"),
            ("✓", "success", "lint & format", "1m 03s"),
            ("✓", "success", "e2e tests", "5m 41s"),
            ("✓", "success", "build & package", "2m 21s"),
            ("○", "warning", "deploy preview", "running"),
            ("✓", "success", "security scan", "1m 34s"),
        ]
        table = _grid(1, 7, 3, padding=(0, 0))
        for icon, color, name, value in rows:
            table.add_row(
                Text(icon, style=self._c(color)), Text(name),
                Text(value, style=self._c("warning") if value == "running" else "dim", justify="right"),
            )
        return table

    def _deployments(self) -> Table:
        rows = [
            ("●", "success", "production", "main", "2h ago", "✓"),
            ("○", "success", "staging", "develop", "6h ago", "✓"),
            ("○", "warning", "preview", "#142", "running", "•••"),
            ("○", "warning", "preview", "#141", "12m ago", "–"),
        ]
        table = _grid(1, 4, 3, 3, 2, padding=(0, 0))
        for icon, color, env, branch, age, result in rows:
            table.add_row(
                Text(icon, style=self._c(color)), Text(env), Text(branch, style="dim"),
                Text(age, style=self._c("warning") if age == "running" else "dim"),
                Text(result, style=self._c(color), justify="right"),
            )
        return table

    def _quick_commands(self) -> Text:
        result = Text(justify="center")
        for key, label in (
            ("/", "search"), ("p", "prs"), ("i", "issues"), ("c", "ci"),
            ("d", "deploys"), ("b", "branches"), ("l", "releases"),
            ("s", "settings"), ("q", "quit"),
        ):
            result.append(f"  {key}  ", style="bold")
            result.append(f"{label}    ", style="dim")
        return result

    def _command_line(self) -> Table:
        table = _grid(1, 1, padding=(0, 0))
        prompt = Text(": ", style=f"bold {self._c('primary')}")
        prompt.append("█", style="bold")
        table.add_row(prompt, Text("type ‘/’ for commands", style="dim", justify="right"))
        return table

    def _footer(self) -> Text:
        result = Text()
        for key, label in (
            ("j/k", "move"), ("enter", "open"), ("r", "refresh"),
            ("/", "commands"), ("q", "quit"),
        ):
            result.append(f"[{key}] {label}   ", style="dim")
        return result

    def _goto_section(self, section: int) -> None:
        from screens.main import MainScreen

        self.app.push_screen(MainScreen(section=section))

    def action_goto_pull_requests(self) -> None:
        self._goto_section(0)

    def action_goto_issues(self) -> None:
        self._goto_section(1)

    def action_goto_actions(self) -> None:
        self._goto_section(2)

    def action_goto_deployments(self) -> None:
        self.notify("Deployments · production and staging are healthy")

    def action_goto_branches(self) -> None:
        self.notify("Branches · main is 2 commits ahead")

    def action_goto_releases(self) -> None:
        self.notify("Releases · 3 published")

    def action_goto_settings(self) -> None:
        from screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_commands(self) -> None:
        self.app.action_help()

    def action_noop(self) -> None:
        pass

    def action_refresh_dashboard(self) -> None:
        if self._refresh_timer is not None:
            return
        self._refresh_frame = 0
        self._refresh_timer = self.set_interval(0.08, self._tick_refresh)

    def _tick_refresh(self) -> None:
        self._refresh_frame += 1
        loading = Text()
        loading.append("\n  ")
        loading.append_text(
            inline_loader(
                "Refreshing repository activity",
                self._refresh_frame,
                kind="refresh",
                color=self._c("primary"),
                command="gh-flow refresh",
            )
        )
        loading.append("\n\n  ")
        loading.append_text(
            indeterminate_bar(self._refresh_frame, width=42, color=self._c("primary"))
        )
        self.query_one("#activity-list", Static).update(loading)
        if self._refresh_frame >= 10:
            self._refresh_timer.stop()
            self._refresh_timer = None
            self.query_one("#activity-list", Static).update(self._activity())
            self.notify("Dashboard refreshed", timeout=1.5)
