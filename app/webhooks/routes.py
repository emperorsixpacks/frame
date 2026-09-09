"""Webhook route handlers for GitHub events."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

logger = logging.getLogger(__name__)
router = APIRouter()


def _verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature."""
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_github_delivery: str = Header(...),
    x_hub_signature_256: str = Header(...),
) -> dict[str, str]:
    """Receive GitHub webhook events and dispatch to the Frame agent."""
    body = await request.body()

    secret: str = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    if secret and not _verify_signature(body, x_hub_signature_256, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload: dict[str, Any] = __import__("json").loads(body)

    logger.info(
        "Received webhook: event=%s delivery=%s action=%s",
        x_github_event,
        x_github_delivery,
        payload.get("action"),
    )

    if x_github_event == "pull_request":
        await _handle_pull_request(payload)
    elif x_github_event == "release":
        await _handle_release(payload)
    else:
        logger.debug("Ignoring event: %s", x_github_event)

    return {"status": "ok"}


async def _handle_pull_request(payload: dict[str, Any]) -> None:
    """Handle pull_request events — trigger generation on merge."""
    if payload.get("action") != "closed":
        return

    pr: dict[str, Any] | None = payload.get("pull_request")
    if not pr or not pr.get("merged"):
        return

    repo: dict[str, Any] | None = payload.get("repository")
    if not repo:
        return

    # Check for frame:generate label
    labels: list[str] = [l["name"] for l in pr.get("labels", [])]
    if labels and "frame:generate" not in labels:
        logger.info("PR %s has labels %s, skipping (no frame:generate)", pr["number"], labels)
        return

    logger.info(
        "PR merged: %s#%d — dispatching to agent",
        repo["full_name"],
        pr["number"],
    )

    from app.worker import enqueue_generation

    await enqueue_generation(
        repo_full_name=repo["full_name"],
        repo_id=repo["id"],
        pr_number=pr["number"],
        pr_title=pr["title"],
        pr_body=pr.get("body", ""),
        pr_diff_url=pr["diff_url"],
        pr_html_url=pr["html_url"],
        installation_id=payload.get("installation", {}).get("id"),
    )


async def _handle_release(payload: dict[str, Any]) -> None:
    """Handle release published events."""
    if payload.get("action") != "published":
        return

    release: dict[str, Any] | None = payload.get("release")
    if not release:
        return

    repo: dict[str, Any] | None = payload.get("repository")
    if not repo:
        return

    logger.info(
        "Release published: %s %s — dispatching to agent",
        repo["full_name"],
        release.get("tag_name", "unknown"),
    )

    from app.worker import enqueue_generation

    await enqueue_generation(
        repo_full_name=repo["full_name"],
        repo_id=repo["id"],
        pr_number=None,
        pr_title=release.get("name", release.get("tag_name", "")),
        pr_body=release.get("body", ""),
        pr_diff_url=None,
        pr_html_url=release.get("html_url", ""),
        installation_id=payload.get("installation", {}).get("id"),
        is_release=True,
        release_tag=release.get("tag_name"),
    )
