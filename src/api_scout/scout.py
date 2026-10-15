"""Core API Scout discovery engine."""

from __future__ import annotations

import math
from typing import Any

from api_scout.analysis import classify_source, confidence_for, detect_capabilities
from api_scout.evidence import extract_relevant_excerpt
from api_scout.github import GitHubClient
from api_scout.models import ApiCandidate, SourceType
from api_scout.profiles import GENERAL
from api_scout.scoring import API_HINTS, keyword_hits, score_repository

DEFAULT_NEEDS = GENERAL.needs
DEFAULT_SEARCH_QUERIES = GENERAL.search_queries


class ApiScout:
    """Discover and rank GitHub API leads."""

    def __init__(self, github: GitHubClient) -> None:
        self.github = github

    async def discover(
        self,
        *,
        needs: tuple[str, ...] = DEFAULT_NEEDS,
        results_per_query: int = 5,
        inspect_limit: int = 15,
        search_queries: tuple[str, ...] = DEFAULT_SEARCH_QUERIES,
        min_score: float = 0.0,
    ) -> list[ApiCandidate]:
        """Search GitHub, inspect READMEs and return relevance-gated leads."""

        repositories: dict[str, dict[str, Any]] = {}
        search_hits: dict[str, int] = {}

        for query in search_queries:
            results = await self.github.search_repositories(
                query,
                per_page=results_per_query,
            )

            for rank, repo in enumerate(results, start=1):
                full_name = repo.get("full_name")
                if not isinstance(full_name, str) or not full_name:
                    continue

                repositories.setdefault(full_name, repo)
                search_hits[full_name] = search_hits.get(full_name, 0) + max(
                    1,
                    results_per_query - rank + 1,
                )

        def pre_rank(repo: dict[str, Any]) -> float:
            full_name = str(repo.get("full_name", ""))
            description = str(repo.get("description") or "")
            topics = tuple(
                topic for topic in repo.get("topics", []) if isinstance(topic, str)
            )
            metadata = " ".join((full_name, description, " ".join(topics)))
            need_hits = keyword_hits(metadata, needs)
            api_hits = keyword_hits(metadata, API_HINTS)
            capabilities = detect_capabilities(metadata)
            stars = int(repo.get("stargazers_count", 0) or 0)

            return (
                len(need_hits) * 4.0
                + len(api_hits) * 2.0
                + len(capabilities) * 1.5
                + search_hits.get(full_name, 0)
                + min(1.0, math.log10(max(stars, 1) + 1) / 5.0)
            )

        ranked_for_inspection = sorted(
            repositories.values(),
            key=pre_rank,
            reverse=True,
        )

        candidates: list[ApiCandidate] = []

        for repo in ranked_for_inspection[:inspect_limit]:
            full_name = str(repo.get("full_name", ""))
            readme = await self.github.readme(full_name)
            description = str(repo.get("description") or "")
            topics = tuple(
                topic for topic in repo.get("topics", []) if isinstance(topic, str)
            )
            metadata_text = " ".join((full_name, description, " ".join(topics)))
            evidence_text = extract_relevant_excerpt(readme, needs)
            relevant_text = f"{metadata_text} {evidence_text}"

            matched_needs = keyword_hits(relevant_text, needs)
            capabilities = detect_capabilities(relevant_text)
            api_evidence = keyword_hits(relevant_text, API_HINTS)

            # Hard relevance gate: the result must have both an intelligence need
            # or capability and local evidence that it exposes data/API access.
            if not api_evidence or not (matched_needs or capabilities):
                continue

            source_type = classify_source(
                full_name=full_name,
                description=description,
                topics=topics,
                evidence_text=evidence_text,
                matched_needs=matched_needs,
                api_evidence=api_evidence,
            )

            if source_type in {SourceType.IRRELEVANT, SourceType.DATASET}:
                continue

            result = score_repository(
                stars=int(repo.get("stargazers_count", 0) or 0),
                updated_at=str(repo.get("updated_at", "") or ""),
                metadata_text=metadata_text,
                evidence_text=evidence_text,
                needs=needs,
                capabilities=capabilities,
                source_type=source_type,
            )

            if result.score < min_score:
                continue

            license_payload = repo.get("license")
            license_name = None
            if isinstance(license_payload, dict):
                raw_name = license_payload.get("name")
                if isinstance(raw_name, str):
                    license_name = raw_name

            candidates.append(
                ApiCandidate(
                    full_name=full_name,
                    html_url=str(repo.get("html_url", "")),
                    description=description,
                    stars=int(repo.get("stargazers_count", 0) or 0),
                    updated_at=str(repo.get("updated_at", "") or ""),
                    license_name=license_name,
                    topics=topics,
                    source_type=source_type,
                    confidence=confidence_for(
                        source_type=source_type,
                        matched_needs=result.matched_needs,
                        capabilities=capabilities,
                        api_evidence=result.api_evidence,
                    ),
                    score=result.score,
                    matched_needs=result.matched_needs,
                    capabilities=capabilities,
                    api_evidence=result.api_evidence,
                    free_hints=result.free_hints,
                    risk_hints=result.risk_hints,
                    score_reasons=result.reasons,
                    readme_excerpt=evidence_text,
                )
            )

        return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
