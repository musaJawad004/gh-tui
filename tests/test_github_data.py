from pathlib import Path
from subprocess import CompletedProcess

from core import github_data


def test_parse_repository_url_variants():
    assert github_data.parse_repository_url("https://github.com/acme/demo.git") == "acme/demo"
    assert github_data.parse_repository_url("git@github.com:acme/demo") == "acme/demo"
    assert github_data.parse_repository_url("acme/demo") == "acme/demo"
    assert github_data.parse_repository_url("not-a-repo") is None


def test_detect_local_repository(monkeypatch):
    monkeypatch.setattr(
        github_data.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args[0], 0, "https://github.com/acme/demo.git\n", ""),
    )
    assert github_data.detect_local_repository(Path(".")) == "acme/demo"


def test_load_snapshot_uses_read_only_queries(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if args[1:3] == ["api", "repos/acme/demo"]:
            payload = '{"full_name":"acme/demo","name":"demo","default_branch":"main"}'
        elif "pulls?" in args[2]:
            payload = '[{"number":1,"title":"Improve UI","head":{"ref":"feat/ui"},"updated_at":"2026-08-27T00:00:00Z"}]'
        elif "actions/runs" in args[2]:
            payload = '{"workflow_runs":[]}'
        else:
            payload = "[]"
        return CompletedProcess(args, 0, payload, "")

    monkeypatch.setattr(github_data.subprocess, "run", fake_run)
    snapshot = github_data.load_snapshot("https://github.com/acme/demo")
    assert snapshot.name == "acme/demo"
    assert snapshot.pr_rows()[0][0] == "#1"
    assert all(command[0] == "gh" for command in calls)
    assert not any(command[1] in {"create", "edit", "delete", "merge", "push"} for command in calls)
