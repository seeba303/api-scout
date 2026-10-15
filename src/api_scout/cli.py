"""Command-line interface for API Scout."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from api_scout.github import GitHubClient, GitHubRateLimitError
from api_scout.profiles import PROFILES, get_profile, merge_needs
from api_scout.reporting import write_json_report, write_markdown_report
from api_scout.scout import ApiScout


async def run(args: argparse.Namespace) -> None:
    """Run one API Scout discovery job."""

    profile = get_profile(args.profile)
    needs = merge_needs(profile.needs, tuple(args.need or ()))
    token = os.getenv("GITHUB_TOKEN") or None
    github = GitHubClient(token=token)

    try:
        scout = ApiScout(github)
        candidates = await scout.discover(
            needs=needs,
            results_per_query=args.per_query,
            inspect_limit=args.inspect,
            search_queries=profile.search_queries,
            min_score=args.min_score,
        )
    except GitHubRateLimitError as exc:
        raise SystemExit(
            f"{exc}\nTip: use a read-only GITHUB_TOKEN for higher GitHub limits."
        ) from exc
    finally:
        await github.aclose()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "api_scout_results.json"
    markdown_path = output_dir / "api_scout_report.md"

    write_json_report(candidates, json_path)
    write_markdown_report(candidates, markdown_path)

    print(f"Profile: {profile.name}")
    print(f"Found {len(candidates)} relevance-gated candidates.")
    print(f"JSON: {json_path}")
    print(f"Report: {markdown_path}")

    if not token:
        print("No GITHUB_TOKEN detected. Using public GitHub access.")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description=("Discover and rank GitHub leads for useful APIs and data sources.")
    )

    parser.add_argument(
        "--profile",
        choices=tuple(PROFILES),
        default="general",
        help="Built-in discovery profile.",
    )
    parser.add_argument(
        "--need",
        action="append",
        help="Additional capability to prioritize. May be repeated.",
    )
    parser.add_argument(
        "--per-query",
        type=int,
        default=5,
        help="Repositories returned per GitHub search query.",
    )
    parser.add_argument(
        "--inspect",
        type=int,
        default=15,
        help="Top repositories whose README is inspected.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Discard candidates below this deterministic score.",
    )
    parser.add_argument(
        "--output",
        default="api_scout_output",
        help="Directory for generated reports.",
    )

    return parser


def main() -> None:
    """CLI entry point."""

    args = build_parser().parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
