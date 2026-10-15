"""Tests for built-in profiles."""

from api_scout.profiles import get_profile, merge_needs


def test_cipher_profile_covers_core_intelligence_sources() -> None:
    profile = get_profile("cipher-intelligence")

    assert "twitter" in profile.needs
    assert "meme" in profile.needs
    assert "solana" in profile.needs
    assert "on-chain" in profile.needs


def test_merge_needs_preserves_order_and_deduplicates() -> None:
    merged = merge_needs(("solana", "news"), ("news", "websocket"))

    assert merged == ("solana", "news", "websocket")
