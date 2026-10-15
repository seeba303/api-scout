"""Tests for deterministic scoring."""

from api_scout.models import SourceType
from api_scout.scoring import keyword_hits, score_repository


def test_keyword_hits_preserves_requested_order() -> None:
    hits = keyword_hits(
        "Free Solana public API",
        ("news", "solana", "public api"),
    )

    assert hits == ("solana", "public api")


def test_api_does_not_match_inside_capital() -> None:
    assert keyword_hits("capital markets", ("api",)) == ()


def test_relevant_provider_scores_above_generic_resource() -> None:
    relevant = score_repository(
        stars=100,
        updated_at="2099-01-01T00:00:00Z",
        metadata_text="Solana API provider",
        evidence_text="REST API endpoint for Solana market data. Free tier.",
        needs=("solana", "market data"),
        capabilities=("ONCHAIN", "CRYPTO_MARKETS"),
        source_type=SourceType.API_PROVIDER,
    )

    generic = score_repository(
        stars=500000,
        updated_at="2099-01-01T00:00:00Z",
        metadata_text="Programming resources",
        evidence_text="API design article",
        needs=("solana", "market data"),
        capabilities=(),
        source_type=SourceType.GENERIC_RESOURCE,
    )

    assert relevant.score > generic.score


def test_risk_hint_penalizes_score() -> None:
    clean = score_repository(
        stars=100,
        updated_at="2099-01-01T00:00:00Z",
        metadata_text="Crypto API",
        evidence_text="Free public API for crypto",
        needs=("crypto",),
        capabilities=("CRYPTO_MARKETS",),
        source_type=SourceType.API_PROVIDER,
    )

    risky = score_repository(
        stars=100,
        updated_at="2099-01-01T00:00:00Z",
        metadata_text="Crypto API",
        evidence_text="Free public API for crypto. Deprecated and discontinued.",
        needs=("crypto",),
        capabilities=("CRYPTO_MARKETS",),
        source_type=SourceType.API_PROVIDER,
    )

    assert clean.score > risky.score
