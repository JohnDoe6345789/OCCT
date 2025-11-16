"""Utility CLI for automating python port prompts and PR scaffolding.

The script simulates the workflow requested in Codex tasks: run a prompt,
prepare a pull request description from the current git diff, mark the PR as
approved, and then run the prompt again.  Everything is logged locally so
maintainers can audit what happened without relying on external services.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import subprocess
import textwrap
from typing import Callable, Dict, Iterable, List, Optional

DEFAULT_PROMPT = "Continue with python port until feature parity"
REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = Path(__file__).resolve().with_name("codex_prompts.jsonl")
PR_PATH = Path(__file__).resolve().with_name("codex_pull_request.json")


def _default_git_runner(*args: str) -> str:
    """Run ``git`` with ``args`` inside the repository root."""
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


@dataclass
class PromptEvent:
    prompt: str
    timestamp: str


class PromptLogger:
    """Append prompt runs to a JSONL file for auditing."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, prompt: str, *, timestamp: Optional[datetime] = None) -> PromptEvent:
        current_time = timestamp or datetime.now(timezone.utc)
        event = PromptEvent(
            prompt=prompt,
            timestamp=current_time.isoformat(timespec="seconds"),
        )
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event)) + "\n")
        return event


@dataclass
class PullRequest:
    title: str
    branch: str
    body: str
    approved: bool = False


class PullRequestManager:
    """Create and approve pseudo pull requests using git metadata."""

    def __init__(self, git_runner: Callable[..., str] | None = None) -> None:
        self._git = git_runner or _default_git_runner

    def _gather_diffstat(self) -> str:
        diffstat = self._git("diff", "--stat")
        return diffstat if diffstat else "No changes detected."

    def _gather_status(self) -> str:
        status = self._git("status", "--short")
        return status if status else "Working tree clean."

    def _current_branch(self) -> str:
        return self._git("rev-parse", "--abbrev-ref", "HEAD")

    def create(self, prompt: str, dest: Path) -> PullRequest:
        branch = self._current_branch()
        diffstat = self._gather_diffstat()
        status = self._gather_status()
        title = f"codex: {prompt}"
        body = textwrap.dedent(
            f"""
            Prompt: {prompt}

            Branch: {branch}

            Status:\n{status}

            Diffstat:\n{diffstat}
            """
        ).strip()
        pr = PullRequest(title=title, branch=branch, body=body)
        self._write_pr(dest, pr)
        return pr

    def approve(self, dest: Path) -> PullRequest:
        pr = self._read_pr(dest)
        pr.approved = True
        self._write_pr(dest, pr)
        return pr

    def _write_pr(self, dest: Path, pr: PullRequest) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as handle:
            json.dump(asdict(pr), handle, indent=2)

    def _read_pr(self, dest: Path) -> PullRequest:
        data = json.loads(dest.read_text(encoding="utf-8"))
        return PullRequest(**data)


def run_workflow(prompt: str, *, log_path: Path, pr_path: Path, dry_run: bool) -> Dict[str, object]:
    """Execute the requested prompt/PR cycle."""

    if dry_run:
        return {
            "prompt": prompt,
            "log_path": str(log_path),
            "pr_path": str(pr_path),
            "actions": [
                "run_prompt",
                "create_pull_request",
                "approve_pull_request",
                "run_prompt",
            ],
        }

    logger = PromptLogger(log_path)
    pr_manager = PullRequestManager()

    first_event = logger.append(prompt)
    pr = pr_manager.create(prompt, pr_path)
    approved = pr_manager.approve(pr_path)
    second_event = logger.append(prompt)

    return {
        "first_prompt": asdict(first_event),
        "pull_request": asdict(pr),
        "approved_pull_request": asdict(approved),
        "second_prompt": asdict(second_event),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automate Codex python port workflow")
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt text used when logging the automation steps.",
    )
    parser.add_argument(
        "--log-path",
        default=str(LOG_PATH),
        help="Where to store prompt run history.",
    )
    parser.add_argument(
        "--pr-path",
        default=str(PR_PATH),
        help="Where to store the generated pull request payload.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the actions without touching the filesystem.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_workflow(
        args.prompt,
        log_path=Path(args.log_path),
        pr_path=Path(args.pr_path),
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
