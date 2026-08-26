# Architecture

> Planning document. Nothing here is implemented yet.

## Guiding principles

1. **Terminal first, keyboard first** — everything doable without a browser, in a few keystrokes.
2. **Useful without AI** — core Git/GitHub/CI never depends on an LLM. AI is an optional layer later.
3. **Feels instant** — the UI never blocks on the network. Background workers + cache.
4. **Safe by default** — destructive ops (delete branch, force-push, merge) require confirmation.

## Layers

```
┌───────────────────────────────────────────────┐
│  Textual App (screens + widgets + .tcss theme) │   ← presentation
├───────────────────────────────────────────────┤
│  Cache / background refresh (asyncio workers)  │   ← keeps UI instant
├───────────────────────────────────────────────┤
│  Data sources                                  │
│   • gh_client  → shells out to `gh` CLI        │   ← GitHub (MVP)
│   • graphql    → `gh api graphql` queries      │   ← dense PR/CI/review pulls
│   • git_local  → pygit2 (reads) + `git` (writes)│  ← local repo
├───────────────────────────────────────────────┤
│  Models (typed dataclasses)                    │   ← normalize both sources
└───────────────────────────────────────────────┘
```

## Why these choices

| Concern | Decision | Reason |
|---|---|---|
| TUI framework | **Textual** | Reactive, async, CSS-styled, mouse, command palette built in. Direct Bubble Tea analog. |
| GitHub access (MVP) | **`gh` CLI shell-out** | Inherits auth/token refresh/enterprise for free. Same approach gh-dash uses. |
| GitHub access (later) | **`gh api graphql` / ghapi** | One GraphQL query pulls PR + CI + reviews + conflicts together. Migrate hot paths only. |
| Local git reads | **pygit2** | libgit2 bindings, no subprocess-per-command, fast for log/diff/branches. |
| Local git writes | **shell out to `git`** | Matching git's exact rebase/cherry-pick/stash behavior is safer than reimplementing. |
| Config | **YAML** (gh-dash style) | Tabs = named `gh` search queries. Flexible with near-zero hardcoding. |

## Known hard parts (call them out early)

1. **The GitHub/Git surface is the real project**, not the TUI. Pagination, rate limits,
   conflict detection, review threads, merge strategies.
2. **Caching + background refresh** must be designed in from day one, not bolted on.
3. **Polling, not push** — GitHub has no websockets for run status/logs. Poll with backoff.
4. **Commit-graph DAG** rendering (the `●───` lines) is fiddly in a terminal.
5. **Two-line table rows** (repo line + title line) need a fixed row height or a custom
   `ListView` row widget — Textual's `DataTable` is single-line by default.
6. **Nerd Fonts required** for the glyphs — a font/install concern, not a code concern.
7. **Distribution** — Python has no single static binary. Plan `pipx` / `uv tool install`,
   or `PyInstaller` / `Nuitka` for a binary.

## Package layout

Flat `src/` layout — no nested package folder. Modules and packages sit directly under
`src/`, so imports read `from core.gh_client import ...`. Run in dev with `python src/`
(which executes `src/__main__.py` with `src/` on the path).

```
gh-tui/
├── README.md · ARCHITECTURE.md · ROADMAP.md · FEATURES.md   # docs live at root (no docs/ folder)
├── CONTRIBUTING.md · CHANGELOG.md · LICENSE
├── pyproject.toml · requirements*.txt · .python-version
├── tests/                # structure + smoke tests
└── src/
    ├── __main__.py       # entry point — `python src/`
    ├── app.py            # main Textual App: mounts screens, global keybindings
    ├── app.tcss          # app-wide stylesheet (layout only; colors via theme tokens)
    ├── config.py         # load ~/.config/gh-tui/config.yml (tabs, theme, keys)
    ├── core/             # data layer (no UI)
    │   ├── gh_client.py  # async wrapper around the `gh` CLI
    │   ├── graphql.py    # GraphQL query strings + runners
    │   ├── git_local.py  # pygit2 reads + `git` subprocess writes
    │   └── cache.py      # background refresh, TTL cache, worker scheduling
    ├── models/           # typed dataclasses shared across sources
    ├── screens/          # one Screen per major view (PRs, repos, branches, actions…)
    ├── widgets/          # reusable widgets (pr_table, detail_pane, tab_bar, status_bar…)
    ├── analysis/         # no-LLM heuristics (pr_risk, ci_failure, repo_health)
    └── themes/           # multiple themes: light / dark / color schemes (see themes/README.md)
```
