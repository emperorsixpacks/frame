"""Background job worker — queues generation tasks for the Strands agent."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GenerationJob:
    """A single video generation job."""

    repo_full_name: str
    repo_id: int
    pr_number: int | None
    pr_title: str
    pr_body: str
    pr_diff_url: str | None
    pr_html_url: str
    installation_id: int | None
    is_release: bool = False
    release_tag: str | None = None


# In-memory queue for v1 — swap to Redis/RQ for production
_jobs: list[GenerationJob] = []


async def enqueue_generation(
    repo_full_name: str,
    repo_id: int,
    pr_number: int | None,
    pr_title: str,
    pr_body: str,
    pr_diff_url: str | None,
    pr_html_url: str,
    installation_id: int | None,
    is_release: bool = False,
    release_tag: str | None = None,
) -> None:
    """Enqueue a video generation job."""
    job = GenerationJob(
        repo_full_name=repo_full_name,
        repo_id=repo_id,
        pr_number=pr_number,
        pr_title=pr_title,
        pr_body=pr_body,
        pr_diff_url=pr_diff_url,
        pr_html_url=pr_html_url,
        installation_id=installation_id,
        is_release=is_release,
        release_tag=release_tag,
    )
    _jobs.append(job)
    logger.info("Enqueued generation job for %s (PR #%s)", repo_full_name, pr_number)

    # In v1, run inline — will be async worker in production
    from agent.strands.frame_agent import run_generation

    await run_generation(job)
