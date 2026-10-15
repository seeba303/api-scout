"""Relevance analysis for API Scout."""

from __future__ import annotations

from api_scout.models import SourceType
from api_scout.scoring import API_HINTS, keyword_hits, normalize_text

CAPABILITY_ALIASES: dict[str, tuple[str, ...]] = {
    "SOCIAL_POSTS": (
        "twitter",
        "tweet",
        "social media",
        "public posts",
        "timeline",
        "mentions",
        "bluesky",
        "atproto",
        "mastodon",
    ),
    "MEME_TRENDS": (
        "meme",
        "memes",
        "gif",
        "gifs",
        "giphy",
        "sticker",
        "stickers",
        "reaction",
    ),
    "NEWS": (
        "news",
        "headline",
        "headlines",
        "rss",
        "gdelt",
    ),
    "COMMUNITIES": (
        "reddit",
        "forum",
        "forums",
        "community",
        "communities",
    ),
    "SEARCH_TRENDS": (
        "trends",
        "trending",
        "search trends",
        "trend data",
    ),
    "CRYPTO_MARKETS": (
        "crypto market",
        "market data",
        "token price",
        "dex",
        "liquidity",
        "volume",
    ),
    "ONCHAIN": (
        "on-chain",
        "onchain",
        "solana",
        "blockchain",
        "transaction",
        "wallet",
        "rpc",
    ),
    "MEDIA_TRENDS": (
        "image",
        "images",
        "video",
        "gif",
        "gifs",
        "sticker",
        "stickers",
        "media",
    ),
}

_GENERIC_PATTERNS = (
    "awesome list",
    "curated list",
    "resources",
    "resource list",
    "cheatsheet",
    "cheat sheet",
    "style guide",
    "course",
    "tutorial",
    "interview",
)

_DIRECTORY_PATTERNS = (
    "list of free apis",
    "list of public apis",
    "public api list",
    "api directory",
    "awesome api",
    "awesome-apis",
    "public-apis",
)

_SDK_PATTERNS = (
    "sdk",
    "client library",
    "api client",
    "wrapper",
)

_DATASET_PATTERNS = (
    "dataset",
    "datasets",
    "data set",
    "data sets",
)


def detect_capabilities(text: str) -> tuple[str, ...]:
    """Detect canonical intelligence capabilities from text."""

    found: list[str] = []

    for capability, aliases in CAPABILITY_ALIASES.items():
        if keyword_hits(text, aliases):
            found.append(capability)

    return tuple(found)


def capability_anchors() -> tuple[str, ...]:
    """Return all capability alias terms for evidence extraction."""

    return tuple(
        dict.fromkeys(
            alias for aliases in CAPABILITY_ALIASES.values() for alias in aliases
        )
    )


def classify_source(
    *,
    full_name: str,
    description: str,
    topics: tuple[str, ...],
    evidence_text: str,
    matched_needs: tuple[str, ...],
    api_evidence: tuple[str, ...],
) -> SourceType:
    """Classify a GitHub result using conservative heuristics."""

    metadata = normalize_text(" ".join((full_name, description, " ".join(topics))))
    relevant = normalize_text(f"{metadata} {evidence_text}")

    if any(pattern in metadata for pattern in _DIRECTORY_PATTERNS):
        return SourceType.API_DIRECTORY

    if any(pattern in metadata for pattern in _DATASET_PATTERNS) and not api_evidence:
        return SourceType.DATASET

    if matched_needs and api_evidence:
        if any(pattern in metadata for pattern in _SDK_PATTERNS):
            return SourceType.SDK_CLIENT

        if any(pattern in relevant for pattern in API_HINTS):
            if any(pattern in metadata for pattern in _GENERIC_PATTERNS):
                return SourceType.GENERIC_RESOURCE
            return SourceType.API_PROVIDER

    if any(pattern in metadata for pattern in _GENERIC_PATTERNS):
        return SourceType.GENERIC_RESOURCE

    return SourceType.IRRELEVANT


def confidence_for(
    *,
    source_type: SourceType,
    matched_needs: tuple[str, ...],
    capabilities: tuple[str, ...],
    api_evidence: tuple[str, ...],
) -> str:
    """Return a simple explainable confidence label."""

    if (
        source_type in {SourceType.API_DIRECTORY, SourceType.API_PROVIDER}
        and api_evidence
        and (len(matched_needs) >= 2 or len(capabilities) >= 2)
    ):
        return "HIGH"

    if (
        source_type
        in {
            SourceType.API_DIRECTORY,
            SourceType.API_PROVIDER,
            SourceType.SDK_CLIENT,
        }
        and api_evidence
    ):
        return "MEDIUM"

    return "LOW"
