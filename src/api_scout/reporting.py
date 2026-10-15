"""Report generation for API Scout."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from api_scout.models import ApiCandidate


def write_json_report(candidates: list[ApiCandidate], output_path: Path) -> None:
    """Write JSON results."""

    output_path.write_text(
        json.dumps(
            [candidate.to_dict() for candidate in candidates],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_markdown_report(candidates: list[ApiCandidate], output_path: Path) -> None:
    """Write a human-readable Markdown report."""

    confidence_counts = Counter(candidate.confidence for candidate in candidates)
    capability_counts = Counter(
        capability for candidate in candidates for capability in candidate.capabilities
    )

    lines = [
        "# API Scout Report",
        "",
        (
            "Discovery lead only - verify official docs, pricing, terms and "
            "quotas before integration."
        ),
        "",
        "## Summary",
        "",
        f"- Candidates: {len(candidates)}",
        f"- High confidence: {confidence_counts.get('HIGH', 0)}",
        f"- Medium confidence: {confidence_counts.get('MEDIUM', 0)}",
        f"- Low confidence: {confidence_counts.get('LOW', 0)}",
    ]

    if capability_counts:
        lines.extend(
            [
                "- Capability coverage: "
                + ", ".join(
                    f"{name} ({count})"
                    for name, count in capability_counts.most_common()
                ),
                "",
            ]
        )
    else:
        lines.append("")

    for index, candidate in enumerate(candidates, start=1):
        lines.extend(
            [
                f"## {index}. {candidate.full_name}",
                "",
                f"- Score: {candidate.score}",
                f"- Confidence: {candidate.confidence}",
                f"- Source type: {candidate.source_type.value}",
                f"- Stars: {candidate.stars}",
                f"- Updated: {candidate.updated_at}",
                f"- License: {candidate.license_name or 'Unknown'}",
                f"- URL: {candidate.html_url}",
                "- Matched needs: " + (", ".join(candidate.matched_needs) or "None"),
                "- Capabilities: " + (", ".join(candidate.capabilities) or "None"),
                "- API evidence: " + (", ".join(candidate.api_evidence) or "None"),
                "- Free/public hints: " + (", ".join(candidate.free_hints) or "None"),
                "- Risk hints: " + (", ".join(candidate.risk_hints) or "None"),
                (
                    "- Why ranked: "
                    + ("; ".join(candidate.score_reasons) or "No reasons recorded")
                ),
                "",
                candidate.description or "_No description._",
                "",
                "### Local README evidence",
                "",
                "```text",
                candidate.readme_excerpt or "No local README evidence found.",
                "```",
                "",
            ]
        )

    # UTF-8 with BOM renders correctly in Windows PowerShell 5.x as well as editors.
    output_path.write_text("\n".join(lines), encoding="utf-8-sig")
