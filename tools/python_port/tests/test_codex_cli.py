import json
from datetime import datetime
from pathlib import Path

import pytest

from tools.python_port import codex_cli


def test_prompt_logger_appends_json(tmp_path: Path):
    log_path = tmp_path / "prompts.jsonl"
    logger = codex_cli.PromptLogger(log_path)

    first = logger.append("test prompt", timestamp=datetime(2024, 1, 1, 0, 0, 0))
    second = logger.append("another", timestamp=datetime(2024, 1, 1, 0, 0, 1))

    contents = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 2
    assert json.loads(contents[0]) == {
        "prompt": first.prompt,
        "timestamp": first.timestamp,
    }
    assert json.loads(contents[1]) == {
        "prompt": second.prompt,
        "timestamp": second.timestamp,
    }


def test_pull_request_manager_creates_and_approves(tmp_path: Path):
    calls = []

    def fake_git_runner(*args: str) -> str:
        calls.append(args)
        mapping = {
            ("rev-parse", "--abbrev-ref", "HEAD"): "feature/codex",
            ("diff", "--stat"): "1 file changed, 2 insertions(+)",
            ("status", "--short"): " M tools/python_port/new_file.py",
        }
        return mapping.get(tuple(args), "")

    manager = codex_cli.PullRequestManager(git_runner=fake_git_runner)
    pr_path = tmp_path / "pr.json"

    pr = manager.create("demo prompt", pr_path)
    assert pr.title == "codex: demo prompt"
    assert "demo prompt" in pr.body
    assert pr.branch == "feature/codex"
    assert pr_path.exists()

    approved = manager.approve(pr_path)
    assert approved.approved is True
    stored = json.loads(pr_path.read_text(encoding="utf-8"))
    assert stored["approved"] is True

    assert ("rev-parse", "--abbrev-ref", "HEAD") in calls
    assert ("diff", "--stat") in calls
    assert ("status", "--short") in calls


@pytest.mark.parametrize("dry_run", [True, False])
def test_run_workflow_paths(tmp_path: Path, monkeypatch, dry_run: bool):
    prompt = "demo"
    log_path = tmp_path / "log.jsonl"
    pr_path = tmp_path / "pr.json"

    events = []

    class DummyLogger(codex_cli.PromptLogger):
        def __init__(self, path: Path):
            super().__init__(path)

        def append(self, prompt: str, *, timestamp=None):
            event = super().append(prompt, timestamp=timestamp)
            events.append(event.prompt)
            return event

    class DummyPRManager(codex_cli.PullRequestManager):
        def __init__(self):
            super().__init__(git_runner=lambda *args: "dummy")

        def create(self, prompt: str, dest: Path):
            pr = codex_cli.PullRequest(title=prompt, branch="main", body="body")
            self._write_pr(dest, pr)
            return pr

        def approve(self, dest: Path):
            pr = self._read_pr(dest)
            pr.approved = True
            self._write_pr(dest, pr)
            return pr

    monkeypatch.setattr(codex_cli, "PromptLogger", DummyLogger)
    monkeypatch.setattr(codex_cli, "PullRequestManager", DummyPRManager)

    result = codex_cli.run_workflow(
        prompt,
        log_path=log_path,
        pr_path=pr_path,
        dry_run=dry_run,
    )

    if dry_run:
        assert result["actions"] == [
            "run_prompt",
            "create_pull_request",
            "approve_pull_request",
            "run_prompt",
        ]
    else:
        assert events == [prompt, prompt]
        assert log_path.exists()
        assert pr_path.exists()
        assert result["approved_pull_request"]["approved"] is True
