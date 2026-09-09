"""Agent tools — integrations the Strands agent can call."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3
import httpx

logger = logging.getLogger(__name__)


def get_code_interpreter_tool() -> callable[..., str]:
    """Create a tool that executes code inside AgentCore Code Interpreter.

    Returns a callable that the Strands agent can invoke as a tool.
    """

    def code_interpreter(code: str, description: str = "") -> str:
        """Execute code in an AgentCore Code Interpreter sandbox.

        Args:
            code: Bash/code to execute in the sandbox session.
            description: Human-readable description of what this code does.

        Returns:
            JSON string with execution result, output, and artifact paths.
        """
        client = boto3.client(
            "bedrock-agentcore",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        interpreter_id: str = os.environ["AGENTCORE_CODE_INTERPRETER_ID"]

        try:
            session = client.create_code_interpreter_session(
                codeInterpreterIdentifier=interpreter_id,
                sessionTimeoutSeconds=300,
            )
            session_id: str = session["sessionId"]
            logger.info("Created Code Interpreter session: %s", session_id)

            result: dict[str, Any] = client.run_code_interpreter_code(
                codeInterpreterIdentifier=interpreter_id,
                sessionId=session_id,
                code=code,
                language="bash",
            )

            output: str = result.get("output", "")
            files: list[str] = result.get("files", [])

            video_path: str | None = None
            for f in files:
                if f.endswith(".mp4"):
                    video_path = f
                    break

            s3_url: str | None = None
            if video_path:
                s3_url = _upload_to_s3(video_path, session_id)

            return json.dumps(
                {
                    "status": "success",
                    "output": output,
                    "files": files,
                    "video_s3_url": s3_url,
                    "session_id": session_id,
                }
            )

        except Exception as e:
            logger.error("Code Interpreter execution failed: %s", e)
            return json.dumps({"status": "error", "error": str(e)})

    return code_interpreter


def _upload_to_s3(local_path: str, session_id: str) -> str | None:
    """Upload a file to S3 and return the presigned URL."""
    try:
        s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        bucket: str = os.environ.get("S3_BUCKET", "frame-renders")
        key = f"renders/{session_id}/promo.mp4"

        s3.upload_file(local_path, bucket, key)

        url: str = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )
        return url
    except Exception as e:
        logger.error("S3 upload failed: %s", e)
        return None


def get_github_diff_tool() -> callable[..., str]:
    """Create a tool that fetches PR diffs from GitHub.

    Returns a callable that the Strands agent can invoke as a tool.
    """

    def fetch_github_diff(repo_full_name: str, pr_number: int) -> str:
        """Fetch the diff and metadata for a GitHub PR.

        Args:
            repo_full_name: Owner/repo format (e.g., "acme/widget").
            pr_number: The PR number to fetch.

        Returns:
            JSON string with diff content and metadata.
        """
        token: str = os.environ.get("GITHUB_INSTALLATION_TOKEN", "")
        headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
        base = f"https://api.github.com/repos/{repo_full_name}"

        try:
            pr_resp = httpx.get(f"{base}/pulls/{pr_number}", headers=headers)
            pr_resp.raise_for_status()
            pr_data: dict[str, Any] = pr_resp.json()

            files_resp = httpx.get(
                f"{base}/pulls/{pr_number}/files",
                headers=headers,
                params={"per_page": 100},
            )
            files_resp.raise_for_status()
            files: list[dict[str, Any]] = files_resp.json()

            diff_resp = httpx.get(
                f"{base}/pulls/{pr_number}",
                headers={**headers, "Accept": "application/vnd.github.v3.diff"},
            )
            diff_resp.raise_for_status()

            return json.dumps(
                {
                    "title": pr_data["title"],
                    "body": pr_data.get("body", ""),
                    "user": pr_data["user"]["login"],
                    "labels": [l["name"] for l in pr_data.get("labels", [])],
                    "changed_files": [
                        {
                            "filename": f["filename"],
                            "status": f["status"],
                            "additions": f["additions"],
                            "deletions": f["deletions"],
                        }
                        for f in files
                    ],
                    "diff": diff_resp.text,
                    "html_url": pr_data["html_url"],
                    "head_sha": pr_data["head"]["sha"],
                }
            )
        except Exception as e:
            logger.error("GitHub diff fetch failed: %s", e)
            return json.dumps({"error": str(e)})

    return fetch_github_diff
