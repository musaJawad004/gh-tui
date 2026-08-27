"""MainScreen — the focused, terminal-first main view.

Top section tabs (PRs / Issues / Actions / Repos / Commits) + one clean list + a compact
detail line + a status bar. One thing at a time. Tab / ←→ switch sections; Enter opens an
item; `d` opens the full dashboard.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Static

from themes.palettes import active_colors

SECTIONS = ["Pull Requests", "Issues", "Actions", "Repos", "Commits"]


# --- mock data ---------------------------------------------------------------


def _prs(colors):
    data = [
        (
            "#142",
            "Add Google OAuth login",
            "feat/oauth",
            "pass",
            "+391 -4",
            "1h",
            "2/2 checks · 2 reviews",
        ),
        (
            "#141",
            "Improve dashboard charts",
            "feat/dashboard",
            "pass",
            "+120 -18",
            "1h",
            "6/6 checks · 1 review",
        ),
        (
            "#140",
            "Fix mobile layout issues",
            "fix/mobile",
            "pass",
            "+48 -12",
            "18m",
            "6/6 checks · 2 reviews",
        ),
        (
            "#139",
            "Payment retry mechanism",
            "fix/payment",
            "pass",
            "+92 -31",
            "3h",
            "6/6 checks · approved",
        ),
        (
            "#138",
            "Add usage analytics",
            "feat/analytics",
            "pass",
            "+210 -5",
            "6h",
            "4/4 checks · 1 review",
        ),
        (
            "#137",
            "Refactor auth middleware",
            "feat/auth",
            "fail",
            "+64 -220",
            "8h",
            "5/6 checks · 3 reviews",
        ),
        (
            "#136",
            "Search across everything",
            "feat/search",
            "pass",
            "+718 -40",
            "1d",
            "8/8 checks · approved",
        ),
    ]
    cols = ["", "Title", "CI", "±", "Updated"]
    rows = []
    for num, title, branch, ci, diff, upd, meta in data:
        ci_cell = (
            Text("✓", style=colors["success"]) if ci == "pass" else Text("✗", style=colors["error"])
        )
        add, rem = diff.split(" ")
        d = Text()
        d.append(add + " ", style=colors["success"])
        d.append(rem, style=colors["error"])
        rows.append(
            {
                "cells": [
                    Text(num, style=colors["primary"]),
                    Text(title),
                    ci_cell,
                    d,
                    Text(upd, style="dim"),
                ],
                "detail": f"{branch} → main · {meta}",
                "item": {
                    "kind": "Pull Request",
                    "id": num,
                    "title": title,
                    "lines": [
                        f"branch   {branch} → main",
                        f"ci       {ci}",
                        f"changes  {diff}",
                        f"meta     {meta}",
                    ],
                },
            }
        )
    return cols, rows


def _issues(colors):
    data = [
        ("#87", "OAuth redirect fails on Safari", "bug, auth", 4, "2h", "dlvhdr"),
        ("#85", "Dark theme contrast on tables", "ui", 1, "5h", "musa"),
        ("#84", "Add pagination to PR list", "enhancement", 0, "8h", "musa"),
        ("#80", "Document the config file", "docs, good-first", 3, "1d", "sarah"),
        ("#78", "Flaky E2E on checkout step", "bug, ci", 6, "1d", "john"),
        ("#75", "Support GitLab backend", "enhancement", 9, "3d", "musa"),
        ("#71", "Cache GraphQL responses", "perf", 2, "4d", "dlvhdr"),
    ]
    cols = ["", "Title", "Labels", "Cmts", "Updated"]
    rows = []
    for num, title, labels, cmts, upd, author in data:
        rows.append(
            {
                "cells": [
                    Text(num, style=colors["warning"]),
                    Text(title),
                    Text(labels, style="dim"),
                    Text(str(cmts), style="dim"),
                    Text(upd, style="dim"),
                ],
                "detail": f"opened by @{author} · {cmts} comments · labels: {labels}",
                "item": {
                    "kind": "Issue",
                    "id": num,
                    "title": title,
                    "lines": [
                        f"author   @{author}",
                        f"labels   {labels}",
                        f"comments {cmts}",
                        f"updated  {upd}",
                    ],
                },
            }
        )
    return cols, rows


def _actions(colors):
    data = [
        ("Backend Tests", "main", "fail", "4m 12s", "4m"),
        ("Lint & Format", "main", "pass", "1m 03s", "6m"),
        ("E2E Tests", "feat/oauth", "pass", "5m 41s", "12m"),
        ("Build & Package", "main", "pass", "2m 21s", "16m"),
        ("Deploy Preview", "feat/oauth", "run", "3m 11s", "17s"),
        ("Security Scan", "main", "pass", "1m 34s", "18m"),
    ]
    cols = ["Workflow", "Branch", "Status", "Duration", "Updated"]
    style = {"pass": colors["success"], "fail": colors["error"], "run": colors["warning"]}
    label = {"pass": "✓ Passed", "fail": "✗ Failed", "run": "◉ Running"}
    rows = []
    for wf, branch, st, dur, upd in data:
        rows.append(
            {
                "cells": [
                    Text(wf),
                    Text(branch, style="dim"),
                    Text(label[st], style=style[st]),
                    Text(dur, style="dim"),
                    Text(upd, style="dim"),
                ],
                "detail": f"{wf} · {branch} · {label[st].split(' ', 1)[1].lower()} in {dur}",
                "item": {
                    "kind": "Workflow run",
                    "id": wf,
                    "title": wf,
                    "lines": [
                        f"branch    {branch}",
                        f"status    {label[st]}",
                        f"duration  {dur}",
                        f"updated   {upd} ago",
                    ],
                },
            }
        )
    return cols, rows


def _repos(colors):
    data = [
        ("musa/my-app", "public", "Python", "42", "2h"),
        ("musa/gh-tui", "public", "Python", "128", "1d"),
        ("musa/portfolio", "public", "TypeScript", "17", "3d"),
        ("musa/emberflow", "public", "Go", "64", "5d"),
        ("musa/job-agent", "private", "Python", "0", "1w"),
        ("musa/glixen-tech", "private", "TypeScript", "3", "2w"),
    ]
    cols = ["Repository", "Vis", "Lang", "Stars", "Updated"]
    rows = []
    for name, vis, lang, stars, upd in data:
        rows.append(
            {
                "cells": [
                    Text(name, style=colors["secondary"]),
                    Text(vis, style="dim"),
                    Text(lang),
                    Text(stars, style=colors["warning"]),
                    Text(upd, style="dim"),
                ],
                "detail": f"{name} · {vis} · {lang} · ★ {stars}",
                "item": {
                    "kind": "Repository",
                    "id": name,
                    "title": name,
                    "lines": [
                        f"visibility  {vis}",
                        f"language    {lang}",
                        f"stars       {stars}",
                        f"updated     {upd} ago",
                    ],
                },
            }
        )
    return cols, rows


def _commits(colors):
    data = [
        ("981dad2", "fix oauth callback", "Musa", "4m", "3 files +84 -21"),
        ("e901bc8", "add Google provider", "Musa", "22m", "5 files +210 -4"),
        ("1ab92ef", "update auth tests", "Sarah", "1h", "2 files +48 -12"),
        ("f90cc21", "add session handling", "Musa", "2h", "4 files +160 -30"),
        ("c12ab90", "bump dependencies", "John", "5h", "1 file +12 -12"),
        ("a81bd90", "docs: contributing guide", "Musa", "1d", "1 file +64 -2"),
    ]
    cols = ["SHA", "Message", "Author", "When"]
    rows = []
    for sha, msg, author, when, changes in data:
        rows.append(
            {
                "cells": [
                    Text(sha, style=colors["warning"]),
                    Text(msg),
                    Text(author, style=colors["secondary"]),
                    Text(when, style="dim"),
                ],
                "detail": f"{sha} · {author} · {changes}",
                "item": {
                    "kind": "Commit",
                    "id": sha,
                    "title": msg,
                    "lines": [
                        f"sha      {sha}",
                        f"author   {author}",
                        f"changes  {changes}",
                        f"when     {when} ago",
                    ],
                },
            }
        )
    return cols, rows


BUILDERS = [_prs, _issues, _actions, _repos, _commits]


# --- detail modal ------------------------------------------------------------


class ItemDetail(ModalScreen):
    DEFAULT_CSS = """
    ItemDetail { align: center middle; background: $background 70%; }
    ItemDetail #card {
        width: 64; height: auto; padding: 1 2;
        border: solid $primary; background: $surface;
    }
    """
    BINDINGS = [("escape", "dismiss", "Close"), ("q", "dismiss", "Close")]

    def __init__(self, item: dict):
        super().__init__()
        self._item = item

    def compose(self) -> ComposeResult:
        colors = active_colors(self.app)
        t = Text()
        t.append(f"{self._item['kind']}  ", style="dim")
        t.append(f"{self._item['id']}\n", style=colors["primary"])
        t.append(f"{self._item['title']}\n\n", style="bold")
        for line in self._item["lines"]:
            t.append(line + "\n", style="dim")
        t.append("\npress esc to close", style="dim")
        yield Static(t, id="card")


# --- main screen -------------------------------------------------------------


class MainScreen(Screen):
    DEFAULT_CSS = """
    MainScreen { layout: vertical; background: $background; }
    MainScreen #header {
        height: 3; padding: 0 1;
        border-bottom: solid $border-dim;
        background: $surface;
    }
    MainScreen #list {
        height: 1fr; padding: 0 1;
        background: $background; color: $foreground;
        scrollbar-size-vertical: 1;
    }
    MainScreen #list > .datatable--header {
        color: $text-muted; text-style: none;
        background: $background;
    }
    MainScreen #list > .datatable--cursor {
        background: $row-selected; color: $foreground;
        text-style: bold;
    }
    MainScreen #list > .datatable--hover { background: $surface; }
    MainScreen #context {
        height: 2; padding: 0 2; color: $text-muted;
        border-top: solid $border-dim;
    }
    MainScreen #command {
        dock: bottom; height: 1; padding: 0 1;
        color: $text-muted; background: $surface;
    }
    """

    BINDINGS = [
        ("1", "section_1", ""),
        ("2", "section_2", ""),
        ("3", "section_3", ""),
        ("4", "section_4", ""),
        ("5", "section_5", ""),
        ("tab", "next_section", "Next"),
        ("shift+tab", "prev_section", "Prev"),
        ("right", "next_section", ""),
        ("left", "prev_section", ""),
        ("j", "cursor_down", ""),
        ("k", "cursor_up", ""),
        ("enter", "open_item", "Open"),
        ("o", "overview", "Overview"),
        ("g", "settings", "Settings"),
    ]

    def __init__(self, section: int = 0) -> None:
        super().__init__()
        self._initial_section = section % len(SECTIONS)

    def compose(self) -> ComposeResult:
        yield Static(id="header")
        yield DataTable(id="list")
        yield Static(id="context")
        yield Static(id="command")

    def on_mount(self) -> None:
        self._section = self._initial_section
        self._rows: list = []
        table = self.query_one("#list", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = False
        self._render_header()
        self._load_section()
        self._render_command()

    def on_screen_resume(self) -> None:
        """Repaint Rich spans after returning from the live theme picker."""
        self.refresh_theme()

    def refresh_theme(self) -> None:
        """Rebuild inline Rich colors after the application palette changes."""
        self._render_header()
        self._load_section()
        self._render_command()

    # ---- rendering ----

    def _render_header(self) -> None:
        colors = active_colors(self.app)
        t = Text()
        t.append(" gh-tui ", style=f"bold {colors['background']} on {colors['primary']}")
        t.append("  musa/my-app", style=colors["secondary"])
        t.append("  main", style=colors["success"])
        t.append("  clean", style=colors["success"])
        t.append(f"  ·  theme {self.app.theme}\n", style="dim")
        t.append(" ")
        for i, name in enumerate(SECTIONS):
            if i:
                t.append("  ")
            if i == self._section:
                t.append(f"[{i + 1}:{name}]", style=f"bold {colors['primary']}")
            else:
                t.append(f" {i + 1}:{name} ", style="dim")
        self.query_one("#header", Static).update(t)

    def _render_command(self) -> None:
        colors = active_colors(self.app)
        t = Text()
        t.append(":", style=f"bold {colors['primary']}")
        t.append(
            "  j/k move  enter open  tab section  o overview  g settings  ^t theme  ? help  q quit"
        )
        self.query_one("#command", Static).update(t)

    def _load_section(self) -> None:
        cols, self._rows = BUILDERS[self._section](active_colors(self.app))
        table = self.query_one("#list", DataTable)
        table.clear(columns=True)
        table.add_columns(*cols)
        for r in self._rows:
            table.add_row(*r["cells"])
        if self._rows:
            self._show_detail(0)

    def _show_detail(self, idx: int) -> None:
        if 0 <= idx < len(self._rows):
            colors = active_colors(self.app)
            detail = Text()
            detail.append("selected  ", style=colors["primary"])
            detail.append(self._rows[idx]["detail"], style="dim")
            self.query_one("#context", Static).update(detail)

    # ---- events ----

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._show_detail(event.cursor_row)

    # ---- actions ----

    def action_next_section(self) -> None:
        self._section = (self._section + 1) % len(SECTIONS)
        self._render_header()
        self._load_section()

    def action_prev_section(self) -> None:
        self._section = (self._section - 1) % len(SECTIONS)
        self._render_header()
        self._load_section()

    def _set_section(self, section: int) -> None:
        self._section = section
        self._render_header()
        self._load_section()

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

    def action_cursor_down(self) -> None:
        self.query_one("#list", DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#list", DataTable).action_cursor_up()

    def action_open_item(self) -> None:
        table = self.query_one("#list", DataTable)
        idx = table.cursor_row
        if 0 <= idx < len(self._rows):
            self.app.push_screen(ItemDetail(self._rows[idx]["item"]))

    def action_overview(self) -> None:
        from screens.overview import OverviewScreen

        self.app.push_screen(OverviewScreen())

    def action_settings(self) -> None:
        from screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())
