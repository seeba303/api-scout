"""Report generation for API Scout."""

from __future__ import annotations

import json
from pathlib import Path

from api_scout.models import ApiCandidate


def write_json_report(
    candidates: list[ApiCandidate],
    output_path: Path,
) -> None:
    """Write JSON results."""

    output_path.write_text(
        json.dumps(
            [
                candidate.to_dict()
                for candidate in candidates
            ],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_markdown_report(
    candidates: list[ApiCandidate],
    output_path: Path,
) -> None:
    """Write a human-readable Markdown report."""

    lines = [
        "# API Scout Report",
        "",
        (
            "Discovery only — verify pricing, "
            "terms, quotas and official docs "
            "before integration."
        ),
        "",
    ]

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"## {index}. "
                    f"{candidate.full_name}"
                ),
                "",
                f"- Score: {candidate.score}",
                f"- Stars: {candidate.stars}",
                (
                    "- Updated: "
                    f"{candidate.updated_at}"
                ),
                (
                    "- License: "
                    f"{candidate.license_name or 'Unknown'}"
                ),
                f"- URL: {candidate.html_url}",
                (
                    "- Matched needs: "
                    + (
                        ", ".join(
                            candidate.matched_needs
                        )
                        or "None"
                    )
                ),
                (
                    "- Free/public hints: "
                    + (
                        ", ".join(
                            candidate.free_hints
                        )
                        or "None"
                    )
                ),
                (
                    "- Risk hints: "
                    + (
                        ", ".join(
                            candidate.risk_hints
                        )
                        or "None"
                    )
                ),
                "",
                (
                    candidate.description
                    or "_No description._"
                ),
                "",
                "### README evidence",
                "",
                "```text",
                (
                    candidate.readme_excerpt
                    or (
                        "No useful README "
                        "excerpt found."
                    )
                ),
                "```",
                "",
            ]
        )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
