"""Agent configuration — prompts, model settings, brand defaults."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BrandConfig(BaseModel):
    """Brand identity for generated videos."""

    name: str = "Frame"
    tagline: str = ""
    logo_url: str = ""
    primary_color: str = "#E8B84B"
    secondary_color: str = "#0D0F12"
    text_color: str = "#EDEDEE"
    tone: str = "technical, confident, minimal"
    dos: list[str] = Field(default_factory=lambda: ["Use monospace type", "Keep it dark"])
    donts: list[str] = Field(default_factory=lambda: ["No stock footage", "No voiceover"])

    def to_prompt_vars(self) -> dict[str, str]:
        """Flatten brand config into prompt template variables."""
        return {
            "brand_name": self.name,
            "brand_tone": self.tone,
            "brand_primary_color": self.primary_color,
            "brand_secondary_color": self.secondary_color,
            "brand_text_color": self.text_color,
            "brand_dos": ", ".join(self.dos),
            "brand_donts": ", ".join(self.donts),
        }


class AgentConfig(BaseModel):
    """Configuration for the Frame agent."""

    model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    max_tokens: int = 4096
    agentcore_code_interpreter_id: str = ""
    s3_bucket: str = "frame-renders"
    aws_region: str = "us-east-1"
    brand: BrandConfig = Field(default_factory=BrandConfig)

    # Promo-worthiness thresholds
    min_files_changed: int = 1
    max_files_changed: int = 100
    min_diff_size_bytes: int = 50
    promo_keywords: list[str] = Field(
        default_factory=lambda: [
            "feature", "release", "launch", "announce", "new",
            "add", "introduce", "milestone", "v1", "v2", "ga", "beta",
        ]
    )
    confidence_threshold: float = 0.7
