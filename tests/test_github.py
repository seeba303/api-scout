"""HTTP contracts exercised with an in-memory transport; no GitHub requests."""

import httpx
import pytest

from api_scout.github import GitHubClient, GitHubRateLimitError


@pytest.mark.parametrize(
    "status,headers",
    [(429, {}), (403, {"x-ratelimit-remaining": "0"}), (403, {"retry-after": "60"})],
)
async def test_rate_limits(status, headers):
    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(status, headers=headers)
        ),
    ) as http:
        with pytest.raises(GitHubRateLimitError):
            await GitHubClient(client=http).search_repositories("weather")


async def test_permission_error_is_not_rate_limit():
    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(403, json={"message": "Forbidden"})
        ),
    ) as http:
        with pytest.raises(httpx.HTTPStatusError):
            await GitHubClient(client=http).search_repositories("weather")


async def test_search_bounds_and_filters_payload():
    def handler(request):
        assert request.url.params["per_page"] == "100"
        assert request.url.params["q"] == "weather in:name,description,readme"
        return httpx.Response(
            200, json={"items": [{"full_name": "example/sdk"}, None, 7]}
        )

    async with httpx.AsyncClient(
        base_url="https://api.github.com", transport=httpx.MockTransport(handler)
    ) as http:
        client = GitHubClient(client=http)
        assert await client.search_repositories("weather", per_page=1000) == [
            {"full_name": "example/sdk"}
        ]
        await client.aclose()
        assert not http.is_closed  # injected client's lifecycle belongs to caller


@pytest.mark.parametrize(
    "status,text,expected",
    [(404, "missing", ""), (200, "# Example API", "# Example API")],
)
async def test_readme(status, text, expected):
    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(status, text=text)
        ),
    ) as http:
        assert await GitHubClient(client=http).readme("example/sdk") == expected


async def test_timeout_propagates_without_retry_storm():
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("timeout", request=request)

    async with httpx.AsyncClient(
        base_url="https://api.github.com", transport=httpx.MockTransport(handler)
    ) as http:
        with pytest.raises(httpx.ReadTimeout):
            await GitHubClient(client=http).search_repositories("weather")
    assert len(calls) == 1
