"""First-run repository confirmation; only the chosen config value is persisted."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from core.github_data import parse_repository_url


class RepoSetupScreen(ModalScreen[str | None]):
    """Ask for a repository when the current directory has no GitHub origin."""

    DEFAULT_CSS = """
    RepoSetupScreen { align: center middle; background: $background 85%; }
    RepoSetupScreen #repo-card { width: 72; height: auto; padding: 1 2; border: round $primary; background: $surface; }
    RepoSetupScreen #repo-title { color: $primary; text-style: bold; }
    RepoSetupScreen #repo-help { margin: 1 0; color: $text-muted; }
    RepoSetupScreen #repo-url { width: 1fr; }
    RepoSetupScreen #repo-actions { height: 3; margin-top: 1; align-horizontal: right; }
    RepoSetupScreen Button { margin-left: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Middle(), Center(), Vertical(id="repo-card"):
            yield Static(Text("Connect a repository", style="bold"), id="repo-title")
            yield Static(
                "No GitHub repository is configured for this directory. Enter a URL or owner/name to load read-only data.",
                id="repo-help",
            )
            yield Input(placeholder="https://github.com/owner/repository", id="repo-url")
            with Center(id="repo-actions"):
                yield Button("Confirm repository", variant="primary", id="confirm")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#repo-url", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._confirm(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self._confirm(self.query_one("#repo-url", Input).value)
        elif event.button.id == "cancel":
            self.action_cancel()

    def _confirm(self, value: str) -> None:
        repository = parse_repository_url(value)
        if not repository:
            self.notify("Enter a valid GitHub URL or owner/name", severity="error")
            return
        self.dismiss(repository)

    def action_cancel(self) -> None:
        self.dismiss(None)
