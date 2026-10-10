"""Quality analyzer rules checking ISO/IEC/IEEE 29148 characteristics."""
import re
from typing import List, Dict, Any, Optional
from app.nlp.quality.lexicon import (
    VAGUE_TERMS,
    WEAK_MODALS,
    UNTESTABLE_TERMS,
    MEASURABLE_UNITS_REGEX,
)

# Standard references
REF_UNAMBIGUOUS = "ISO/IEC/IEEE 29148:2018 - Clear & Unambiguous"
REF_COMPLETE = "ISO/IEC/IEEE 29148:2018 - Complete"
REF_VERIFIABLE = "ISO/IEC/IEEE 29148:2018 - Verifiable/Testable"
REF_ATOMIC = "ISO/IEC/IEEE 29148:2018 - Singular/Atomic"
REF_MANDATORY_LANG = "ISO/IEC/IEEE 29148:2018 - Mandatory Wording"


def check_ambiguity_and_vagueness(text: str) -> List[Dict[str, Any]]:
    """Detect vague or ambiguous lexicon terms."""
    issues = []
    text_lower = text.lower()

    # Check weak modals (should, may, can...)
    for modal in WEAK_MODALS:
        pattern = r"\b" + re.escape(modal) + r"\b"
        match = re.search(pattern, text_lower)
        if match:
            issues.append({
                "category": "AMBIGUITY",
                "severity": "HIGH",
                "trigger_text": match.group(0),
                "explanation": f"Use of weak modal verb '{match.group(0)}' introduces ambiguity. Replace with mandatory 'shall'.",
                "standard_reference": REF_MANDATORY_LANG,
            })
            break

    # Check vague terms (quickly, user-friendly, fast, etc.)
    for term in VAGUE_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        match = re.search(pattern, text_lower)
        if match:
            issues.append({
                "category": "VAGUENESS",
                "severity": "MEDIUM",
                "trigger_text": match.group(0),
                "explanation": f"Vague term '{match.group(0)}' lacks clear quantifiable definition.",
                "standard_reference": REF_UNAMBIGUOUS,
            })

    return issues


def check_passive_voice(text: str, nlp_doc: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Detect passive voice constructs in requirement statements."""
    issues = []

    # Heuristic passive pattern (auxiliary verb + past participle or 'shall be <verb>ed')
    passive_regex = re.compile(
        r"\b(shall|should|must|will|is|are|was|were|be|been|being)\s+([a-z]+ed)\b",
        re.IGNORECASE,
    )

    if nlp_doc is not None:
        # Using spaCy dependency parser
        for token in nlp_doc:
            if token.dep_ in ("nsubjpass", "auxpass") or (token.tag_ == "VBN" and token.head.lemma_ in ("be", "shall")):
                trigger = token.text
                issues.append({
                    "category": "PASSIVE_VOICE",
                    "severity": "LOW",
                    "trigger_text": trigger,
                    "explanation": f"Requirement uses passive voice syntax near '{trigger}'. Specify the explicit subject performing the action.",
                    "standard_reference": REF_UNAMBIGUOUS,
                })
                break
    else:
        match = passive_regex.search(text)
        if match:
            issues.append({
                "category": "PASSIVE_VOICE",
                "severity": "LOW",
                "trigger_text": match.group(0),
                "explanation": f"Requirement uses passive voice '{match.group(0)}'. Specify the explicit subject performing the action.",
                "standard_reference": REF_UNAMBIGUOUS,
            })

    return issues


def check_missing_actor(text: str, nlp_doc: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Check if requirement lacks an explicit subject actor."""
    issues = []
    text_lower = text.lower()
    actors = ["system", "application", "platform", "user", "patient", "admin", "administrator", "service", "software", "portal"]

    has_actor = any(actor in text_lower for actor in actors)

    if not has_actor:
        # Check if sentence starts with 'Shall' or lacks subject
        issues.append({
            "category": "INCOMPLETENESS",
            "severity": "HIGH",
            "trigger_text": text[:30] + "...",
            "explanation": "Requirement statement does not specify an explicit subject actor (e.g. 'The system shall...').",
            "standard_reference": REF_COMPLETE,
        })

    return issues


def check_missing_measurable_criteria(text: str, req_type: str) -> List[Dict[str, Any]]:
    """Flag non-functional requirements lacking quantifiable units."""
    issues = []
    if req_type.upper() in ("NON_FUNCTIONAL", "PERFORMANCE", "RELIABILITY"):
        has_measurable = bool(re.search(MEASURABLE_UNITS_REGEX, text, re.IGNORECASE))
        if not has_measurable:
            issues.append({
                "category": "NON_TESTABILITY",
                "severity": "HIGH",
                "trigger_text": text[:40] + "...",
                "explanation": "Non-functional requirement lacks explicit quantifiable metrics (e.g. response time in seconds, percentage, concurrent users).",
                "standard_reference": REF_VERIFIABLE,
            })
    return issues


def check_non_atomic(text: str) -> List[Dict[str, Any]]:
    """Flag compound non-atomic requirements combining multiple requirements into one."""
    issues = []

    # Check for multiple 'shall' statements
    modals = re.findall(r"\b(shall|must)\b", text, re.IGNORECASE)
    if len(modals) > 1:
        issues.append({
            "category": "NON_ATOMIC",
            "severity": "MEDIUM",
            "trigger_text": "multiple shall statements",
            "explanation": "Requirement statement is non-atomic and contains multiple modal verbs. Split into separate single-capability requirements.",
            "standard_reference": REF_ATOMIC,
        })
    elif " and also " in text.lower() or " as well as " in text.lower():
        issues.append({
            "category": "NON_ATOMIC",
            "severity": "LOW",
            "trigger_text": "conjoint clause",
            "explanation": "Requirement contains compound conjoint clauses. Ensure it expresses only a single capability.",
            "standard_reference": REF_ATOMIC,
        })

    return issues


def check_untestable_wording(text: str) -> List[Dict[str, Any]]:
    """Flag subjective untestable claims."""
    issues = []
    text_lower = text.lower()

    for term in UNTESTABLE_TERMS:
        if term in text_lower:
            issues.append({
                "category": "NON_TESTABILITY",
                "severity": "CRITICAL" if "never crash" in term else "HIGH",
                "trigger_text": term,
                "explanation": f"Subjective or absolute claim '{term}' cannot be deterministically verified or tested.",
                "standard_reference": REF_VERIFIABLE,
            })

    return issues


def analyze_requirement_quality(
    text: str, req_type: str = "UNCLASSIFIED", nlp_doc: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """Run full ISO/IEC/IEEE 29148 quality rule engine on a requirement statement."""
    all_issues = []

    all_issues.extend(check_ambiguity_and_vagueness(text))
    all_issues.extend(check_passive_voice(text, nlp_doc))
    all_issues.extend(check_missing_actor(text, nlp_doc))
    all_issues.extend(check_missing_measurable_criteria(text, req_type))
    all_issues.extend(check_non_atomic(text))
    all_issues.extend(check_untestable_wording(text))

    return all_issues
