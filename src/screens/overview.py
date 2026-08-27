"""OverviewScreen — the main dashboard (default landing screen).

Sidebar (brand + menu + shortcuts + status) | header + stat cards + recent activity,
CI status, recent failure, PR list, repo health, quick actions. UI only (mock data).

On load it runs a brief loader, then reveals the panels with a staggered eased fade-in.
"""

from __future__ import annotations

from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from screens.pull_requests import HomeScreen
from screens.settings import SettingsScreen
from themes.palettes import ACCENT_BLUE as BLUE
from themes.palettes import GREEN, RED, YELLOW
from widgets.bar_chart import BarChart

CYAN = "#56D4DD"
MAGENTA = "#C586E0"


# --- small helpers -----------------------------------------------------------


def _grid(*ratios: int) -> Table:
    """An expanding, borderless grid with the given column count."""
    t = Table.grid(expand=True, padding=(0, 1))
    for _ in ratios:
        t.add_column()
    return t


class Panel(Vertical):
    """A bordered box with a title in its border."""

    def __init__(self, title: str, renderable, **kw) -> None:
        self._title = title
        self._renderable = renderable
        super().__init__(**kw)

    def compose(self) -> ComposeResult:
        if isinstance(self._renderable, Widget):
            yield self._renderable
        else:
            yield Static(self._renderable)

    def on_mount(self) -> None:
        self.border_title = self._title


# --- screen ------------------------------------------------------------------


