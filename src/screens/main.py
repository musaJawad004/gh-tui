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
from textual.containers import Horizontal, Vertical
from textual.events import Resize
from textual.screen import Screen
from textual.widgets import Static

from themes.palettes import active_colors
from widgets.spinner import indeterminate_bar, inline_loader

SECTIONS = ["Pull Requests", "Issues", "CI / CD", "Repos", "Commits"]


def _grid(*ratios: int, padding: tuple[int, int] = (0, 1)) -> Table:
    table = Table.grid(expand=True, padding=padding)
    for ratio in ratios:
        table.add_column(ratio=ratio)
    return table


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
    MainScreen #detail {
        width: 58%;
        height: 1fr;
        padding: 1 2;
        overflow: hidden hidden;
        background: $background;
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
    MainScreen.narrow #navigator { display: none; }
    MainScreen.narrow #detail { width: 100%; padding: 1; }
    MainScreen.compact #header { height: 3; }
    MainScreen.compact #status { height: 1; }
    MainScreen.compact #navigator,
    MainScreen.compact #detail { padding: 0 1; }
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
        ("j", "noop", ""),
        ("k", "noop", ""),
        ("enter", "noop", ""),
        ("o", "overview", "Overview"),
        ("g", "settings", "Settings"),
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
            with Vertical(id="detail"):
                yield Static(id="detail-content")
        yield Static(id="status")

    def on_mount(self) -> None:
        self._section = self._initial_section
        self._load_frame = 0
        self._load_timer = None
        self._compact = False
        self._apply_breakpoints(self.size.width, self.size.height)
        self._render_workspace()

    def on_resize(self, event: Resize) -> None:
        self._apply_breakpoints(event.size.width, event.size.height)
        if self.is_mounted and self._load_timer is None:
            self._render_workspace()

    def _apply_breakpoints(self, width: int, height: int) -> None:
        self._compact = height < 34
        if width < 90:
            self.add_class("narrow")
        else:
            self.remove_class("narrow")
        if self._compact:
            self.add_class("compact")
        else:
            self.remove_class("compact")

    def on_screen_resume(self) -> None:
        self.refresh_theme()

    def refresh_theme(self) -> None:
        self._render_workspace()

    def _c(self, name: str) -> str:
        return active_colors(self.app)[name]

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
        self.query_one("#navigator-content", Static).update(left)
        self.query_one("#detail-content", Static).update(right)
        self.query_one("#status", Static).update(status)

    def _render_header(self) -> None:
        line = Text()
        line.append(" gh-flow ", style=f"bold {self._c('background')} on {self._c('success')}")
        line.append("  musa/my-app", style=self._c("primary"))
        line.append("  main ↑2", style=self._c("success"))
        line.append("  ·  clean\n", style="dim")
        for index, name in enumerate(SECTIONS):
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

    def _pull_requests(self):
        rows = [
            ("#142", "Add Google OAuth login", "feat/oauth", "✓", "2/2", "+391  -4", "4m"),
            ("#141", "Improve dashboard charts", "feat/dashboard", "✓", "6/6", "+120  -18", "1h"),
            ("#140", "Fix mobile layout issues", "fix/mobile", "✓", "6/6", "+48  -12", "18m"),
            ("#139", "Payment retry mechanism", "fix/payment", "✓", "6/6", "+92  -31", "3h"),
        ]
        if self._compact:
            rows = rows[:3]
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
            style = f"on {self._c('row_selected')}" if index == 0 else None
            table.add_row(Text(number, style=self._c("primary")), title_cell, ci_cell, change_cell, style=style)

        left = Group(
            self._search("is:pr is:open author:@me", "4 open"),
            Text("\n"),
            table,
        )

        meta = Text()
        meta.append("musa/my-app  ·  #142\n", style=self._c("primary"))
        meta.append("Add Google OAuth login\n", style="bold")
        meta.append("\n OPEN ", style=f"bold {self._c('background')} on {self._c('primary')}")
        meta.append("  feat/oauth → main  ·  by @musa  ·  4m ago\n", style="dim")
        meta.append("\n▣ Overview   ✓ Checks 2/2   ◇ Files changed 8   ◌ Activity", style="bold")

        summary = Text()
        summary.append("Ready for review\n", style=f"bold {self._c('success')}")
        summary.append("Adds Google OAuth sign-in, session persistence, and callback handling.\n\n")
        summary.append("+391 additions   ", style=self._c("success"))
        summary.append("-4 deletions   ", style=self._c("error"))
        summary.append("8 files changed", style="dim")

        comment = Text()
        comment.append("@sarah  ·  reviewer  ·  2m\n", style="bold")
        comment.append("The callback flow looks clean. One small question about token expiry, ")
        comment.append("otherwise this is ready to merge.", style="dim")

        right = Group(
            meta,
            Text("\n"),
            Panel(summary, title="review summary", border_style=self._c("border")),
            Text("\n conversation", style=self._c("primary")),
            Panel(comment, border_style=self._c("border")),
            Panel(Text("comment  █", style="dim"), border_style=self._c("border")),
        )
        return left, right, self._status("PR 1/4", "2 approvals", "2/2 checks", "8 files")

    def _issues(self):
        rows = [
            ("#87", "OAuth redirect fails on Safari", "bug · auth", "4", "2h"),
            ("#85", "Dark theme contrast on tables", "ui", "1", "5h"),
            ("#84", "Add pagination to PR list", "enhancement", "0", "8h"),
            ("#80", "Document the config file", "docs · good first issue", "3", "1d"),
            ("#78", "Flaky E2E on checkout step", "bug · ci", "6", "1d"),
        ]
        if self._compact:
            rows = rows[:3]
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=6)
        table.add_column(ratio=1)
        table.add_column(width=8, justify="right")
        for index, (number, title, labels, comments, age) in enumerate(rows):
            body = Text(title, style="bold" if index == 0 else "")
            body.append(f"\n{labels}", style=self._c("warning"))
            tail = Text(f"◌ {comments}\n{age}", style="dim", justify="right")
            style = f"on {self._c('row_selected')}" if index == 0 else None
            table.add_row(Text(number, style=self._c("warning")), body, tail, style=style)
        left = Group(self._search("is:issue is:open", "7 open"), Text("\n"), table)

        header = Text()
        header.append("musa/my-app  ·  Issue #87\n", style=self._c("primary"))
        header.append("OAuth redirect fails on Safari\n", style="bold")
        header.append("\n OPEN ", style=f"bold {self._c('background')} on {self._c('success')}")
        header.append("  opened by @dlvhdr 2h ago  ·  bug  auth\n", style="dim")
        header.append("\n▣ Conversation   ◉ Timeline   ◇ Related PRs", style="bold")

        first = Text()
        first.append("@dlvhdr  ·  author  ·  2h\n", style="bold")
        first.append("Safari returns to the callback without the stored state cookie. ")
        first.append("Chrome and Firefox both work as expected.\n\n", style="dim")
        first.append("macOS 15.6  ·  Safari 18.6  ·  production", style=self._c("warning"))
        reply = Text()
        reply.append("@musa  ·  maintainer  ·  38m\n", style="bold")
        reply.append("Confirmed. The SameSite policy looks like the likely cause. ")
        reply.append("I’m tracing the callback cookie now.", style="dim")
        right = Group(
            header,
            Text("\n"),
            Panel(first, border_style=self._c("border")),
            Panel(reply, border_style=self._c("border")),
            Text("\n reply", style=self._c("primary")),
            Panel(Text("Write a comment…  █\n\nMarkdown supported", style="dim"), border_style=self._c("primary")),
        )
        return left, right, self._status("Issue 1/7", "4 comments", "2 participants", "updated 2h")

    def _pipelines(self):
        rows = [
            ("×", "backend-tests", "main", "failed", "4m 12s", "4m"),
            ("✓", "lint & format", "main", "passed", "1m 03s", "6m"),
            ("✓", "e2e tests", "feat/oauth", "passed", "5m 41s", "12m"),
            ("✓", "build & package", "main", "passed", "2m 21s", "16m"),
            ("○", "deploy preview", "feat/oauth", "running", "3m 11s", "now"),
            ("✓", "security scan", "main", "passed", "1m 34s", "18m"),
        ]
        if self._compact:
            rows = rows[:4]
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=3)
        table.add_column(ratio=1)
        table.add_column(width=11, justify="right")
        for index, (icon, name, branch, state, duration, age) in enumerate(rows):
            color = "error" if state == "failed" else "warning" if state == "running" else "success"
            body = Text(name, style="bold" if index == 0 else "")
            body.append(f"\n{branch}", style="dim")
            tail = Text(state, style=self._c(color), justify="right")
            tail.append(f"\n{duration} · {age}", style="dim")
            style = f"on {self._c('row_selected')}" if index == 0 else None
            table.add_row(Text(icon, style=self._c(color)), body, tail, style=style)
        left = Group(self._search("branch:main event:push", "23 runs"), Text("\n"), table)

        header = Text()
        header.append("backend-tests  ·  run #9182\n", style=self._c("primary"))
        header.append("main  ·  981dad2  ·  push by @musa\n", style="dim")
        header.append("\n FAILED ", style=f"bold {self._c('background')} on {self._c('error')}")
        header.append("  4m 12s  ·  finished 4m ago\n")
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
        logs.append("tests/test_auth.py::test_safari_callback ", style="dim")
        logs.append("FAILED\n", style=self._c("error"))
        logs.append("AssertionError: state cookie was not restored\n", style=self._c("error"))
        logs.append("1 failed, 248 passed in 181.44s", style="dim")
        right = Group(
            header,
            Text("\n pipeline", style=self._c("primary")),
            Panel(steps, border_style=self._c("border")),
            Text("\n failure log", style=self._c("error")),
            Panel(logs, border_style=self._c("error")),
            Text("\n deployments  production ✓   staging ✓   preview ○ running", style="dim"),
        )
        return left, right, self._status("Run 1/23", "3 jobs", "1 failed", "2 artifacts")

    def _repositories(self):
        rows = [
            ("musa/my-app", "Python", "public", "42", "2h"),
            ("musa/gh-tui", "Python", "public", "128", "1d"),
            ("musa/portfolio", "TypeScript", "public", "17", "3d"),
            ("musa/emberflow", "Go", "public", "64", "5d"),
            ("musa/job-agent", "Python", "private", "0", "1w"),
        ]
        if self._compact:
            rows = rows[:3]
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(width=13)
        table.add_column(width=8, justify="right")
        for index, (name, lang, visibility, stars, age) in enumerate(rows):
            body = Text(name, style=f"bold {self._c('primary')}")
            body.append(f"\n{lang} · {visibility}", style="dim")
            tail = Text(f"★ {stars}\n{age}", style=self._c("warning"), justify="right")
            table.add_row(body, "", tail, style=f"on {self._c('row_selected')}" if index == 0 else None)
        left = Group(self._search("owner:musa", "6 repos"), Text("\n"), table)
        info = Text()
        info.append("musa/my-app\n", style=f"bold {self._c('primary')}")
        info.append("GitHub workflow dashboard and deployment toolkit.\n\n", style="dim")
        info.append("main  ↑2   clean\n", style=self._c("success"))
        info.append("Python  ·  MIT  ·  public  ·  ★ 42\n\n", style="dim")
        info.append("4 pull requests   7 issues   3 releases\n")
        info.append("CI passing   production healthy", style=self._c("success"))
        tree = Text("▾ src\n  ▾ screens\n    overview.py\n    main.py\n  ▾ widgets\n    spinner.py\n  app.py\n▸ tests\nREADME.md", style="dim")
        right = Group(info, Text("\n repository tree", style=self._c("primary")), Panel(tree, border_style=self._c("border")))
        return left, right, self._status("Repo 1/6", "main ↑2", "clean", "updated 2h")

    def _commits(self):
        tree = Text()
        tree.append("⌕  Filter files                         8 changed\n\n", style="dim")
        file_rows = [
            ("▾", "src", "", "primary", False),
            ("  ▾", "screens", "", "primary", False),
            ("    ", "main.py", "M  +84 -21", "warning", True),
            ("    ", "overview.py", "M  +31 -12", "warning", False),
            ("  ▾", "widgets", "", "primary", False),
            ("    ", "spinner.py", "M  +198 -46", "warning", False),
            ("▾", "tests", "", "primary", False),
            ("    ", "test_loaders.py", "A  +41", "success", False),
            ("    ", "test_smoke.py", "M  +16 -0", "warning", False),
            ("  ", "README.md", "M  +12 -3", "warning", False),
            ("  ", "pyproject.toml", "M  +4 -1", "warning", False),
        ]
        if self._compact:
            file_rows = file_rows[:8]
        for prefix, name, change, color, selected in file_rows:
            row = Text(f"{prefix} ")
            row.append(name, style=self._c("primary") if "▾" in prefix else "")
            if change:
                row.append(f"  {change}", style=self._c(color))
            if selected:
                row.stylize(f"bold on {self._c('row_selected')}")
            tree.append_text(row)
            tree.append("\n")
        left = Group(tree, Text("\n  8 files   +386 additions   -83 deletions", style="dim"))

        head = Text()
        head.append("Commit 981dad2\n", style=self._c("primary"))
        head.append("feat: rebuild terminal workspaces\n", style="bold")
        head.append("@musa  ·  4m ago  ·  main  ·  signed ✓\n", style="dim")
        head.append("\n AHEAD 2 ", style=f"bold {self._c('background')} on {self._c('success')}")
        head.append("   behind 0   │   Files 8   │   +386 ", style="dim")
        head.append("-83\n", style=self._c("error"))
        head.append("\n◀ previous commit   1 / 8 files   next file ▶", style="dim")

        diff_header = Text("▣ src/screens/main.py     ", style="bold")
        diff_header.append("+84", style=self._c("success"))
        diff_header.append("  -21", style=self._c("error"))
        diff = _grid(1, 1, padding=(0, 1))
        old = Text()
        new = Text()
        for number, code, style in (
            (26, "class MainScreen(Screen):", ""),
            (27, "    layout: vertical", ""),
            (28, "    DataTable(id='list')", "error"),
            (29, "", ""),
            (30, "    def _load_section():", ""),
            (31, "        table.clear()", "error"),
            (32, "", ""),
        ):
            old.append(f"{number:>3}  {code}\n", style=self._c(style) if style else "dim")
        for number, code, style in (
            (26, "class MainScreen(Screen):", ""),
            (27, "    layout: vertical", ""),
            (28, "    Horizontal(id='workspace')", "success"),
            (29, "    VerticalScroll(id='detail')", "success"),
            (30, "    def _render_workspace():", ""),
            (31, "        left, right = renderer()", "success"),
            (32, "        detail.update(right)", "success"),
        ):
            new.append(f"{number:>3}  {code}\n", style=self._c(style) if style else "dim")
        diff.add_row(old, new)
        right = Group(head, Text("\n"), Panel(diff, title=diff_header, border_style=self._c("border")))
        status = self._status("Commit 981dad2", "ahead 2 · behind 0", "file 1/8", "+386 -83")
        return left, right, status

    def _status(self, *items: str) -> Text:
        result = Text()
        for index, item in enumerate(items):
            if index:
                result.append("  ·  ", style="dim")
            result.append(item, style=self._c("primary") if index == 0 else "dim")
        result.append("     [tab] section  [←/→] switch  [o] overview  [q] quit", style="dim")
        return result

    def _set_section(self, section: int) -> None:
        self._section = section % len(SECTIONS)
        self._render_header()
        self._begin_section_load()

    def _begin_section_load(self) -> None:
        if self._load_timer is not None:
            self._load_timer.stop()
        self._load_frame = 0
        self.query_one("#workspace", Horizontal).display = False
        self.query_one("#loader", Static).display = True
        self._render_section_loader()
        self._load_timer = self.set_interval(0.08, self._tick_section_load)

    def _tick_section_load(self) -> None:
        self._load_frame += 1
        self._render_section_loader()
        if self._load_frame >= 7:
            self._load_timer.stop()
            self._load_timer = None
            self._render_workspace()
            self.query_one("#loader", Static).display = False
            self.query_one("#workspace", Horizontal).display = True

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
        content.append("\n\n")
        content.append_text(indeterminate_bar(self._load_frame, width=46, color=self._c("primary")))
        self.query_one("#loader", Static).update(content)

    def action_next_section(self) -> None:
        self._set_section(self._section + 1)

    def action_prev_section(self) -> None:
        self._set_section(self._section - 1)

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

    def action_noop(self) -> None:
        pass
