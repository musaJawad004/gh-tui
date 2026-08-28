"""Read-only mutation action palette.

The palette intentionally exposes the workflows without executing GitHub writes yet.
"""
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Input, OptionList, Static
from textual.widgets.option_list import Option

ACTION_FIELDS = {
    "Create branch": (("name", "Branch name", "feature/my-change"), ("base", "Base branch", "main")),
    "Commit changes": (("message", "Commit message", "feat: describe the change"),),
    "Push current branch": (("remote", "Remote", "origin"), ("branch", "Branch", "current branch")),
    "Open pull request": (("title", "PR title", "Describe this pull request"), ("base", "Base branch", "main"), ("head", "Head branch", "current branch")),
    "Open issue": (("title", "Issue title", "Describe the issue"), ("labels", "Labels (optional)", "bug, enhancement")),
    "Checkout branch / pull request": (("target", "Branch or PR number", "feature/my-change or #123"),),
    "Merge pull request": (("pr", "Pull request", "#123"), ("method", "Merge method", "squash")),
    "Create repository": (("name", "Repository name", "my-new-repository"), ("visibility", "Visibility", "private")),
    "Review pull request": (("pr", "Pull request", "#123"),),
    "View CI/CD workflow": (("workflow", "Workflow or run", "build"),),
}


class MutationForm(ModalScreen[None]):
    """A confirmation-shaped form that deliberately performs no mutation."""
    DEFAULT_CSS = """
    MutationForm { align: center middle; background: $background 80%; }
    MutationForm #form-card { width: 76; max-height: 32; padding: 1 2; border: round $primary; background: $surface; }
    MutationForm #form-title { color: $primary; text-style: bold; }
    MutationForm #form-note { margin: 1 0; color: $warning; }
    MutationForm .field-label { color: $text-muted; margin-top: 1; }
    MutationForm Input { width: 1fr; }
    MutationForm #form-actions { height: 3; margin-top: 1; align-horizontal: right; }
    MutationForm Button { margin-left: 1; }
    """
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, action: str) -> None:
        super().__init__()
        self.action_name = action

    def compose(self) -> ComposeResult:
        fields = ACTION_FIELDS.get(self.action_name, ())
        with Vertical(id="form-card"):
            yield Static(self.action_name, id="form-title")
            yield Static("Confirmation form preview · execution is not connected", id="form-note")
            for field_id, label, placeholder in fields:
                yield Static(label, classes="field-label")
                yield Input(placeholder=placeholder, id=f"field-{field_id}")
            with Center(id="form-actions"):
                yield Button("Confirm (UI only)", variant="primary", id="confirm")
                yield Button("Cancel", id="cancel")
            yield Static("No gh command will run · values remain local to this preview", id="form-foot")

    def on_mount(self) -> None:
        first = self.query("Input").first()
        if first:
            first.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.action_cancel()
        elif event.button.id == "confirm":
            self.notify(f"{self.action_name} form confirmed · UI preview only", timeout=2)
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.notify("Use Confirm (UI only) to review this action", timeout=1.5)

    def action_cancel(self) -> None:
        self.dismiss()


class MutationPalette(ModalScreen[None]):
    DEFAULT_CSS = """
    MutationPalette { align: center middle; background: $background 80%; }
    MutationPalette #actions-box { width: 64; max-height: 24; border: solid $primary; background: $surface; }
    MutationPalette #actions-title { height: 3; padding: 1 2; color: $primary; text-style: bold; }
    MutationPalette #actions-list { height: 1fr; padding: 0 1; }
    MutationPalette .option-list--option-highlighted { background: $row-selected; color: $foreground; text-style: bold; }
    MutationPalette #actions-hint { height: 2; padding: 0 2; color: $text-muted; }
    """
    BINDINGS = [("escape", "dismiss", "Close"), ("q", "dismiss", "Close")]

    ACTIONS = (
        "Create branch",
        "Commit changes",
        "Push current branch",
        "Open pull request",
        "Open issue",
        "Checkout branch / pull request",
        "Merge pull request",
        "Run or retry workflow",
        "Create repository",
        "Review pull request",
        "View CI/CD workflow",
    )

    def compose(self) -> ComposeResult:
        with Vertical(id="actions-box"):
            yield Static("Git actions", id="actions-title")
            yield OptionList(*(Option(f"{name}  ·  UI only", id=name) for name in self.ACTIONS), id="actions-list")
            yield Static("Select an action to preview · execution will be connected in a later phase", id="actions-hint")
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        action = str(event.option.id)
        if action == "Run or retry workflow":
            action = "View CI/CD workflow"
        self.app.push_screen(MutationForm(action))
