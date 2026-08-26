"""themes — the gh-tui theme registry.

In Textual, a theme is a `Theme` object (a named set of colors + a `dark` flag), NOT a
separate CSS file. The app's single stylesheet (`src/app.tcss`) references semantic tokens
like `$primary`, `$surface`, `$success`; swapping `app.theme = "<name>"` re-resolves those
tokens, and every widget restyles instantly.

Planned public API (to implement when we code):

    THEMES: list[Theme]              # all built-in themes (see palettes.py)
    def register_themes(app) -> None # app.register_theme(t) for t in THEMES
    DEFAULT_THEME = "gh-dark"        # applied on first launch, overridable via config.yml

Planned built-in themes (light + dark + extra color schemes):
    gh-dark   (default), gh-light, dracula, nord, gruvbox-dark, solarized-light

See README.md in this folder for the semantic token table and how to add a theme.

TODO: define THEMES, register_themes(), DEFAULT_THEME.

Status: stub — not implemented yet.
"""
