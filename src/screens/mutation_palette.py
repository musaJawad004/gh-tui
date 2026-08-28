"""Read-only mutation action palette.

The palette intentionally exposes the workflows without executing GitHub writes yet.
"""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, OptionList, Static
from textual.widgets.option_list import Option


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
    )

    def compose(self) -> ComposeResult:
        with Vertical(id="actions-box"):
            yield Static("Git actions", id="actions-title")
            yield OptionList(*(Option(f"{name}  ·  UI only", id=name) for name in self.ACTIONS), id="actions-list")
            yield Static("Select an action to preview · execution will be connected in a later phase", id="actions-hint")
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.notify(f"{event.option.id} is staged in the UI · no GitHub changes made", timeout=2)
        self.dismiss()
