"""Prompt loader — reads .md templates from disk, renders with variables."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from string import Formatter

PROMPTS_DIR = Path(__file__).parent


@dataclass(frozen=True)
class PromptDef:
    """Definition of a single prompt from the manifest."""

    id: str
    file: str
    description: str
    variables: list[str]
    _raw: str = field(repr=False, default="")

    def render(self, **kwargs: str | int | float | list[str]) -> str:
        """Render the prompt template with the given variables.

        Uses ``{{var}}`` syntax (double-brace) so Jinja/str.format don't
        clash with the LLM output JSON braces.
        """
        rendered = self._raw
        for key, value in kwargs.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered


class PromptStore:
    """Loads prompts from the manifest + markdown files on disk."""

    def __init__(self, prompts_dir: Path | str | None = None) -> None:
        self._dir = Path(prompts_dir) if prompts_dir else PROMPTS_DIR
        self._manifest: dict[str, PromptDef] = {}
        self._load()

    def _load(self) -> None:
        manifest_path = self._dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Prompt manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            manifest = json.load(f)

        for prompt_id, meta in manifest["prompts"].items():
            md_path = self._dir / meta["file"]
            if not md_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {md_path}")

            raw = md_path.read_text()
            self._manifest[prompt_id] = PromptDef(
                id=prompt_id,
                file=meta["file"],
                description=meta["description"],
                variables=meta["variables"],
                _raw=raw,
            )

    def get(self, prompt_id: str) -> PromptDef:
        """Get a prompt definition by ID."""
        if prompt_id not in self._manifest:
            available = ", ".join(sorted(self._manifest))
            raise KeyError(f"Prompt '{prompt_id}' not found. Available: {available}")
        return self._manifest[prompt_id]

    def render(self, prompt_id: str, **kwargs: str | int | float | list[str]) -> str:
        """Shorthand: get + render in one call."""
        return self.get(prompt_id).render(**kwargs)

    def list_ids(self) -> list[str]:
        """Return all registered prompt IDs."""
        return sorted(self._manifest.keys())


# Module-level singleton for convenience
_store: PromptStore | None = None


def get_store() -> PromptStore:
    global _store
    if _store is None:
        _store = PromptStore()
    return _store


def render_prompt(prompt_id: str, **kwargs: str | int | float | list[str]) -> str:
    """Convenience function: render a prompt by ID with variables."""
    return get_store().render(prompt_id, **kwargs)
