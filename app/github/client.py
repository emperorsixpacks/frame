"""GitHub API client for Check Runs and PR interactions."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GITHUB_API: str = "https://api.github.com"


class GitHubClient:
    """Minimal GitHub API client for Checks and content access."""

    def __init__(self, installation_id: int) -> None:
        self.installation_id = installation_id
        self._token: str | None = None

    async def _get_token(self) -> str:
        """Get or refresh the installation access token."""
        if self._token:
            return self._token
        self._token = os.environ.get("GITHUB_INSTALLATION_TOKEN", "")
        return self._token

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any] | list[Any] | None:
        token = await self._get_token()
        headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method, f"{GITHUB_API}{path}", headers=headers, **kwargs
            )
            resp.raise_for_status()
            return resp.json() if resp.content else None

    async def get_pr_files(self, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """Get the list of files changed in a PR."""
        data = await self._request("GET", f"/repos/{repo}/pulls/{pr_number}/files")
        return data if isinstance(data, list) else []

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """Get the raw diff for a PR."""
        token = await self._get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3.diff",
                },
            )
            resp.raise_for_status()
            return resp.text

    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str = "queued",
        output: dict[str, Any] | None = None,
        actions: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Create a new Check Run."""
        payload: dict[str, Any] = {"name": name, "head_sha": head_sha, "status": status}
        if output:
            payload["output"] = output
        if actions:
            payload["actions"] = actions
        return await self._request("POST", f"/repos/{repo}/check-runs", json=payload)  # type: ignore[return-value]

    async def update_check_run(
        self,
        repo: str,
        check_run_id: int,
        status: str | None = None,
        conclusion: str | None = None,
        output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an existing Check Run."""
        payload: dict[str, Any] = {}
        if status:
            payload["status"] = status
        if conclusion:
            payload["conclusion"] = conclusion
        if output:
            payload["output"] = output
        return await self._request(  # type: ignore[return-value]
            "PATCH", f"/repos/{repo}/check-runs/{check_run_id}", json=payload
        )

    async def add_pr_comment(self, repo: str, pr_number: int, body: str) -> dict[str, Any]:
        """Add a comment to a PR."""
        return await self._request(  # type: ignore[return-value]
            "POST",
            f"/repos/{repo}/issues/{pr_number}/comments",
            json={"body": body},
        )
