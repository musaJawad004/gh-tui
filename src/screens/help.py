"""HelpScreen — a modal cheatsheet of keybindings, opened with `?`."""

from __future__ import annotations

from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import ModalScreen
from textual.widgets import Static

from themes.palettes import ACCENT_BLUE as BLUE

BINDINGS_HELP = [
    ("Navigation", ""),
    ("↑ / k", "Move up"),
    ("↓ / j", "Move down"),
    ("← / →", "Move between panels"),
    ("Tab / Shift+Tab", "Cycle focus"),
    ("Enter", "Open / view details"),
    ("Esc", "Back"),
    ("", ""),
    ("Global", ""),
    ("?", "This help"),
    ("Ctrl+P", "Command palette"),
    ("/", "Search"),
    ("Ctrl+T", "Toggle theme"),
    ("g", "Go to settings"),
    ("q", "Quit gh-tui"),
]


class HelpScreen(ModalScreen):
    DEFAULT_CSS = """
    HelpScreen { align: center middle; background: $background 60%; }
    HelpScreen #card {
        width: 54; height: auto; padding: 1 2;
        border: round $border-dim; background: $surface;
    }
    HelpScreen #hint { color: $text-muted; margin-top: 1; }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
        ("question_mark", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Middle(), Center():
            yield Static(self._body(), id="card")

    def _body(self):
        table = Table.grid(padding=(0, 2))
        table.add_column(justify="right", no_wrap=True)
        table.add_column()
        title = Text("gh-tui — keyboard shortcuts", style=f"bold {BLUE}")
        table.add_row("", title)
        table.add_row("", "")
        for key, desc in BINDINGS_HELP:
            if key == "" and desc == "":
                table.add_row("", "")
            elif desc == "":
                table.add_row("", Text(key, style="bold"))
            else:
                table.add_row(Text(key, style=BLUE), Text(desc, style="dim"))
        table.add_row("", "")
        table.add_row("", Text("press esc to close", style="dim"))
        return table
