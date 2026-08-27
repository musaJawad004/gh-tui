"""GhTuiApp — the Textual application.

Registers themes, applies the default (or a requested) theme, and opens the requested
start screen (the focused workspace by default).
"""

from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from themes import DEFAULT_THEME, THEME_NAMES, register_themes


class GhTuiApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "gh-tui"

    # App-level bindings work from any screen (screen bindings for `quit` don't resolve
    # to the app's action, which is why `q` didn't work before).
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("question_mark", "help", "Help"),
        Binding("ctrl+t", "cycle_theme", "Theme"),
    ]

    def __init__(self, theme: str | None = None, start_screen: str | None = None) -> None:
        super().__init__()
        # Register + apply the theme here so its custom CSS variables ($border-dim,
        # $row-selected, ...) are defined when the stylesheet is first parsed.
        register_themes(self)
        self.theme = theme if theme in THEME_NAMES else DEFAULT_THEME
        self._start_screen = start_screen
        # App-wide settings (edited on the Settings screen).
        self.settings: dict = {
            "theme": self.theme,
            "nerd_fonts": False,
            "default_screen": "workspace",
            "confirm_destructive": True,
            "auto_refresh": "30s",
            "per_page": 30,
            "default_owner": "musaJawad004",
            "base_branch": "main",
        }

    def action_quit(self) -> None:
        self.exit()

    def action_help(self) -> None:
        from screens.help import HelpScreen

        if not isinstance(self.screen, HelpScreen):
            self.push_screen(HelpScreen())

    def action_cycle_theme(self) -> None:
        names = THEME_NAMES
        current = self.theme
        i = names.index(current) if current in names else 0
        self.theme = names[(i + 1) % len(names)]
        self.settings["theme"] = self.theme
        refresh_theme = getattr(self.screen, "refresh_theme", None)
        if refresh_theme:
            refresh_theme()
        self.notify(f"Theme: {self.theme}", timeout=1.5)

    def on_mount(self) -> None:
        from screens.main import MainScreen
        from screens.overview import OverviewScreen
        from screens.settings import SettingsScreen
        from screens.splash import SplashScreen

        if self._start_screen == "pull-requests":
            self.push_screen(MainScreen(section=0))
        elif self._start_screen == "workspace":
            self.push_screen(MainScreen())
        elif self._start_screen == "settings":
            self.push_screen(SettingsScreen())
        else:
            # Default: CLI-style boot splash -> focused terminal workspace.
            self.push_screen(
                OverviewScreen() if self._start_screen == "overview" else SplashScreen()
            )


def main() -> None:
    GhTuiApp().run()


if __name__ == "__main__":
    main()
