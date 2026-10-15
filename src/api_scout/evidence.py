"""Context-aware README evidence extraction."""

from __future__ import annotations

from api_scout.analysis import capability_anchors
from api_scout.scoring import API_HINTS, keyword_hits


def _clean_lines(text: str) -> list[str]:
    return [" ".join(line.strip().split()) for line in text.splitlines()]


def extract_relevant_excerpt(
    readme: str,
    needs: tuple[str, ...],
    *,
    radius: int = 2,
    max_chars: int = 1400,
) -> str:
    """Return local README windows where needs/capabilities meet API evidence."""

    lines = _clean_lines(readme)
    if not lines:
        return ""

    anchors = tuple(dict.fromkeys((*needs, *capability_anchors())))
    selected_indexes: set[int] = set()

    for index, line in enumerate(lines):
        if not line or not keyword_hits(line, anchors):
            continue

        start = max(0, index - radius)
        end = min(len(lines), index + radius + 1)
        window = " ".join(item for item in lines[start:end] if item)

        if not keyword_hits(window, API_HINTS):
            continue

        selected_indexes.update(range(start, end))

    if not selected_indexes:
        return ""

    selected: list[str] = []
    size = 0

    for index in sorted(selected_indexes):
        line = lines[index]
        if not line:
            continue

        selected.append(line)
        size += len(line) + 1
        if size >= max_chars:
            break

    return "\n".join(selected)[:max_chars]
