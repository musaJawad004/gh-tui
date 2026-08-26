# Roadmap

> Milestones. Ordered so each version is usable on its own. Nothing is built yet.

## v0.1 — Foundations (GitHub read-only, matches gh-dash's core)

- [ ] Textual app skeleton + global keybindings + status bar
- [ ] `gh` CLI wrapper (`core/gh_client.py`)
- [ ] YAML config loading (tabs = search queries)
- [ ] Top tab bar with counts
- [ ] PR list screen — two-line rows, CI dots, `+/-` diff counts, times
- [ ] PR detail pane — Overview / Checks / Activity sub-tabs
- [ ] Issues screen
- [ ] Repository browser (this is where we pass gh-dash)

## v0.2 — Local Git (the big differentiator)

- [ ] pygit2 read layer (`core/git_local.py`)
- [ ] Branch manager (local + remote, ahead/behind, checkout/create/delete)
- [ ] Commit history + graph
- [ ] Diff viewer (Rich syntax highlighting)
- [ ] Stash management
- [ ] Push / pull / fetch / merge / rebase (with confirmations)
- [ ] Checkout / update PR locally

## v0.3 — CI/CD

- [ ] Actions dashboard (poll `gh run list`)
- [ ] Workflow run detail + job steps
- [ ] CI log explorer
- [ ] Retry failed / retry all jobs
- [ ] Workflow management (enable/disable/dispatch)
- [ ] PR ↔ CI relationship view

## v0.4 — Ops & intelligence

- [ ] Deployments dashboard
- [ ] Releases (create, view, download assets)
- [ ] Secrets / variables management
- [ ] Repo settings
- [ ] Unified search (`/`) across everything
- [ ] Command palette (Ctrl+P)
- [ ] PR risk analysis (no LLM)
- [ ] CI failure diagnosis (no LLM)
- [ ] Repo health

## Future

- [ ] Notifications inbox
- [ ] Repository create / clone / fork UI
- [ ] Optional AI-assisted CI debugging (opt-in, never required)
- [ ] MCP server
- [ ] GitLab / Gitea backends
- [ ] Packaging: `uv tool install`, PyInstaller/Nuitka binaries
