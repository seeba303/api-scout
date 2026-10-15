"""Deterministic scoring helpers for API Scout."""

from __future__ import annotations

import math
from datetime import UTC, datetime

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
)


def normalize_text(value: str | None) -> str:
    """Normalize text for lightweight matching."""

    return " ".join((value or "").casefold().split())


def keyword_hits(
    text: str,
    keywords: tuple[str, ...],
) -> tuple[str, ...]:
    """Return keywords found in text, preserving requested order."""

    lowered = normalize_text(text)

    return tuple(
        keyword
        for keyword in keywords
        if keyword.casefold() in lowered
    )


def score_repository(
    *,
    stars: int,
    updated_at: str,
    combined_text: str,
    needs: tuple[str, ...],
) -> tuple[
    float,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    """Score a repository using explainable heuristics."""

    matched_needs = keyword_hits(
        combined_text,
        needs,
    )
    free_hints = keyword_hits(
        combined_text,
        FREE_HINTS,
    )
    risk_hints = keyword_hits(
        combined_text,
        RISK_HINTS,
    )

    star_score = min(
        3.0,
        math.log10(max(stars, 1) + 1),
    )
    need_score = min(
        5.0,
        len(matched_needs) * 1.1,
    )
    free_score = min(
        2.0,
        len(free_hints) * 0.6,
    )
    risk_penalty = min(
        4.0,
        len(risk_hints) * 1.5,
    )

    freshness_score = 0.0

    try:
        updated = datetime.fromisoformat(
            updated_at
        )

        age_days = (
            datetime.now(UTC)
            - updated.astimezone(UTC)
        ).days

        if age_days <= 90:
            freshness_score = 2.0
        elif age_days <= 365:
            freshness_score = 1.0
        elif age_days <= 730:
            freshness_score = 0.5
    except ValueError:
        pass

    score = round(
        max(
            0.0,
            star_score
            + need_score
            + free_score
            + freshness_score
            - risk_penalty,
        ),
        2,
    )

    return (
        score,
        matched_needs,
        free_hints,
        risk_hints,
    )