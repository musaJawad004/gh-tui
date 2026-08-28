"""GhTuiApp — the Textual application.

Registers themes, applies the default (or a requested) theme, and opens the requested
start screen (the focused workspace by default).
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App
from textual.binding import Binding

from config import load_settings, save_settings
from core.drafts import load_drafts, save_drafts
from core.github_data import (
    GhCliError,
    GitHubSnapshot,
    detect_local_repository,
    load_commit_detail,
    load_issue_detail,
    load_pull_request_detail,
    load_snapshot,
    load_workflow_detail,
    parse_repository_url,
)
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

    def __init__(
        self,
        theme: str | None = None,
        start_screen: str | None = None,
        config_path: Path | None = None,
        drafts_path: Path | None = None,
    ) -> None:
        super().__init__()
        # Register + apply the theme here so its custom CSS variables ($border-dim,
        # $row-selected, ...) are defined when the stylesheet is first parsed.
        register_themes(self)
        self._config_path = config_path
        self._drafts_path = drafts_path
        self.settings = load_settings(config_path)
        self.comment_drafts = load_drafts(drafts_path)
        saved_cwd = self.settings.get("repository_cwd", "")
        self.repository = (
            parse_repository_url(self.settings.get("repository", ""))
            if saved_cwd and Path(saved_cwd).expanduser().resolve() == Path.cwd().resolve()
            else None
        )
        self.github_snapshot = None
        self.data_loading = False
        self.data_error: str | None = None
        self.detail_data: dict | None = None
        self.detail_kind: str | None = None
        self.detail_loading = False
        saved_theme = self.settings.get("theme")
        requested_theme = theme if theme in THEME_NAMES else saved_theme
        self.theme = requested_theme if requested_theme in THEME_NAMES else DEFAULT_THEME
        self.settings["theme"] = self.theme
        self._start_screen = start_screen

    def action_quit(self) -> None:
        self.persist_settings()
        self.persist_comment_drafts()
        self.exit()

    def persist_settings(self) -> bool:
        """Save settings without allowing a filesystem problem to crash the TUI."""
        try:
            save_settings(self.settings, self._config_path)
        except OSError:
            return False
        return True

    def persist_comment_drafts(self) -> bool:
        """Save local drafts without allowing a cache problem to crash the TUI."""
        try:
            save_drafts(self.comment_drafts, self._drafts_path)
        except OSError:
            return False
        return True

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
        self.persist_settings()
        refresh_theme = getattr(self.screen, "refresh_theme", None)
        if refresh_theme:
            refresh_theme()
        self.notify(f"Theme: {self.theme}", timeout=1.5)

    def on_mount(self) -> None:
        from screens.repo_setup import RepoSetupScreen
        from screens.settings import SettingsScreen
        from screens.splash import SplashScreen

        local_repository = detect_local_repository(Path.cwd())
        if local_repository:
            self.repository = local_repository
            self.settings["repository"] = local_repository
            self.settings["repository_cwd"] = str(Path.cwd().resolve())
            self.persist_settings()

        if not self.repository:
            self.push_screen(RepoSetupScreen(), self._repository_confirmed)
            return

        if self._start_screen == "settings":
            self.push_screen(SettingsScreen())
        elif self._start_screen == "pull-requests":
            from screens.main import MainScreen
            self.push_screen(MainScreen(section=0))
        elif self._start_screen == "workspace":
            from screens.main import MainScreen
            self.push_screen(MainScreen())
        elif self._start_screen == "overview":
            from screens.overview import OverviewScreen
            self.push_screen(OverviewScreen())
        else:
            # Always gate repository screens behind the animated, truthful loader.
            destination = self.settings.get("default_screen", "overview")
            self.push_screen(SplashScreen(destination=destination))
        self.begin_data_load()

    def begin_data_load(self, *, force: bool = False) -> None:
        """Start read-only GitHub loading in a worker; results stay in memory."""
        if self.data_loading or not self.repository:
            return
        self.data_loading = True
        self.data_error = None
        self.run_worker(lambda: self._load_data(force=force), thread=True, exclusive=True)

    def _load_data(self, *, force: bool = False) -> None:
        try:
            snapshot = load_snapshot(self.repository, cwd=Path.cwd(), limit=self.settings.get("per_page", 30), force=force)
        except GhCliError as exc:
            self.call_from_thread(self._data_failed, str(exc))
            return
        self.call_from_thread(self._data_loaded, snapshot)

    def _data_loaded(self, snapshot) -> None:
        self.github_snapshot = snapshot
        self.data_loading = False
        self.data_error = None
        refresh = getattr(self.screen, "refresh_data", None)
        if refresh:
            refresh()
        self.notify(f"Loaded {snapshot.name} · read-only data", timeout=2)

    def _data_failed(self, error: str) -> None:
        # Keep the UI truthful after a rate-limit/offline failure: an empty snapshot
        # makes every panel render an explicit empty state instead of demo fixtures.
        self.github_snapshot = GitHubSnapshot(repository={"nameWithOwner": self.repository or ""})
        self.data_loading = False
        self.data_error = error
        refresh = getattr(self.screen, "refresh_data", None)
        if refresh:
            refresh()
        self.notify(f"GitHub data unavailable · {error}", severity="warning", timeout=3)

    def _repository_confirmed(self, value: str | None) -> None:
        if not value:
            self.exit()
            return
        self.repository = value
        self.settings["repository"] = value
        self.settings["repository_cwd"] = str(Path.cwd().resolve())
        self.persist_settings()
        self.begin_data_load()

    def begin_detail_load(self, kind: str, number: int | str) -> None:
        """Fetch one PR/issue detail only when the user opens it."""
        if self.detail_loading or not self.repository:
            return
        self.detail_loading = True
        self.detail_data = None
        self.detail_kind = kind
        self.run_worker(lambda: self._load_detail(kind, number), thread=True, exclusive=False)

    def _load_detail(self, kind: str, number: int) -> None:
        try:
            loader = {"pr": load_pull_request_detail, "issue": load_issue_detail, "workflow": load_workflow_detail, "commit": load_commit_detail}[kind]
            detail = loader(self.repository, number, cwd=Path.cwd())
        except GhCliError as exc:
            self.call_from_thread(self._detail_failed, str(exc))
            return
        self.call_from_thread(self._detail_loaded, detail)

    def _detail_loaded(self, detail: dict) -> None:
        self.detail_data = detail
        self.detail_loading = False
        refresh = getattr(self.screen, "refresh_data", None)
        if refresh:
            refresh()

    def _detail_failed(self, error: str) -> None:
        self.detail_loading = False
        self.data_error = error
        refresh = getattr(self.screen, "refresh_data", None)
        if refresh:
            refresh()

def main() -> None:
    GhTuiApp().run()


if __name__ == "__main__":
    main()
