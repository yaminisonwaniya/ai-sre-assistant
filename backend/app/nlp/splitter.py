"""Requirement splitter identifying numbered lists, bullet points, and modal verb sentences."""
import re
from typing import List, Dict, Any
from app.nlp.cleaner import clean_document_text, is_heading_line

# Regex patterns for requirements splitting
LIST_PREFIX_PATTERN = re.compile(
    r"^(?:(?:REQ-?\d+|[A-Z]{2,4}-?\d+|[0-9]+(?:\.[0-9]+)*)[:\.\)-]?|[-*•])\s*",
    re.IGNORECASE,
)

REQUIREMENT_MODAL_VERBS = re.compile(
    r"\b(shall|should|must|will|can|is required to|are required to)\b",
    re.IGNORECASE,
)


def contains_requirement_modal(text: str) -> bool:
    """Check if the text statement contains a requirement modal verb."""
    return bool(REQUIREMENT_MODAL_VERBS.search(text))


def split_paragraph_into_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into individual sentences using sentence boundary regex."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", paragraph)
    return [s.strip() for s in sentences if s.strip()]


def is_valid_candidate(statement: str, is_list_item: bool) -> bool:
    """Return True if statement qualifies as a candidate requirement."""
    words = statement.split()
    if len(words) < 3:
        return False
    if contains_requirement_modal(statement):
        return True
    # If list item without modal, require at least 4 words and non-heading
    if is_list_item and len(words) >= 4 and not is_heading_line(statement):
        return True
    return False


def extract_requirements_from_text(raw_text: str) -> List[Dict[str, Any]]:
    """Extract individual requirements from raw text with line/section references."""
    cleaned_lines = clean_document_text(raw_text)
    extracted_items = []

    for line_no, line_text in cleaned_lines:
        is_list_item = bool(LIST_PREFIX_PATTERN.match(line_text))
        cleaned_statement = LIST_PREFIX_PATTERN.sub("", line_text).strip()

        if not cleaned_statement:
            continue

        if is_valid_candidate(cleaned_statement, is_list_item):
            if contains_requirement_modal(cleaned_statement):
                sentences = split_paragraph_into_sentences(cleaned_statement)
                for s_idx, sentence in enumerate(sentences):
                    if contains_requirement_modal(sentence) or len(sentences) == 1:
                        extracted_items.append({
                            "text": sentence,
                            "source_reference": f"Line {line_no}" if len(sentences) == 1 else f"Line {line_no}, Sent {s_idx + 1}"
                        })
            else:
                extracted_items.append({
                    "text": cleaned_statement,
                    "source_reference": f"Line {line_no}"
                })

    return extracted_items
