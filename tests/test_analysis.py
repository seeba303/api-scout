"""Tests for capability and source analysis."""

from api_scout.analysis import classify_source, detect_capabilities
from api_scout.models import SourceType


def test_detects_cipher_capabilities() -> None:
    capabilities = detect_capabilities(
        "Bluesky public posts plus Solana on-chain market data and trending GIFs"
    )

    assert "SOCIAL_POSTS" in capabilities
    assert "ONCHAIN" in capabilities
    assert "MEME_TRENDS" in capabilities


def test_public_api_list_is_directory() -> None:
    source_type = classify_source(
        full_name="public-apis/public-apis",
        description="A collective list of free APIs",
        topics=("api",),
        evidence_text="Solana public API",
        matched_needs=("solana",),
        api_evidence=("api",),
    )

    assert source_type is SourceType.API_DIRECTORY


def test_generic_awesome_repo_stays_generic() -> None:
    source_type = classify_source(
        full_name="example/awesome-datascience",
        description="A curated list of data science resources",
        topics=("awesome-list",),
        evidence_text="Solana API example",
        matched_needs=("solana",),
        api_evidence=("api",),
    )

    assert source_type is SourceType.GENERIC_RESOURCE
