"""Core API Scout discovery engine."""

from __future__ import annotations

from typing import Any

from api_scout.github import GitHubClient
from api_scout.models import ApiCandidate
from api_scout.scoring import score_repository

DEFAULT_NEEDS = (
    "news",
    "social media",
    "crypto",
    "solana",
    "trends",
    "rss",
    "market data",
    "on-chain",
)

DEFAULT_SEARCH_QUERIES = (
    '"public api" free list',
    '"free api" news social',
    '"free api" crypto solana',
    '"open api" trends social media',
    '"public api" market data crypto',
)


def readme_excerpt(
    readme: str,
    needs: tuple[str, ...],
    *,
    max_chars: int = 900,
) -> str:
    """Extract lines likely to contain API details."""

    interesting = (
        "api",
        "auth",
        "free",
        "rate",
        "limit",
        *needs,
    )

    selected: list[str] = []
    current_size = 0

    for line in readme.splitlines():
        clean = " ".join(
            line.strip().split()
        )

        if not clean:
            continue

        lowered = clean.casefold()

        if not any(
            word.casefold() in lowered
            for word in interesting
        ):
            continue

        selected.append(clean)
        current_size += len(clean) + 1

        if current_size >= max_chars:
            break

    return "\n".join(selected)[:max_chars]


class ApiScout:
    """Discover and rank GitHub API leads."""

    def __init__(
        self,
        github: GitHubClient,
    ) -> None:
        self.github = github

    async def discover(
        self,
        *,
        needs: tuple[str, ...] = DEFAULT_NEEDS,
        results_per_query: int = 4,
        inspect_limit: int = 10,
        search_queries: tuple[str, ...] = (
            DEFAULT_SEARCH_QUERIES
        ),
    ) -> list[ApiCandidate]:
        """Search GitHub, inspect READMEs and rank leads."""

        repositories: dict[
            str,
            dict[str, Any],
        ] = {}

        for query in search_queries:
            results = (
                await self.github.search_repositories(
                    query,
                    per_page=results_per_query,
                )
            )

            for repo in results:
                full_name = repo.get(
                    "full_name"
                )

                if (
                    isinstance(full_name, str)
                    and full_name
                ):
                    repositories.setdefault(
                        full_name,
                        repo,
                    )

        by_popularity = sorted(
            repositories.values(),
            key=lambda repo: int(
                repo.get(
                    "stargazers_count",
                    0,
                )
                or 0
            ),
            reverse=True,
        )

        candidates: list[ApiCandidate] = []

        for repo in by_popularity[
            :inspect_limit
        ]:
            full_name = str(
                repo.get(
                    "full_name",
                    "",
                )
            )

            readme = (
                await self.github.readme(
                    full_name
                )
            )

            description = str(
                repo.get("description")
                or ""
            )

            topics = tuple(
                topic
                for topic in repo.get(
                    "topics",
                    [],
                )
                if isinstance(topic, str)
            )

            combined_text = " ".join(
                (
                    full_name,
                    description,
                    " ".join(topics),
                    readme,
                )
            )

            (
                score,
                matched_needs,
                free_hints,
                risk_hints,
            ) = score_repository(
                stars=int(
                    repo.get(
                        "stargazers_count",
                        0,
                    )
                    or 0
                ),
                updated_at=str(
                    repo.get(
                        "updated_at",
                        "",
                    )
                    or ""
                ),
                combined_text=combined_text,
                needs=needs,
            )

            license_payload = repo.get(
                "license"
            )
            license_name = None

            if isinstance(
                license_payload,
                dict,
            ):
                raw_name = (
                    license_payload.get(
                        "name"
                    )
                )
                if isinstance(
                    raw_name,
                    str,
                ):
                    license_name = (
                        raw_name
                    )

            candidates.append(
                ApiCandidate(
                    full_name=full_name,
                    html_url=str(
                        repo.get(
                            "html_url",
                            "",
                        )
                    ),
                    description=description,
                    stars=int(
                        repo.get(
                            "stargazers_count",
                            0,
                        )
                        or 0
                    ),
                    updated_at=str(
                        repo.get(
                            "updated_at",
                            "",
                        )
                        or ""
                    ),
                    license_name=(
                        license_name
                    ),
                    topics=topics,
                    score=score,
                    matched_needs=(
                        matched_needs
                    ),
                    free_hints=(
                        free_hints
                    ),
                    risk_hints=(
                        risk_hints
                    ),
                    readme_excerpt=(
                        readme_excerpt(
                            readme,
                            needs,
                        )
                    ),
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.score
            ),
            reverse=True,
        )
