"""Data models for API Scout."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


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
    score: float
    matched_needs: tuple[str, ...]
    free_hints: tuple[str, ...]
    risk_hints: tuple[str, ...]
    readme_excerpt: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)
