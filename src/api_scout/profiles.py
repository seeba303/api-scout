"""Built-in discovery profiles for API Scout."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoutProfile:
    """A reusable discovery profile."""

    name: str
    description: str
    needs: tuple[str, ...]
    search_queries: tuple[str, ...]


CIPHER_INTELLIGENCE = ScoutProfile(
    name="cipher-intelligence",
    description=(
        "Public, legitimate data sources for real-time cultural, social, meme, "
        "news, Solana, on-chain and market intelligence."
    ),
    needs=(
        "twitter",
        "social media",
        "public posts",
        "bluesky",
        "meme",
        "gif",
        "trends",
        "reddit",
        "news",
        "rss",
        "solana",
        "on-chain",
        "crypto market",
        "dex",
    ),
    search_queries=(
        '"twitter api" public posts',
        '"social media api" posts',
        '"bluesky api" atproto',
        '"meme api" gif trends',
        '"giphy api" trending',
        '"reddit api" data',
        '"news api" rss',
        '"solana api" on-chain',
        '"crypto market api" dex',
        '"public api" trends social',
    ),
)

GENERAL = ScoutProfile(
    name="general",
    description="General-purpose public/free API discovery.",
    needs=(
        "news",
        "social media",
        "crypto",
        "solana",
        "trends",
        "rss",
        "market data",
        "on-chain",
    ),
    search_queries=(
        '"public api" free list',
        '"free api" news social',
        '"free api" crypto solana',
        '"open api" trends social media',
        '"public api" market data crypto',
    ),
)

PROFILES: dict[str, ScoutProfile] = {
    GENERAL.name: GENERAL,
    CIPHER_INTELLIGENCE.name: CIPHER_INTELLIGENCE,
}


def get_profile(name: str) -> ScoutProfile:
    """Return a built-in profile by name."""

    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown API Scout profile: {name}") from exc


def merge_needs(
    profile_needs: tuple[str, ...],
    extra_needs: tuple[str, ...],
) -> tuple[str, ...]:
    """Merge profile and CLI needs while preserving order."""

    return tuple(dict.fromkeys((*profile_needs, *extra_needs)))
