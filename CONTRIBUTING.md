# Contributing to gh-tui

Thanks for your interest! gh-tui is open source (MIT) and contributions are welcome.

> ⚠️ The project is currently a **pre-code scaffold** — structure, docs, and empty module
> stubs only. Early contributions are mostly about shaping architecture and picking off
> [`ROADMAP.md`](ROADMAP.md) items.

## Dev setup

```bash
git clone https://github.com/musaJawad004/gh-tui.git
cd gh-tui

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"            # editable install + dev tools
```

You'll also need:

- The [`gh` CLI](https://cli.github.com/), authenticated: `gh auth login`
- A **Nerd Font** set in your terminal (for the glyphs)

## Running (once there's code)

```bash
python src/            # runs src/__main__.py
# or, after `pip install -e .`:
gh-tui
```

## Project layout

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full picture. Short version:

```
src/
├── app.py        # main Textual App
├── config.py     # YAML config
├── core/         # data layer (gh CLI, GraphQL, local git, cache)
├── models/       # typed dataclasses
├── screens/      # one screen per major view
├── widgets/      # reusable widgets
├── analysis/     # no-LLM heuristics (risk, CI diagnosis, health)
└── themes/       # light/dark + color-scheme themes
```

## Conventions

- **Format & lint** with `ruff` before pushing: `ruff format . && ruff check .`
- **Tests** with `pytest`. Keep the structure/smoke tests green.
- **Commits**: short imperative subject (`add branch checkout`, `fix CI dot color`).
- **Branches**: `feat/…`, `fix/…`, `docs/…`. Open a PR against `main`.
- **No LLM in core features.** AI stays an optional, opt-in layer.
- **Safe by default**: destructive actions must have a confirm step.

## Good first areas

- v0.1 items in [`ROADMAP.md`](ROADMAP.md) (PR list, detail pane, repo browser)
- Theme palettes in `src/themes/`
- Docs & examples

Open an issue to discuss anything bigger before you build it. 🙌
