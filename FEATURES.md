# Feature scope — gh-tui vs gh-dash

The differentiation, in one table. gh-dash is the PR/issue dashboard; gh-tui covers the
whole Git + GitHub + CI/CD workflow.

| Feature                        |       `gh-dash` | gh-tui | Milestone |
| ------------------------------ | --------------: | -----: | --------- |
| Browse PRs                     |               ✅ |      ✅ | v0.1 |
| PR diffs                       |               ✅ |      ✅ | v0.2 |
| Comment/review PRs             |               ✅ |      ✅ | v0.1 |
| PR commits                     |               ✅ |      ✅ | v0.1 |
| Issues                         |               ✅ |      ✅ | v0.1 |
| Notifications                  |               ✅ |      ✅ | Future |
| Checkout/update PR             |               ✅ |      ✅ | v0.2 |
| Create new repository UI       |               ❌ |      ✅ | Future |
| Browse/manage all repositories |               ❌ |      ✅ | v0.1 |
| Full local branch manager      |               ❌ |      ✅ | v0.2 |
| Full local commit manager      |               ❌ |      ✅ | v0.2 |
| Stash management               |               ❌ |      ✅ | v0.2 |
| GitHub Actions dashboard       | ❌ separate tool |      ✅ | v0.3 |
| CI failure/log explorer        |               ❌ |      ✅ | v0.3 |
| Retry failed CI jobs           |      ❌ natively |      ✅ | v0.3 |
| Workflow management            |               ❌ |      ✅ | v0.3 |
| Deployment management          |               ❌ |      ✅ | v0.4 |
| Release management             |               ❌ |      ✅ | v0.4 |
| Secrets / variables            |               ❌ |      ✅ | v0.4 |
| Repo settings                  |               ❌ |      ✅ | v0.4 |
| Unified search                 |         Limited |      ✅ | v0.4 |
| PR + CI relationship           |         Limited |      ✅ | v0.3 |
| CI failure diagnosis           |               ❌ |      ✅ | v0.4 |
| Repo health                    |               ❌ |      ✅ | v0.4 |

## Non-goals (for now)

- Replacing `git` or the `gh` CLI — we give them a better interface, not a rewrite.
- Being a web app — Textual can serve to a browser, but this is a terminal-first tool.
- Requiring an LLM for any core feature.
