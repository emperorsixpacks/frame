"""Check Run lifecycle management for Frame."""

from __future__ import annotations

import logging
from typing import Any

from app.github.client import GitHubClient

logger = logging.getLogger(__name__)


class CheckRunManager:
    """Manages the Check Run lifecycle: queued -> in_progress -> completed."""

    CHECK_NAME: str = "Frame — promo video"

    def __init__(self, client: GitHubClient) -> None:
        self.client = client
        self._check_run_id: int | None = None

    async def start(self, repo: str, head_sha: str, title: str, summary: str) -> int:
        """Create a Check Run in queued state. Returns the check_run_id."""
        result: dict[str, Any] = await self.client.create_check_run(
            repo=repo,
            name=self.CHECK_NAME,
            head_sha=head_sha,
            status="queued",
            output={"title": title, "summary": summary},
            actions=[
                {
                    "label": "Approve & post",
                    "description": "Approve the video and post to Facebook",
                    "identifier": "approve_and_post",
                },
                {
                    "label": "Request changes",
                    "description": "Flag for revision — don't post",
                    "identifier": "request_changes",
                },
            ],
        )
        self._check_run_id = result["id"]
        logger.info("Created Check Run %d on %s", self._check_run_id, repo)
        return self._check_run_id

    async def mark_in_progress(self, repo: str) -> None:
        """Transition Check Run to in_progress."""
        if not self._check_run_id:
            raise RuntimeError("No Check Run to update")
        await self.client.update_check_run(
            repo=repo,
            check_run_id=self._check_run_id,
            status="in_progress",
            output={
                "title": "Generating promo video...",
                "summary": "The Frame agent is analyzing the change and rendering a clip.",
            },
        )

    async def complete_success(
        self,
        repo: str,
        title: str,
        summary: str,
        preview_url: str,
        video_url: str,
    ) -> None:
        """Mark Check Run as completed (success) with preview link."""
        if not self._check_run_id:
            raise RuntimeError("No Check Run to update")
        await self.client.update_check_run(
            repo=repo,
            check_run_id=self._check_run_id,
            status="completed",
            conclusion="success",
            output={
                "title": title,
                "summary": summary,
                "text": (
                    f"**Preview:** [Watch video]({preview_url})\n\n"
                    f"**Download:** [mp4]({video_url})\n\n"
                    "---\n"
                    "Use the **Approve & post** action to publish to Facebook, "
                    "or **Request changes** to flag for revision."
                ),
            },
        )

    async def complete_needs_review(
        self, repo: str, title: str, summary: str, preview_url: str
    ) -> None:
        """Mark Check Run as completed (neutral) — needs human review."""
        if not self._check_run_id:
            raise RuntimeError("No Check Run to update")
        await self.client.update_check_run(
            repo=repo,
            check_run_id=self._check_run_id,
            status="completed",
            conclusion="neutral",
            output={
                "title": title,
                "summary": summary,
                "text": (
                    f"**Preview:** [Watch video]({preview_url})\n\n"
                    "The agent generated a clip but isn't confident enough to auto-post. "
                    "Review manually, then approve or request changes."
                ),
            },
        )

    async def complete_skip(self, repo: str, reason: str) -> None:
        """Mark Check Run as completed (success) — change skipped."""
        if not self._check_run_id:
            raise RuntimeError("No Check Run to update")
        await self.client.update_check_run(
            repo=repo,
            check_run_id=self._check_run_id,
            status="completed",
            conclusion="success",
            output={"title": "Skipped — not promo-worthy", "summary": reason},
        )

    async def complete_failure(self, repo: str, error: str) -> None:
        """Mark Check Run as completed (failure)."""
        if not self._check_run_id:
            raise RuntimeError("No Check Run to update")
        await self.client.update_check_run(
            repo=repo,
            check_run_id=self._check_run_id,
            status="completed",
            conclusion="failure",
            output={"title": "Video generation failed", "summary": error},
        )