class OverviewScreen(Screen):
    DEFAULT_CSS = """
    OverviewScreen { background: $background; layout: vertical; }

    #ov-body { height: 1fr; }

    #sidebar { width: 34; padding: 0; }
    #sidebar #brand { height: 5; border: round $border-dim; padding: 0 1; content-align: left middle; }
    #sidebar #menu { height: auto; border: round $border-dim; padding: 0 1; background: $background; }
    #sidebar #shortcuts { height: auto; border: round $border-dim; padding: 0 1; }
    #sidebar #statusp { height: 1fr; border: round $border-dim; padding: 0 1; }

    #menu > .option-list--option-highlighted { background: $primary; color: $background; text-style: bold; }
    #menu > .option-list--option-highlighted-hover { background: $primary; color: $background; }

    #main { width: 1fr; }
    #topbar { height: 1; padding: 0 1; }
    #stats { height: 4; }
    #stats .card { width: 1fr; border: round $border-dim; padding: 0 1; }

    #panels { height: 1fr; }
    #center { width: 3fr; }
    #right { width: 2fr; }
    .panel { height: auto; border: round $border-dim; padding: 0 1; border-title-align: left; }
    .panel Static { padding: 0; }
    .grow { height: 1fr; }
    #activity { height: 9; }
    #failure { border: round $error; }

    #footer { dock: bottom; height: 1; padding: 0 1; color: $text-muted; }
    """

    BINDINGS = [
        ("enter", "open_selected", "Open"),
        ("left", "focus_previous", "Prev panel"),
        ("right", "focus_next", "Next panel"),
        ("g", "settings", "Settings"),
    ]

    # ---- compose ----

    def compose(self) -> ComposeResult:
        with Horizontal(id="ov-body"):
            with Vertical(id="sidebar"):
                yield Static(self._brand(), id="brand")
                yield self._menu()
                yield Static(self._shortcuts(), id="shortcuts")
                yield Static(self._status_panel(), id="statusp")
            with Vertical(id="main"):
                yield Static(self._topbar(), id="topbar")
                with Horizontal(id="stats"):
                    yield from self._stat_cards()
                with Horizontal(id="panels"):
                    with Vertical(id="center"):
                        yield Panel(
                            "ACTIVITY  ·  commits / week",
                            self._activity_chart(),
                            classes="panel animate",
                            id="activity",
                        )
                        yield Panel(
                            "RECENT ACTIVITY",
                            self._recent_activity(),
                            classes="panel animate grow",
                            id="recent",
                        )
                        yield Panel(
                            "ACTIONS / CI STATUS",
                            self._ci_status(),
                            classes="panel animate",
                            id="ci",
                        )
                        yield Panel(
                            "RECENT FAILURE: Backend Tests #9182",
                            self._failure(),
                            classes="panel animate",
                            id="failure",
                        )
                    with Vertical(id="right"):
                        yield Panel(
                            "PULL REQUESTS (7)",
                            self._pr_list(),
                            classes="panel animate grow",
                            id="prs",
                        )
                        yield Panel(
                            "REPOSITORY HEALTH",
                            self._health(),
                            classes="panel animate",
                            id="health",
                        )
                        yield Panel(
                            "QUICK ACTIONS",
                            self._quick_actions(),
                            classes="panel animate",
                            id="quick",
                        )
        yield Static(self._footer(), id="footer")

    # ---- lifecycle + animation ----

    def on_mount(self) -> None:
        self.query_one("#menu", OptionList).highlighted = 0
        panels = list(self.query(".animate"))
        for i, panel in enumerate(panels):
            panel.styles.opacity = 0.0
            panel.styles.animate("opacity", 1.0, duration=0.3, delay=0.02 * i, easing="out_cubic")

    # ---- actions ----

    def action_open_selected(self) -> None:
        menu = self.query_one("#menu", OptionList)
        if menu.highlighted is None:
            return
        self._route(menu.get_option_at_index(menu.highlighted).id)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._route(event.option.id)

    def action_settings(self) -> None:
        self.app.push_screen(SettingsScreen())

    def _route(self, option_id: str | None) -> None:
        if option_id == "pull_requests":
            self.app.push_screen(HomeScreen())
        elif option_id == "settings":
            self.app.push_screen(SettingsScreen())
        elif option_id == "quit":
            self.app.exit()

    # ---- sidebar builders ----

    def _brand(self) -> Text:
        t = Text()
        t.append("gh", style=f"bold {BLUE}")
        t.append("-flow", style="bold")
        t.append("   v0.1.0\n", style="dim")
        t.append("Your entire GitHub workflow,\n", style="dim")
        t.append("without leaving the terminal.", style="dim")
        return t

    def _menu(self) -> OptionList:
        items = [
            ("overview", "▦", "Overview", ""),
            ("repositories", "▤", "Repositories", ""),
            ("branches", "⎇", "Branches", ""),
            ("commits", "●", "Commits", ""),
            ("pull_requests", "⇄", "Pull Requests", ""),
            ("reviews", "▷", "Reviews (Inbox)", "2"),
            ("issues", "◷", "Issues", "7"),
            ("actions", "◉", "Actions / CI", "1"),
            ("deployments", "⬆", "Deployments", "●"),
            ("releases", "⊛", "Releases", "3"),
            ("search", "⌕", "Search", "/"),
            ("settings", "⚙", "Settings", ""),
            ("quit", "⏻", "Quit", "q"),
        ]
        options = []
        for oid, icon, label, right in items:
            row = Text()
            row.append(f"{icon}  {label}")
            if right:
                pad = max(1, 26 - row.cell_len - len(right))
                row.append(" " * pad)
                style = "dim" if right in ("/", "q") else RED
                row.append(right, style=GREEN if right == "●" else style)
            options.append(Option(row, id=oid))
        menu = OptionList(*options, id="menu")
        return menu

    def _shortcuts(self) -> Table:
        g = _grid(1, 2)
        g.add_row(Text("ctrl + p", style=CYAN), Text("Command Palette", style="dim"))
        g.add_row(Text("/", style=CYAN), Text("Global Search", style="dim"))
        g.add_row(Text("?", style=CYAN), Text("Help", style="dim"))
        g.add_row(Text("q", style=CYAN), Text("Quit gh-flow", style="dim"))
        return g

    def _status_panel(self) -> Table:
        g = _grid(1, 2)
        g.add_row(Text("GitHub", style="dim"), Text("✓ Connected", style=GREEN))
        g.add_row(Text("Repo", style="dim"), Text("musa/my-app"))
        g.add_row(Text("Branch", style="dim"), Text("main", style=GREEN))
        g.add_row(Text("Ahead", style="dim"), Text("0"))
        g.add_row(Text("Behind", style="dim"), Text("0"))
        g.add_row(Text("Workspace", style="dim"), Text("~/projects/my-app", style="dim"))
        return g

    # ---- main builders ----

    def _topbar(self) -> Table:
        g = _grid(1, 1)
        left = Text()
        left.append("Repository: ", style="dim")
        left.append("musa/my-app", style=BLUE)
        left.append("      Branch: ", style="dim")
        left.append("main", style=GREEN)
        left.append("      Status: ", style="dim")
        left.append("Clean", style=GREEN)
        right = Text("Sun 25 May 2025   11:42 PM", style="dim", justify="right")
        g.add_row(left, right)
        return g

    def _stat_cards(self):
        cards = [
            ("PULL REQUESTS", "dim", [("4", "Open", GREEN), ("2", "Review", YELLOW)]),
            ("ISSUES", "dim", [("7", "Open", GREEN), ("3", "Assigned", YELLOW)]),
            ("ACTIONS", BLUE, [("1", "Failed", RED), ("2", "Running", YELLOW)]),
            ("DEPLOYMENTS", "dim", [("2", "Active", GREEN), ("1", "Healthy", GREEN)]),
            ("NOTIFICATIONS", "dim", [("3", "Unread", MAGENTA)]),
            ("RELEASES", "dim", [("3", "Published", GREEN), ("1", "Draft", YELLOW)]),
        ]
        for title, tstyle, rows in cards:
            t = Text()
            t.append(title + "\n", style=tstyle)
            for i, (num, label, style) in enumerate(rows):
                if i:
                    t.append("\n")
                t.append(f"{num} ", style=f"bold {style}")
                t.append(label, style="dim")
            yield Static(t, classes="card animate")

    def _activity_chart(self) -> BarChart:
        # mock weekly commit counts (52 weeks); deterministic, no RNG
        values = [3 + (i * 7 + 5) % 11 + (i * i) % 4 for i in range(52)]
        highlight = 27
        values[highlight] = 42
        return BarChart(
            values,
            height=5,
            highlight=highlight,
            left_label="Sep 2023",
            right_label="Sep 2024",
        )

    def _recent_activity(self) -> Table:
        rows = [
            ("✗", RED, "Backend Tests workflow failed", "#9182", "4m ago"),
            ("✓", GREEN, "Merge pull request #140 from feat/dashboard", "main", "18m ago"),
            ("✎", BLUE, "Update README.md", "main", "38m ago"),
            ("✗", RED, "Database migration: Add user_sessions table", "#141 develop", "1h ago"),
            ("⬆", BLUE, "Deploy to Production", "main", "2h ago"),
            ("✎", BLUE, "Fix payment retry logic", "#139 feat/payments", "3h ago"),
            ("✓", GREEN, "Bump dependencies", "main", "5h ago"),
            ("✎", GREEN, "feat: Add usage analytics", "#138 feat/analytics", "6h ago"),
            ("✓", GREEN, "Merge pull request #137 from fix/mobile", "main", "8h ago"),
            ("✎", BLUE, "Refactor auth middleware", "#136 feat/auth", "10h ago"),
            ("⬆", BLUE, "Deploy Preview #142", "feat/oauth", "11h ago"),
            ("✓", GREEN, "Tag release v2.4.0", "main", "12h ago"),
            ("✎", BLUE, "Update dependencies lockfile", "main", "14h ago"),
            ("✗", RED, "E2E flake on checkout step", "#134 develop", "16h ago"),
            ("✓", GREEN, "Cache CI node_modules", "main", "18h ago"),
            ("✎", GREEN, "docs: expand contributing guide", "#133 docs", "1d ago"),
            ("✓", GREEN, "Merge pull request #132 from feat/search", "main", "1d ago"),
            ("⬆", BLUE, "Deploy to Staging", "develop", "1d ago"),
            ("✎", BLUE, "Add rate limiting to API", "#131 feat/api", "2d ago"),
            ("✗", RED, "Lint failed on feature branch", "#130 feat/ui", "2d ago"),
            ("✓", GREEN, "Bump actions/checkout to v4", "main", "2d ago"),
            ("✎", GREEN, "test: add coverage for auth", "#129 tests", "3d ago"),
            ("✓", GREEN, "Merge pull request #128 from chore/deps", "main", "3d ago"),
            ("⬆", BLUE, "Rollback Production to v2.3.1", "main", "3d ago"),
        ]
        g = _grid(1, 1, 1)
        g.columns[1].justify = "left"
        g.columns[2].justify = "right"
        for icon, color, text, ref, when in rows:
            line = Text()
            line.append(f"{icon} ", style=color)
            line.append(text)
            g.add_row(line, Text(ref, style="dim"), Text(when, style="dim"))
        return g

    def _ci_status(self) -> Table:
        rows = [
            ("✗", "Backend Tests", "main", "Failed", RED, "4m 12s", "4m ago"),
            ("◉", "Lint & Format", "main", "Passed", GREEN, "1m 03s", "6m ago"),
            ("◉", "E2E Tests", "feat/oauth", "Passed", GREEN, "5m 41s", "12m ago"),
            ("◉", "Build & Package", "main", "Passed", GREEN, "2m 21s", "16m ago"),
            ("◉", "Deploy Preview", "feat/oauth", "Running", YELLOW, "3m 11s", "17s ago"),
            ("◉", "Security Scan", "main", "Passed", GREEN, "1m 34s", "18m ago"),
        ]
        t = Table(expand=True, box=None, pad_edge=False, header_style="dim")
        t.add_column("WORKFLOW", ratio=3)
        t.add_column("BRANCH", ratio=2)
        t.add_column("STATUS", ratio=2)
        t.add_column("DURATION", ratio=1, justify="right")
        t.add_column("UPDATED", ratio=1, justify="right")
        for icon, wf, branch, status, color, dur, when in rows:
            name = Text(f"{icon} {wf}", style=color if status == "Failed" else "")
            st = Text()
            st.append(
                "✓ " if status == "Passed" else ("✗ " if status == "Failed" else "◉ "), style=color
            )
            st.append(status, style=color)
            t.add_row(
                name, Text(branch, style="dim"), st, Text(dur, style="dim"), Text(when, style="dim")
            )
        return t

    def _failure(self) -> Text:
        t = Text()
        t.append("tests/auth/test_oauth.py::test_google_login\n")
        t.append("AssertionError: ", style=f"bold {RED}")
        t.append("assert 401 == 200\n", style=RED)
        t.append("    + where 401 = <Response [401 Unauthorized]>.status_code\n", style="dim")
        t.append("src/auth/oauth.py:84\n\n", style=BLUE)
        t.append("[l]", style=CYAN)
        t.append(" View Logs    ", style="dim")
        t.append("[r]", style=CYAN)
        t.append(" Retry    ", style="dim")
        t.append("[c]", style=CYAN)
        t.append(" Copy Error    ", style="dim")
        t.append("[o]", style=CYAN)
        t.append(" Open in Editor", style="dim")
        return t

    def _pr_list(self) -> Table:
        prs = [
            (
                "#142",
                "Add Google OAuth login",
                "feat/oauth → main",
                "✓ 2/2 checks",
                "• 2 reviews",
                "4m",
            ),
            (
                "#141",
                "Improve dashboard charts",
                "feat/dashboard → main",
                "✓ 6/6 checks",
                "• 1 review",
                "1h",
            ),
            (
                "#140",
                "Fix mobile layout issues",
                "fix/mobile → main",
                "✓ 6/6 checks",
                "• 2 reviews",
                "18m",
            ),
            (
                "#139",
                "Payment retry mechanism",
                "fix/payment → main",
                "✓ 6/6 checks",
                "✓ Approved",
                "3h",
            ),
            (
                "#138",
                "Add usage analytics",
                "feat/analytics → main",
                "✓ 4/4 checks",
                "• 1 review",
                "6h",
            ),
            (
                "#137",
                "Refactor auth middleware",
                "feat/auth → main",
                "✗ 5/6 checks",
                "• 3 reviews",
                "8h",
            ),
            (
                "#136",
                "Search across everything",
                "feat/search → main",
                "✓ 8/8 checks",
                "✓ Approved",
                "1d",
            ),
        ]
        g = _grid(1, 1)
        g.columns[1].justify = "right"
        for num, title, branch, checks, reviews, when in prs:
            block = Text()
            block.append(f"{num}  ", style=BLUE)
            block.append(f"{title}\n")
            block.append(f"    {branch}\n", style="dim")
            block.append("    ")
            block.append(checks + "   ", style=GREEN if checks.startswith("✓") else RED)
            block.append(reviews, style="dim")
            g.add_row(block, Text(when, style="dim"))
            g.add_row(Text(""), Text(""))
        return g

    def _health(self) -> Table:
        g = _grid(1, 3)
        g.add_row(Text("A-", style=f"bold {GREEN}"), Text(""))
        g.add_row(Text("Lines of Code", style="dim"), self._metric("24,312", "+324", GREEN))
        g.add_row(Text("Test Coverage", style="dim"), self._metric("87%", "+2%", GREEN))
        g.add_row(Text("Open Issues", style="dim"), self._metric("7", "-3", GREEN))
        g.add_row(Text("Open PRs", style="dim"), self._metric("4", "-1", GREEN))
        g.add_row(Text("Last updated: just now", style="dim"), Text(""))
        return g

    def _metric(self, value: str, delta: str, delta_style: str) -> Text:
        t = Text(justify="right")
        t.append(value + "   ")
        t.append(delta, style=delta_style)
        return t

    def _quick_actions(self) -> Text:
        actions = [
            ("c", "Create Pull Request"),
            ("b", "Create Branch"),
            ("w", "Run Workflow"),
            ("d", "Deploy"),
            ("n", "New Issue"),
            ("s", "Search Everything"),
        ]
        t = Text()
        for i, (key, label) in enumerate(actions):
            if i:
                t.append("\n")
            t.append(f"[{key}]", style=CYAN)
            t.append(f" {label}", style="dim")
        return t

    def _footer(self) -> Table:
        g = _grid(1, 1)
        left = Text()
        left.append("Press ", style="dim")
        left.append("?", style=CYAN)
        left.append(" for help     Ctrl+p", style="dim")
        left.append("", style=CYAN)
        left.append(" for command palette     ", style="dim")
        left.append("/", style=CYAN)
        left.append(" for search", style="dim")
        right = Text(justify="right")
        right.append("gh-flow 0.1.0    ", style="dim")
        right.append("https://github.com/musaJawad004/gh-tui", style="dim")
        g.add_row(left, right)
        return g
