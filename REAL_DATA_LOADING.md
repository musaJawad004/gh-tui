# Real data loading

gh-tui loads repository information through the authenticated GitHub CLI (`gh`). The
loader only invokes read-only commands (`gh repo view/list`, `gh pr list`, `gh issue list`,
`gh run list`, `gh release list`, and read-only `gh api` endpoints). It does not create,
edit, merge, push, or delete anything while loading.

If the current directory has no GitHub origin, the app asks for a repository URL (or
`owner/name`) and saves that selection in local settings. Fetched data remains in memory;
settings and local drafts are the only files written by the app.

The future Repo Manager actions (create repo, branches, commits, pushes, pull requests,
and issues) are intentionally presented as disabled/planned UI until their confirmation
flows are implemented.

## Rate-limit policy

The loader follows the same broad pattern used by `gh-dash`: bounded fetches, one shared
process, and a 30-minute in-memory snapshot TTL. Switching screens does not refetch the
same repository. An explicit refresh bypasses the TTL once. Failed authentication is
reported directly (`gh auth login -h github.com`) and rate-limit failures stop rather than
retrying in a loop. The cache is process-local and contains no credentials.
