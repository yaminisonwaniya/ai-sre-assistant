"""Document noise cleaner stripping Table of Contents, page numbers, and structural headings."""
import re
from typing import List, Tuple

# Regex patterns for noise heuristics
PAGE_NUMBER_PATTERN = re.compile(
    r"^(?:page\s+\d+(?:\s+of\s+\d+)?|-?\s*\d+\s*-?)$", re.IGNORECASE
)
TOC_DOT_LEADER_PATTERN = re.compile(
    r"^.+\.{3,}\s*\d+$"
)
STANDALONE_HEADING_PATTERN = re.compile(
    r"^(?:\d+(?:\.\d+)*\s+)?(?:introduction|scope|overview|table of contents|appendices|appendix|revision history|purpose|references|definitions|document convention)\b",
    re.IGNORECASE,
)


def is_page_number_line(line: str) -> bool:
    """Return True if the line represents a document header/footer page number."""
    stripped = line.strip()
    return bool(PAGE_NUMBER_PATTERN.match(stripped))


def is_toc_line(line: str) -> bool:
    """Return True if the line is a Table of Contents entry with dot leaders."""
    stripped = line.strip()
    return bool(TOC_DOT_LEADER_PATTERN.match(stripped)) or "table of contents" in stripped.lower()


def is_heading_line(line: str) -> bool:
    """Return True if line is a structural non-requirement document section heading."""
    stripped = line.strip()
    if len(stripped.split()) > 8:
        return False
    return bool(STANDALONE_HEADING_PATTERN.match(stripped))


def clean_document_text(raw_text: str) -> List[Tuple[int, str]]:
    """Clean document text and return list of (line_number, line_text) tuples."""
    cleaned_lines = []
    lines = raw_text.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if is_page_number_line(stripped):
            continue
        if is_toc_line(stripped):
            continue
        if is_heading_line(stripped):
            continue

        cleaned_lines.append((idx, stripped))

    return cleaned_lines
