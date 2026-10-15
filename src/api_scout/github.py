"""GitHub client for API Scout."""

from __future__ import annotations

from typing import Any

import httpx

GITHUB_API = "https://api.github.com"


class GitHubClient:
    """Small async GitHub REST client."""

    def __init__(
        self,
        *,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        """Create a GitHub client."""

        self._owns_client = client is None

        if client is not None:
            self._client = client
            return

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "API-Scout/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if token:
            headers["Authorization"] = (
                f"Bearer {token}"
            )

        self._client = httpx.AsyncClient(
            base_url=GITHUB_API,
            headers=headers,
            timeout=timeout_seconds,
        )

    async def aclose(self) -> None:
        """Close an internally created HTTP client."""

        if self._owns_client:
            await self._client.aclose()

    async def search_repositories(
        self,
        query: str,
        *,
        per_page: int = 5,
    ) -> list[dict[str, Any]]:
        """Search GitHub repositories."""

        response = await self._client.get(
            "/search/repositories",
            params={
                "q": (
                    f"{query} "
                    "in:name,description,readme"
                ),
                "sort": "stars",
                "order": "desc",
                "per_page": str(per_page),
            },
        )
        response.raise_for_status()

        payload = response.json()
        items = payload.get("items", [])

        if not isinstance(items, list):
            return []

        return [
            item
            for item in items
            if isinstance(item, dict)
        ]

    async def readme(
        self,
        full_name: str,
    ) -> str:
        """Fetch a repository README as raw text."""

        response = await self._client.get(
            f"/repos/{full_name}/readme",
            headers={
                "Accept": (
                    "application/vnd.github.raw+json"
                )
            },
        )

        if response.status_code == 404:
            return ""

        response.raise_for_status()
        return response.text
