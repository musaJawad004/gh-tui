"""SettingsScreen — real, editable settings.

Grouped list; Enter on a row cycles its value (theme applies live). Includes a working
"Check for updates" that hits GitHub in a background thread and notifies the result.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from themes.palettes import ACCENT_BLUE as BLUE
from themes.palettes import THEME_NAMES
from version import __version__

# id -> ordered list of values it cycles through
CYCLES: dict[str, list] = {
    "theme": THEME_NAMES,
    "nerd_fonts": [False, True],
    "default_screen": ["overview", "pull-requests"],
    "auto_refresh": ["off", "15s", "30s", "60s"],
    "confirm_destructive": [True, False],
    "per_page": [20, 30, 50],
}

# (kind, id, label)  kind: header | sep | cycle | info | action
ROWS = [
    ("header", None, "APPEARANCE"),
    ("cycle", "theme", "Theme"),
    ("cycle", "nerd_fonts", "Nerd Font glyphs"),
    ("sep", None, None),
    ("header", None, "BEHAVIOR"),
    ("cycle", "default_screen", "Default screen"),
    ("cycle", "auto_refresh", "Auto-refresh"),
    ("cycle", "confirm_destructive", "Confirm destructive actions"),
    ("cycle", "per_page", "Items per page"),
    ("sep", None, None),
    ("header", None, "GITHUB & GIT"),
    ("info", "default_owner", "Default owner"),
    ("info", "base_branch", "Default base branch"),
    ("sep", None, None),
    ("header", None, "ABOUT"),
    ("action", "check_updates", "Check for updates"),
    ("info", "version", "Version"),
]

_LABELS = {sid: label for kind, sid, label in ROWS if kind in ("cycle", "info", "action")}


class SettingsScreen(Screen):
    DEFAULT_CSS = """
    SettingsScreen { layout: vertical; background: $background; padding: 1 2; }
    SettingsScreen #s-title { height: 1; margin-bottom: 1; }
    SettingsScreen #s-list {
        height: 1fr; border: round $border-dim; padding: 1 1; background: $background;
    }
    SettingsScreen #s-list > .option-list--option-highlighted {
        background: $primary; color: $background; text-style: bold;
    }
    SettingsScreen #s-hint { height: 1; margin-top: 1; color: $text-muted; }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(Text("⚙  Settings", style="bold"), id="s-title")
        yield self._build_list()
        yield Static(Text("enter: change   ·   esc: back   ·   q: quit", style="dim"), id="s-hint")

    # ---- data ----

    def _value(self, sid: str) -> str:
        if sid == "version":
            return __version__
        v = self.app.settings.get(sid)
        if isinstance(v, bool):
            return "On" if v else "Off"
        return str(v)

    def _row(self, label: str, value: str | None) -> Text:
        t = Text()
        t.append("  " + label)
        if value is not None:
            pad = max(2, 46 - t.cell_len - len(value))
            t.append(" " * pad)
            t.append(value, style=BLUE)
        return t

    def _build_list(self) -> OptionList:
        options: list = []
        for kind, sid, label in ROWS:
            if kind == "sep":
                options.append(Option(Text(""), disabled=True))
            elif kind == "header":
                options.append(Option(Text(label, style="bold dim"), disabled=True))
            elif kind == "action":
                options.append(Option(self._row(label, "▷ run"), id=sid))
            else:  # cycle | info
                options.append(Option(self._row(label, self._value(sid)), id=sid))
        return OptionList(*options, id="s-list")

    # ---- interaction ----

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        sid = event.option.id
        if sid is None:
            return
        if sid == "check_updates":
            self._check_updates()
            return
        if sid in CYCLES:
            values = CYCLES[sid]
            current = self.app.settings.get(sid)
            nxt = (
                values[(values.index(current) + 1) % len(values)]
                if current in values
                else values[0]
            )
            self.app.settings[sid] = nxt
            if sid == "theme":
                self.app.theme = nxt
            self.query_one("#s-list", OptionList).replace_option_prompt(
                sid, self._row(_LABELS[sid], self._value(sid))
            )

    def _check_updates(self) -> None:
        self.notify("Checking for updates…")
        self.run_worker(self._do_check, thread=True)

    def _do_check(self) -> None:
        from cli import latest_message

        self.app.call_from_thread(self.notify, latest_message())
