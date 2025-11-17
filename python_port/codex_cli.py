#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


CODEX_REFERENCE = "https://github.com/openai/codex?tab=readme-ov-file"
CODEX_API_ENDPOINT = "https://chatgpt.com/codex/api/prompt"
DEFAULT_PROMPT = f"Continue with python port until feature parity using instructions from {CODEX_REFERENCE}"

_SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = _SCRIPT_DIR.parent.parent
LOG_PATH = _SCRIPT_DIR / "codex_prompts.jsonl"
PR_PATH = _SCRIPT_DIR / "codex_pull_request.json"


def run_git(*args: str) -> str:
    """Run a git command and return its output."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or f"git {' '.join(args)} failed")
    return result.stdout.strip()


class PromptLogger:
    """Logger for prompt events."""

    def __init__(self, log_path: str | Path) -> None:
        self.log_path = Path(log_path)

    async def append(self, prompt: str, response: dict[str, Any]) -> dict[str, Any]:
        """Append a prompt event to the log."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        iso = datetime.now().isoformat()
        timestamp = f"{iso.split('.')[0]}Z"
        event = {"prompt": prompt, "timestamp": timestamp, "response": response}
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        return event


class CodexAPIError(Exception):
    """Exception raised for Codex API errors."""

    pass


class CodexAPIClient:
    """Client for interacting with the Codex API."""

    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.endpoint = endpoint or CODEX_API_ENDPOINT
        self.api_key = api_key or os.environ.get("CODEX_API_KEY")

    async def run_prompt(self, prompt: str) -> dict[str, Any]:
        """Send a prompt to the Codex API and return the response."""
        try:
            try:
                import httpx
            except ImportError as e:
                raise CodexAPIError(
                    "httpx is required for Codex API calls. Install it with: pip install httpx"
                ) from e

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    json={"prompt": prompt},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except CodexAPIError:
            raise
        except Exception as e:
            raise CodexAPIError(f"Codex API request failed: {e}") from e


class PullRequestManager:
    """Manager for creating and managing pull request records."""

    def __init__(self, git_runner=None) -> None:
        self.git_runner = git_runner or run_git

    def _current_branch(self) -> str:
        """Get the current git branch."""
        return self.git_runner("rev-parse", "--abbrev-ref", "HEAD")

    def _gather_diffstat(self) -> str:
        """Gather git diff statistics."""
        try:
            diffstat = self.git_runner("diff", "--stat")
            return diffstat or "No changes detected."
        except RuntimeError:
            return "No changes detected."

    def _gather_status(self) -> str:
        """Gather git status."""
        try:
            status = self.git_runner("status", "--short")
            return status or "Working tree clean."
        except RuntimeError:
            return "Working tree clean."

    async def create(self, prompt: str, dest: str | Path) -> dict[str, Any]:
        """Create a pull request record."""
        dest_path = Path(dest)
        branch = self._current_branch()
        diffstat = self._gather_diffstat()
        status = self._gather_status()
        title = f"codex: {prompt}"
        body = "\n".join([
            f"Prompt: {prompt}",
            "",
            f"Branch: {branch}",
            "",
            "Status:",
            status,
            "",
            "Diffstat:",
            diffstat,
            "",
            "Codex reference:",
            CODEX_REFERENCE,
        ])
        pr = {"title": title, "branch": branch, "body": body, "approved": False}
        await self._write_pr(dest_path, pr)
        return pr

    async def approve(self, dest: str | Path) -> dict[str, Any]:
        """Approve a pull request record."""
        dest_path = Path(dest)
        pr = await self._read_pr(dest_path)
        updated = {**pr, "approved": True}
        await self._write_pr(dest_path, updated)
        return updated

    async def _write_pr(self, dest: Path, pr: dict[str, Any]) -> None:
        """Write a pull request record to a file."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(pr, f, indent=2)
            f.write("\n")

    async def _read_pr(self, dest: Path) -> dict[str, Any]:
        """Read a pull request record from a file."""
        with open(dest, encoding="utf-8") as f:
            return json.load(f)


async def run_workflow(
    prompt: str,
    log_path: str | Path,
    pr_path: str | Path,
    dry_run: bool,
    codex_client: Optional[CodexAPIClient] = None,
) -> dict[str, Any]:
    """Run the Codex workflow."""
    if dry_run:
        return {
            "prompt": prompt,
            "log_path": str(log_path),
            "pr_path": str(pr_path),
            "actions": ["run_prompt", "create_pull_request", "approve_pull_request", "run_prompt"],
        }

    logger = PromptLogger(log_path)
    pr_manager = PullRequestManager()
    client = codex_client or CodexAPIClient()

    first_response = await client.run_prompt(prompt)
    first_event = await logger.append(prompt, first_response)
    pr = await pr_manager.create(prompt, pr_path)
    approved = await pr_manager.approve(pr_path)
    second_response = await client.run_prompt(prompt)
    second_event = await logger.append(prompt, second_response)

    return {
        "first_prompt": first_event,
        "pull_request": pr,
        "approved_pull_request": approved,
        "second_prompt": second_event,
    }


async def main(argv: Optional[list[str]] = None) -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Codex automation CLI")
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT, help="Prompt to send to Codex")
    parser.add_argument("--log-path", type=str, default=str(LOG_PATH), help="Path to log file")
    parser.add_argument("--pr-path", type=str, default=str(PR_PATH), help="Path to PR file")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--codex-endpoint", type=str, default=CODEX_API_ENDPOINT, help="Codex API endpoint")

    args = parser.parse_args(argv)

    client = None if args.dry_run else CodexAPIClient(endpoint=args.codex_endpoint)
    result = await run_workflow(
        args.prompt,
        log_path=args.log_path,
        pr_path=args.pr_path,
        dry_run=args.dry_run,
        codex_client=client,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main(sys.argv[1:]))
    except Exception as error:
        message = str(error)
        print(message, file=sys.stderr)
        if hasattr(error, "__traceback__"):
            import traceback

            traceback.print_exc(file=sys.stderr)
        sys.exit(1)
