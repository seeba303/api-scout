"""Data models for API Scout."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class SourceType(StrEnum):
    """High-level kind of source represented by a GitHub result."""

    API_DIRECTORY = "api_directory"
    API_PROVIDER = "api_provider"
    SDK_CLIENT = "sdk_client"
    DATASET = "dataset"
    GENERIC_RESOURCE = "generic_resource"
    IRRELEVANT = "irrelevant"


@dataclass(frozen=True)
class ApiCandidate:
    """One repository/API lead discovered by API Scout."""

    full_name: str
    html_url: str
    description: str
    stars: int
    updated_at: str
    license_name: str | None
    topics: tuple[str, ...]
    source_type: SourceType
    confidence: str
    score: float
    matched_needs: tuple[str, ...]
    capabilities: tuple[str, ...]
    api_evidence: tuple[str, ...]
    free_hints: tuple[str, ...]
    risk_hints: tuple[str, ...]
    score_reasons: tuple[str, ...]
    readme_excerpt: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)
