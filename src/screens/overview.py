"""OverviewScreen — the gh-flow dashboard (default landing view).

Clean, spacious layout: status line, stat cards with icons, MAIN MENU + RECENT ACTIVITY,
then PULL REQUESTS / ACTIONS·CI / REPOSITORY HEALTH, a command-palette line and a footer.
UI only (mock data). Menu items (and their shortcut letters) route to focused section views.
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

from themes.palettes import active_colors

# section id -> MainScreen section index
SECTION_ROUTE = {"pull_requests": 0, "issues": 1, "actions": 2, "repositories": 3, "commits": 4}


def _grid(*cols: int) -> Table:
    t = Table.grid(expand=True, padding=(0, 1))
    for _ in cols:
        t.add_column()
    return t


class Panel(Vertical):
    """Bordered box with a blue title (and optional 'view all' subtitle)."""

    def __init__(self, title: str, renderable, subtitle: str | None = None, **kw) -> None:
        self._title = title
        self._subtitle = subtitle
        self._renderable = renderable
        super().__init__(**kw)

    def compose(self) -> ComposeResult:
        if isinstance(self._renderable, Widget):
            yield self._renderable
        else:
            yield Static(self._renderable)

    def on_mount(self) -> None:
        self.border_title = self._title
        if self._subtitle:
            self.border_subtitle = self._subtitle


class OverviewScreen(Screen):
    DEFAULT_CSS = """
    OverviewScreen { layout: vertical; background: $background; }

    #topbar { height: 1; padding: 0 2; }

    #stats { height: 5; padding: 1 1 0 1; }
    #stats .card { width: 1fr; height: 100%; border: round $border-dim; padding: 0 1; margin: 0 1; }

    #mid { height: 1fr; padding: 1 1 0 1; }
    #menu-panel { width: 36; margin: 0 1; }
    #activity-panel { width: 1fr; margin: 0 1; }

    #bottom { height: 12; padding: 1 1 0 1; }
    #prs-panel { width: 1fr; margin: 0 1; }
    #ci-panel { width: 1fr; margin: 0 1; }
    #health-panel { width: 44; margin: 0 1; }

    .panel {
        border: round $border-dim; padding: 0 1;
        border-title-color: $primary; border-title-align: left;
        border-subtitle-color: $primary; border-subtitle-align: right;
    }
    #menu { background: $background; height: 1fr; border: none; padding: 0; scrollbar-size: 0 0; }
    #menu > .option-list--option-highlighted { background: $primary; color: $text-primary; text-style: bold; }

    #palette-panel { height: 3; padding: 1 1 0 1; }
    #palette-panel .panel { margin: 0 1; }

    #footer { height: 1; padding: 0 2; color: $text-muted; }
    """

    BINDINGS = [
        ("enter", "open_selected", "Open"),
        ("r", "goto_repositories", ""),
        ("p", "goto_pull_requests", ""),
        ("i", "goto_issues", ""),
        ("a", "goto_actions", ""),
        ("c", "goto_commits", ""),
        ("s", "goto_settings", ""),
    ]

    # ---- compose ----

    def compose(self) -> ComposeResult:
        yield Static(self._topbar(), id="topbar")
        with Horizontal(id="stats"):
            yield from self._stat_cards()
        with Horizontal(id="mid"):
            yield Panel("MAIN MENU", self._menu(), id="menu-panel", classes="panel")
            yield Panel(
                "RECENT ACTIVITY",
                self._activity(),
                subtitle="view all",
                id="activity-panel",
                classes="panel",
            )
        with Horizontal(id="bottom"):
            yield Panel(
                "PULL REQUESTS",
                self._prs(),
                subtitle="view all (7)",
                id="prs-panel",
                classes="panel",
            )
            yield Panel(
                "ACTIONS / CI STATUS",
                self._ci(),
                subtitle="view all (23)",
                id="ci-panel",
                classes="panel",
            )
            yield Panel("REPOSITORY HEALTH", self._health(), id="health-panel", classes="panel")
        with Horizontal(id="palette-panel"):
            yield Panel("COMMAND PALETTE", self._palette(), classes="panel")
        yield Static(self._footer(), id="footer")

    def on_mount(self) -> None:
        self.query_one("#menu", OptionList).highlighted = 0

    def _c(self, name: str) -> str:
        return active_colors(self.app)[name]

    def refresh_theme(self) -> None:
        """Recompose the optional overview so its inline colors follow the theme."""
        self.refresh(recompose=True)

    # ---- top bar ----

    def _topbar(self) -> Table:
        g = _grid(1, 1)
        left = Text()
        left.append("gh-flow", style=f"bold {self._c('primary')}")
        left.append(" v0.1.0      ", style="dim")
        for label, value in (
            ("repo: ", "musa/my-app"),
            ("branch: ", "main"),
            ("status: ", "clean"),
        ):
            left.append(label, style="dim")
            left.append(value + "     ", style=self._c("success"))
        right = Text("Sun 25 May 2025   11:42 PM", style="dim", justify="right")
        g.add_row(left, right)
        return g

    # ---- stat cards ----

    def _stat_cards(self):
        cards = [
            (
                "⇄",
                self._c("primary"),
                "PULL REQUESTS",
                [("4", "open", self._c("success")), ("2", "review", "dim")],
            ),
            (
                "◉",
                self._c("warning"),
                "ISSUES",
                [("7", "open", self._c("warning")), ("3", "assigned", "dim")],
            ),
            (
                "▷",
                self._c("accent"),
                "ACTIONS / CI",
                [("1", "failed", self._c("error")), ("2", "running", self._c("warning"))],
            ),
            (
                "⇧",
                self._c("success"),
                "DEPLOYMENTS",
                [("2", "active", self._c("success")), ("1", "healthy", "dim")],
            ),
            ("◆", self._c("secondary"), "NOTIFICATIONS", [("3", "unread", self._c("secondary"))]),
            (
                "◈",
                self._c("primary"),
                "RELEASES",
                [("3", "published", self._c("success")), ("1", "draft", "dim")],
            ),
        ]
        for icon, color, title, rows in cards:
            t = Text()
            t.append(f"{icon}  ", style=color)
            t.append(f"{title}\n", style="dim")
            for i, (num, label, style) in enumerate(rows):
                if i:
                    t.append("\n")
                t.append(f"{num} ", style=f"bold {style}")
                t.append(label, style="dim")
            yield Static(t, classes="card")

    # ---- main menu ----

    def _menu(self) -> OptionList:
        items = [
            ("overview", "⌂", "Overview", ""),
            ("repositories", "▤", "Repositories", "r"),
            ("pull_requests", "⇄", "Pull Requests", "p"),
            ("issues", "◉", "Issues", "i"),
            ("actions", "▷", "Actions / CI", "a"),
            ("deployments", "⇧", "Deployments", "d"),
            ("releases", "◈", "Releases", "l"),
            ("branches", "⎇", "Branches", "b"),
            ("commits", "●", "Commits", "c"),
            ("search", "⌕", "Search", "/"),
            ("settings", "⚙", "Settings", "s"),
            ("quit", "⏻", "Quit", "q"),
        ]
        options = []
        for oid, icon, label, key in items:
            row = Text(no_wrap=True, overflow="ellipsis")
            row.append(f"{icon}  {label}")
            if key:
                pad = max(1, 30 - row.cell_len - len(key))
                row.append(" " * pad)
                row.append(key, style="dim")
            options.append(Option(row, id=oid))
        return OptionList(*options, id="menu")

    # ---- recent activity ----

    def _activity(self) -> Table:
        rows = [
            ("✗", self._c("error"), "Backend Tests workflow failed", "#9182", "4m ago"),
            (
                "✓",
                self._c("success"),
                "Merge pull request #140 from feat/dashboard",
                "main",
                "18m ago",
            ),
            ("✎", self._c("primary"), "Update README.md", "main", "38m ago"),
            (
                "✗",
                self._c("error"),
                "Database migration: Add user_sessions table",
                "#141 develop",
                "1h ago",
            ),
            ("⇧", self._c("accent"), "Deploy to Production", "main", "2h ago"),
            ("✎", self._c("primary"), "Fix payment retry logic", "#139 feat/payments", "3h ago"),
            ("✓", self._c("success"), "Bump dependencies", "main", "5h ago"),
            ("⇧", self._c("accent"), "feat: Add usage analytics", "#138 feat/analytics", "6h ago"),
            ("✓", self._c("success"), "Merge pull request #137 from fix/mobile", "main", "8h ago"),
            ("✎", self._c("primary"), "Refactor auth middleware", "#136 feat/auth", "10h ago"),
        ]
        g = _grid(1, 1, 1)
        g.columns[0].no_wrap = True
        g.columns[0].overflow = "ellipsis"
        g.columns[1].justify = "left"
        g.columns[2].justify = "right"
        for icon, color, text, ref, when in rows:
            line = Text()
            line.append(f"{icon}  ", style=color)
            line.append(text)
            g.add_row(line, Text(ref, style="dim"), Text(when, style="dim"))
        return g

    # ---- pull requests ----

    def _prs(self) -> Table:
        prs = [
            ("#142", "Add Google OAuth login", "feat/oauth", "2/2", "pass", "4m"),
            ("#141", "Improve dashboard charts", "feat/dashboard", "6/6", "pass", "1h"),
            ("#140", "Fix mobile layout issues", "fix/mobile", "6/6", "pass", "18m"),
            ("#139", "Payment retry mechanism", "fix/payment", "6/6", "pass", "3h"),
            ("#137", "Refactor auth middleware", "feat/auth", "5/6", "fail", "8h"),
        ]
        g = _grid(2, 2, 1)
        g.columns[0].no_wrap = True
        g.columns[0].overflow = "ellipsis"
        g.columns[1].no_wrap = True
        g.columns[1].overflow = "ellipsis"
        g.columns[2].justify = "right"
        for num, title, branch, checks, ci, when in prs:
            left = Text()
            left.append(f"{num}  ", style=self._c("primary"))
            left.append(title)
            mid = Text(f"{branch} → main", style="dim")
            right = Text()
            right.append(
                checks + " ", style=self._c("success") if ci == "pass" else self._c("error")
            )
            right.append(when, style="dim")
            g.add_row(left, mid, right)
        return g

    # ---- ci status ----

    def _ci(self) -> Table:
        runs = [
            ("Backend Tests", "fail", "4m 12s", "4m"),
            ("Lint & Format", "pass", "1m 03s", "6m"),
            ("E2E Tests", "pass", "5m 41s", "12m"),
            ("Build & Package", "pass", "2m 21s", "16m"),
            ("Deploy Preview", "run", "3m 11s", "17s"),
            ("Security Scan", "pass", "1m 34s", "18m"),
        ]
        color = {"pass": self._c("success"), "fail": self._c("error"), "run": self._c("warning")}
        label = {"pass": "✓ Passed", "fail": "✗ Failed", "run": "◉ Running"}
        g = _grid(2, 1, 1)
        g.columns[1].justify = "right"
        g.columns[2].justify = "right"
        for name, st, dur, when in runs:
            n = Text()
            n.append("● ", style=color[st])
            n.append(name)
            g.add_row(n, Text(label[st], style=color[st]), Text(f"{dur}  {when}", style="dim"))
        return g

    # ---- repository health ----

    def _health(self) -> Table:
        g = _grid(1, 2)
        g.add_row(Text("A-", style=f"bold {self._c('success')}"), Text(""))
        for label, value, delta in (
            ("Lines of Code", "24,312", "+324"),
            ("Test Coverage", "87%", "+2%"),
            ("Open Issues", "7", "-3"),
            ("Open PRs", "4", "-1"),
        ):
            m = Text(justify="right")
            m.append(value + "   ")
            m.append(delta, style=self._c("success"))
            g.add_row(Text(label, style="dim"), m)
        g.add_row(Text("last updated: just now", style="dim"), Text(""))
        return g

    # ---- command palette + footer ----

    def _palette(self) -> Text:
        t = Text()
        t.append(":  ", style=self._c("primary"))
        t.append("▌", style="dim")
        return t

    def _footer(self) -> Table:
        g = _grid(1, 1)
        left = Text()
        for key, desc in (
            ("↑/↓", "navigate"),
            ("enter", "select"),
            ("esc", "back"),
            ("/", "search"),
            ("?", "help"),
        ):
            left.append(f"{key} ", style=self._c("primary"))
            left.append(f"{desc}    ", style="dim")
        right = Text("https://github.com/musaJawad004/gh-tui", style="dim", justify="right")
        g.add_row(left, right)
        return g

    # ---- navigation ----

    def action_open_selected(self) -> None:
        menu = self.query_one("#menu", OptionList)
        if menu.highlighted is not None:
            self._route(menu.get_option_at_index(menu.highlighted).id)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._route(event.option.id)

    def _route(self, option_id: str | None) -> None:
        if option_id in SECTION_ROUTE:
            from screens.main import MainScreen

            self.app.push_screen(MainScreen(section=SECTION_ROUTE[option_id]))
        elif option_id == "settings":
            from screens.settings import SettingsScreen

            self.app.push_screen(SettingsScreen())
        elif option_id == "quit":
            self.app.exit()
        elif option_id and option_id != "overview":
            self.notify(f"{option_id.replace('_', ' ').title()} — coming soon")

    def action_goto_repositories(self) -> None:
        self._route("repositories")

    def action_goto_pull_requests(self) -> None:
        self._route("pull_requests")

    def action_goto_issues(self) -> None:
        self._route("issues")

    def action_goto_actions(self) -> None:
        self._route("actions")

    def action_goto_commits(self) -> None:
        self._route("commits")

    def action_goto_settings(self) -> None:
        self._route("settings")
