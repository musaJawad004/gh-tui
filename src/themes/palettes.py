"""palettes — color values for each built-in theme.

Each theme is one `Theme(...)` with Textual's base colors (primary, secondary, background,
surface, panel, success, warning, error, accent, foreground, `dark`) plus a `variables`
dict for gh-tui's own semantic tokens (see the token table in README.md), e.g.:

    Theme(
        name="gh-dark",
        dark=True,
        primary="#4C9EEB",
        background="#0D1117",
        surface="#161B22",
        success="#3FB950",     # CI ✓ dot
        error="#F85149",       # CI ✗ dot
        ...
        variables={
            "diff-add": "#3FB950",
            "diff-remove": "#F85149",
            "pr-open": "#3FB950",
            "pr-merged": "#A371F7",
            "pr-draft": "#8B949E",
            "row-selected": "#1F2937",
        },
    )

Planned themes: gh-dark (default), gh-light, dracula, nord, gruvbox-dark, solarized-light.
Light and dark variants must both define every token so the UI is legible in either.

TODO: define one Theme per palette and collect them into themes.THEMES.

Status: stub — not implemented yet.
"""
