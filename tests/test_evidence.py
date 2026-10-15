"""Tests for context-aware evidence extraction."""

from api_scout.evidence import extract_relevant_excerpt


def test_excerpt_keeps_local_api_need_context() -> None:
    readme = """
General introduction.
Deprecated old unrelated widget.
Many lines of unrelated content.
Another unrelated line.
Solana market data
REST API endpoint with public access
Rate limit: 100 requests/minute
"""

    excerpt = extract_relevant_excerpt(readme, ("solana",))

    assert "Solana market data" in excerpt
    assert "REST API endpoint" in excerpt
    assert "Deprecated old unrelated widget" not in excerpt


def test_excerpt_rejects_need_without_api_context() -> None:
    readme = "Solana is a blockchain.\nThis is a course and reading list."

    assert extract_relevant_excerpt(readme, ("solana",)) == ""
