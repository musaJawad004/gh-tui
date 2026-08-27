# Theming

gh-tui ships **20 themes** — curated dark terminal schemes — selectable
from the visual Settings picker, `ctrl+t`, or `--theme NAME`. This folder defines them.

## How it works (Textual model)

A theme is **not** a separate CSS file. It's a `Theme` object: a named set of colors plus a
`dark: bool`. The whole app uses **one** stylesheet (`src/app.tcss`) written against
*semantic tokens* (`$primary`, `$surface`, `$success`, …). Switching theme re-resolves
those tokens and every widget restyles instantly:

```python
app.theme = "dracula"  # done — no CSS reload, no per-widget code
```

So: **colors live here, layout/structure lives in `src/app.tcss`.** Never hardcode a hex
value in a widget — always reference a token.

## Files

| File | Role |
|------|------|
| `__init__.py` | theme registry + `register_themes(app)` + `DEFAULT_THEME` |
| `palettes.py` | one `Theme(...)` per built-in theme (the actual colors) |
| `README.md` | this file |

## Semantic tokens

Every theme (light and dark) must define all of these so the UI stays legible in both:

| Token | Used for |
|-------|----------|
| `$background` | app background |
| `$surface` | panels / cards |
| `$panel` | secondary panels, detail pane |
| `$foreground` | primary text |
| `$text-muted` | secondary text, timestamps |
| `$primary` | accent, active tab, links (repo names) |
| `$secondary` | secondary accent |
| `$success` | CI ✓ dot, healthy status |
| `$warning` | pending / queued status |
| `$error` | CI ✗ dot, failures |
| `$row-selected` | highlighted table row |
| `$diff-add` | `+` additions |
| `$diff-remove` | `-` deletions |
| `$pr-open` / `$pr-merged` / `$pr-closed` / `$pr-draft` | PR state colors |

## Built-in themes

Run `gh-tui --list-themes` for the authoritative list:

`gh-flow`, `linear`, `codex`, `claude`, `notion`, `apple`, `github-dark`, `tokyo-night`,
`catppuccin-mocha`, `gruvbox-dark`, `dracula`, `nord`, `one-dark`, `solarized-dark`,
`monokai`, `ayu-dark`, `rose-pine`, `kanagawa`, `matrix`, and `mono`.

## Add a theme

1. Add a `Theme(...)` in `palettes.py` defining every token above.
2. Append it to `THEMES` in `__init__.py`.
3. Users select it with `theme: <name>` in `config.yml`.

That's it — no CSS changes needed.
