"""Tests for deterministic scoring."""

from api_scout.scoring import (
    keyword_hits,
    score_repository,
)


def test_keyword_hits_preserves_requested_order() -> None:
    hits = keyword_hits(
        "Free Solana public API",
        (
            "news",
            "solana",
            "public api",
        ),
    )

    assert hits == (
        "solana",
        "public api",
    )


def test_relevant_free_repo_scores_above_irrelevant_repo() -> None:
    relevant, *_ = score_repository(
        stars=1000,
        updated_at="2099-01-01T00:00:00Z",
        combined_text=(
            "Free public API for Solana "
            "market data. No API key."
        ),
        needs=(
            "solana",
            "market data",
        ),
    )

    irrelevant, *_ = score_repository(
        stars=1,
        updated_at="2000-01-01T00:00:00Z",
        combined_text=(
            "Old unrelated repository"
        ),
        needs=(
            "solana",
            "market data",
        ),
    )

    assert relevant > irrelevant


def test_deprecation_hint_penalizes_score() -> None:
    clean, *_ = score_repository(
        stars=100,
        updated_at="2099-01-01T00:00:00Z",
        combined_text=(
            "Free public API for crypto"
        ),
        needs=("crypto",),
    )

    risky, *_ = score_repository(
        stars=100,
        updated_at="2099-01-01T00:00:00Z",
        combined_text=(
            "Free public API for crypto. "
            "Deprecated and discontinued."
        ),
        needs=("crypto",),
    )

    assert clean > risky
