"""Tests for API Scout discovery."""

import httpx
import pytest

from api_scout.github import GitHubClient
from api_scout.scout import ApiScout


@pytest.mark.asyncio
async def test_scout_deduplicates_and_ranks_results() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        if request.url.path == (
            "/search/repositories"
        ):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "full_name": "acme/sol-api",
                            "html_url": (
                                "https://github.com/"
                                "acme/sol-api"
                            ),
                            "description": (
                                "Free Solana API"
                            ),
                            "stargazers_count": 100,
                            "updated_at": (
                                "2099-01-01T00:00:00Z"
                            ),
                            "topics": [
                                "solana",
                                "api",
                            ],
                            "license": {
                                "name": "MIT License"
                            },
                        }
                    ]
                },
            )

        if request.url.path == (
            "/repos/acme/sol-api/readme"
        ):
            return httpx.Response(
                200,
                text=(
                    "Free public API for "
                    "Solana market data. "
                    "No API key required."
                ),
            )

        return httpx.Response(404)

    client = httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(
            handler
        ),
    )

    github = GitHubClient(
        client=client,
    )

    scout = ApiScout(github)

    candidates = await scout.discover(
        needs=(
            "solana",
            "market data",
        ),
        results_per_query=1,
        inspect_limit=5,
        search_queries=(
            "one",
            "two",
        ),
    )

    assert len(candidates) == 1
    assert (
        candidates[0].full_name
        == "acme/sol-api"
    )
    assert "solana" in (
        candidates[0].matched_needs
    )
    assert candidates[0].score > 0

    await client.aclose()
