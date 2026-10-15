"""Deterministic scoring helpers for API Scout."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from api_scout.models import SourceType

FREE_HINTS = (
    "free",
    "free tier",
    "no api key",
    "no authentication",
    "public api",
    "open api",
)

RISK_HINTS = (
    "deprecated",
    "archived",
    "discontinued",
    "paid only",
    "no longer maintained",
    "sunset",
    "end of life",
)

API_HINTS = (
    "api",
    "rest api",
    "graphql",
    "endpoint",
    "endpoints",
    "sdk",
    "developer api",
    "webhook",
    "websocket",
    "firehose",
    "stream api",
    "api client",
)


@dataclass(frozen=True)
class ScoreResult:
    """Explainable deterministic score result."""

    score: float
    matched_needs: tuple[str, ...]
    free_hints: tuple[str, ...]
    risk_hints: tuple[str, ...]
    api_evidence: tuple[str, ...]
    reasons: tuple[str, ...]


def normalize_text(value: str | None) -> str:
    """Normalize text for lightweight matching."""

    return " ".join((value or "").casefold().split())


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = normalize_text(text)
    normalized_phrase = normalize_text(phrase)

    if not normalized_phrase:
        return False

    pattern = (
        r"(?<!\w)" + re.escape(normalized_phrase).replace(r"\ ", r"\s+") + r"(?!\w)"
    )
    return re.search(pattern, normalized_text) is not None


def keyword_hits(
    text: str,
    keywords: tuple[str, ...],
) -> tuple[str, ...]:
    """Return phrases found in text, preserving requested order."""

    return tuple(keyword for keyword in keywords if _contains_phrase(text, keyword))


def score_repository(
    *,
    stars: int,
    updated_at: str,
    metadata_text: str,
    evidence_text: str,
    needs: tuple[str, ...],
    capabilities: tuple[str, ...],
    source_type: SourceType,
) -> ScoreResult:
    """Score a repository using explainable, relevance-first heuristics."""

    relevant_text = f"{metadata_text} {evidence_text}"

    matched_needs = keyword_hits(relevant_text, needs)
    free_hints = keyword_hits(relevant_text, FREE_HINTS)
    risk_hints = keyword_hits(relevant_text, RISK_HINTS)
    api_evidence = keyword_hits(relevant_text, API_HINTS)

    need_score = min(4.0, len(matched_needs) * 1.25)
    capability_score = min(2.4, len(capabilities) * 0.6)
    api_score = min(2.0, len(api_evidence) * 0.5)
    free_score = min(1.2, len(free_hints) * 0.4)
    risk_penalty = min(3.6, len(risk_hints) * 1.2)

    source_bonus = {
        SourceType.API_PROVIDER: 1.5,
        SourceType.API_DIRECTORY: 1.2,
        SourceType.SDK_CLIENT: 1.0,
        SourceType.DATASET: 0.2,
        SourceType.GENERIC_RESOURCE: 0.0,
        SourceType.IRRELEVANT: -3.0,
    }[source_type]

    star_score = min(1.0, math.log10(max(stars, 1) + 1) / 5.0)

    freshness_score = 0.0
    try:
        updated = datetime.fromisoformat(updated_at)
        age_days = max(0, (datetime.now(UTC) - updated.astimezone(UTC)).days)
        if age_days <= 90:
            freshness_score = 1.0
        elif age_days <= 365:
            freshness_score = 0.6
        elif age_days <= 730:
            freshness_score = 0.3
    except ValueError:
        pass

    score = round(
        max(
            0.0,
            need_score
            + capability_score
            + api_score
            + free_score
            + source_bonus
            + star_score
            + freshness_score
            - risk_penalty,
        ),
        2,
    )

    reasons: list[str] = []
    if matched_needs:
        reasons.append(f"matched {len(matched_needs)} requested need(s)")
    if capabilities:
        reasons.append(f"covers {len(capabilities)} intelligence capability area(s)")
    if api_evidence:
        reasons.append("contains local API/data-access evidence")
    if source_type in {SourceType.API_PROVIDER, SourceType.API_DIRECTORY}:
        reasons.append(f"classified as {source_type.value}")
    if free_hints:
        reasons.append("contains free/public-access hints")
    if risk_hints:
        reasons.append(f"risk flags: {', '.join(risk_hints)}")

    return ScoreResult(
        score=score,
        matched_needs=matched_needs,
        free_hints=free_hints,
        risk_hints=risk_hints,
        api_evidence=api_evidence,
        reasons=tuple(reasons),
    )
