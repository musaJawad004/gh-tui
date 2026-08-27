"""GhTuiApp — the Textual application.

Registers themes, applies the default (or a requested) theme, and opens the requested
start screen (the Overview dashboard by default).
"""

from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from themes import DEFAULT_THEME, register_themes


class GhTuiApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "gh-tui"

    BINDINGS = [
        Binding("question_mark", "help", "Help"),
        Binding("ctrl+t", "cycle_theme", "Theme"),
    ]

    def __init__(self, theme: str | None = None, start_screen: str | None = None) -> None:
        super().__init__()
        # Register + apply the theme here so its custom CSS variables ($border-dim,
        # $row-selected, ...) are defined when the stylesheet is first parsed.
        register_themes(self)
        self.theme = theme if theme in ("gh-dark", "gh-light") else DEFAULT_THEME
        self._start_screen = start_screen
        # App-wide settings (edited on the Settings screen).
        self.settings: dict = {
            "theme": self.theme,
            "nerd_fonts": False,
            "default_screen": "overview",
            "confirm_destructive": True,
            "auto_refresh": "30s",
            "per_page": 30,
            "default_owner": "musaJawad004",
            "base_branch": "main",
        }

    def action_help(self) -> None:
        from screens.help import HelpScreen

        if not isinstance(self.screen, HelpScreen):
            self.push_screen(HelpScreen())

    def action_cycle_theme(self) -> None:
        order = ["gh-dark", "gh-light"]
        current = self.theme
        self.theme = (
            order[(order.index(current) + 1) % len(order)] if current in order else order[0]
        )
        self.settings["theme"] = self.theme

    def on_mount(self) -> None:
        from screens.overview import OverviewScreen
        from screens.pull_requests import HomeScreen
        from screens.settings import SettingsScreen

        if self._start_screen == "pull-requests":
            self.push_screen(HomeScreen())
        elif self._start_screen == "settings":
            self.push_screen(SettingsScreen())
        else:
            self.push_screen(OverviewScreen())


def main() -> None:
    GhTuiApp().run()


if __name__ == "__main__":
    main()
