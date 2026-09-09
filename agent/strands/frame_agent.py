"""Strands agent core — orchestrates the full Frame generation pipeline."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

from strands import Agent
from strands.models import BedrockModel

from agent.config.prompts.loader import render_prompt
from agent.config.settings import AgentConfig, BrandConfig
from agent.tools.integrations import get_code_interpreter_tool, get_github_diff_tool

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result of a video generation run."""

    promo_worthy: bool
    confidence: float
    reason: str
    verdict: str  # "ready_to_post" | "needs_review" | "skip"
    storyboard: dict[str, Any] | None = None
    remotion_code: str | None = None
    video_s3_url: str | None = None
    preview_url: str | None = None
    skip_reason: str | None = None


def _build_agent(config: AgentConfig) -> Agent:
    """Build the Strands Agent with tools and config."""
    model = BedrockModel(model_id=config.model_id)

    code_interpreter = get_code_interpreter_tool()
    github_diff = get_github_diff_tool()

    # Build the system prompt from config + JSON template
    brand_vars = config.brand.to_prompt_vars()
    brand_vars["confidence_threshold"] = str(config.confidence_threshold)

    system_prompt = render_prompt("frame_system", **brand_vars)

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[code_interpreter, github_diff],
    )
    return agent


def _build_judge_agent(config: AgentConfig) -> Agent:
    """Build a lightweight agent for Step 1 (promo-worthiness only)."""
    model = BedrockModel(model_id=config.model_id)
    github_diff = get_github_diff_tool()

    brand_vars = config.brand.to_prompt_vars()
    system_prompt = render_prompt("promo_judge", **brand_vars)

    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[github_diff],
    )


def _parse_json_response(text: str) -> dict[str, Any] | None:
    """Extract the first JSON object from agent response text."""
    # Try to find JSON in code blocks first
    import re

    json_block = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if json_block:
        try:
            return json.loads(json_block.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find a raw JSON object
    brace_start = text.find("{")
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start : i + 1])
                    except json.JSONDecodeError:
                        break
    return None


async def run_generation(job: Any) -> GenerationResult:
    """Run the full generation pipeline for a webhook job.

    This is the main entry point called by the worker after a webhook event.
    """
    logger.info("Starting generation for %s PR#%s", job.repo_full_name, job.pr_number)

    config = AgentConfig()

    # Build changed files summary for the judge prompt
    changed_summary = f"PR #{job.pr_number}: {job.pr_title}"
    if job.pr_body:
        changed_summary += f"\n{job.pr_body[:500]}"

    # Step 1: Judge promo-worthiness
    brand_vars = config.brand.to_prompt_vars()
    brand_vars["pr_title"] = job.pr_title
    brand_vars["pr_body"] = job.pr_body or ""
    brand_vars["changed_files_summary"] = changed_summary
    brand_vars["diff_stats"] = f"Source: {job.pr_diff_url or 'N/A'}"

    judge_prompt = render_prompt("promo_judge", **brand_vars)
    judge_agent = _build_judge_agent(config)

    logger.info("Step 1: Judging promo-worthiness...")
    judge_response = judge_agent(judge_prompt)
    judge_text = str(judge_response)
    judgment = _parse_json_response(judge_text)

    if not judgment or not judgment.get("promo_worthy"):
        reason = judgment.get("reason", "Not promo-worthy") if judgment else "Could not parse judgment"
        logger.info("Skipping: %s", reason)
        return GenerationResult(
            promo_worthy=False,
            confidence=0.0,
            reason=reason,
            verdict="skip",
            skip_reason=reason,
        )

    logger.info("Promo-worthy (confidence=%.2f). Proceeding to storyboard...", judgment.get("confidence", 0))

    # Step 2-4: Full pipeline (storyboard + render + confidence)
    full_agent = _build_agent(config)
    full_prompt = render_prompt("frame_system", **brand_vars)

    logger.info("Steps 2-4: Storyboard + render + confidence check...")
    full_response = full_agent(full_prompt)
    full_text = str(full_response)
    result = _parse_json_response(full_text)

    if not result:
        logger.error("Failed to parse agent response")
        return GenerationResult(
            promo_worthy=True,
            confidence=0.0,
            reason="Agent response could not be parsed",
            verdict="needs_review",
        )

    return GenerationResult(
        promo_worthy=result.get("promo_worthy", True),
        confidence=result.get("brand_confidence", result.get("confidence", 0)),
        reason=result.get("reason", ""),
        verdict=result.get("verdict", "needs_review"),
        storyboard=result.get("storyboard"),
        remotion_code=result.get("remotion_code"),
        video_s3_url=result.get("video_s3_url"),
        skip_reason=result.get("skip_reason"),
    )
