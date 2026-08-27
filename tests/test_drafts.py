"""Local comment drafts never require a server or database."""

from core.drafts import load_drafts, save_drafts


def test_drafts_round_trip_locally_and_drop_empty_values(tmp_path):
    path = tmp_path / "cache" / "drafts.yml"
    save_drafts(
        {
            "pr:musa/my-app:#142": "Please check @musa",
            "issue:musa/my-app:#85": "Dark theme note",
            "issue:musa/my-app:#84": "",
        },
        path,
    )

    assert load_drafts(path) == {
        "issue:musa/my-app:#85": "Dark theme note",
        "pr:musa/my-app:#142": "Please check @musa",
    }


def test_invalid_draft_cache_falls_back_safely(tmp_path):
    path = tmp_path / "drafts.yml"
    path.write_text("[not: valid", encoding="utf-8")
    assert load_drafts(path) == {}
