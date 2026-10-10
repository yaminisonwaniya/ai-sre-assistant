"""Positive and negative unit tests for every ISO/IEC/IEEE 29148 quality rule."""
import pytest
import spacy

from app.nlp.quality.rules import (
    check_ambiguity_and_vagueness,
    check_passive_voice,
    check_missing_actor,
    check_missing_measurable_criteria,
    check_non_atomic,
    check_untestable_wording,
    analyze_requirement_quality,
)
from app.nlp.quality.scoring import calculate_quality_score

try:
    nlp_model = spacy.load("en_core_web_sm")
except Exception:
    nlp_model = None


# --- 1. Ambiguity & Vagueness Rules ---

def test_ambiguity_positive():
    """Positive test: statement with vague terms and weak modal verb 'should'."""
    text = "The system should respond quickly and be user-friendly."
    issues = check_ambiguity_and_vagueness(text)
    assert len(issues) >= 2
    categories = [i["category"] for i in issues]
    assert "AMBIGUITY" in categories
    assert "VAGUENESS" in categories
    assert any(i["standard_reference"].startswith("ISO/IEC/IEEE 29148") for i in issues)


def test_ambiguity_negative():
    """Negative test: clear statement with mandatory 'shall' and no vague terms."""
    text = "The system shall process funds transfers within 2.0 seconds."
    issues = check_ambiguity_and_vagueness(text)
    assert len(issues) == 0


# --- 2. Passive Voice Rules ---

def test_passive_voice_positive():
    """Positive test: statement using passive voice 'data shall be encrypted'."""
    text = "All patient health record data at rest shall be encrypted."
    doc = nlp_model(text) if nlp_model else None
    issues = check_passive_voice(text, doc)
    assert len(issues) > 0
    assert issues[0]["category"] == "PASSIVE_VOICE"


def test_passive_voice_negative():
    """Negative test: active voice statement 'The system shall encrypt data'."""
    text = "The system shall encrypt all patient health record data at rest."
    doc = nlp_model(text) if nlp_model else None
    issues = check_passive_voice(text, doc)
    assert len(issues) == 0


# --- 3. Missing Actor Rules ---

def test_missing_actor_positive():
    """Positive test: statement lacking an explicit subject actor."""
    text = "Shall store encrypted passwords using SHA-256."
    issues = check_missing_actor(text)
    assert len(issues) > 0
    assert issues[0]["category"] == "INCOMPLETENESS"


def test_missing_actor_negative():
    """Negative test: statement with explicit actor 'The application'."""
    text = "The application shall store encrypted passwords using SHA-256."
    issues = check_missing_actor(text)
    assert len(issues) == 0


# --- 4. Missing Measurable Criteria Rules ---

def test_missing_measurable_criteria_positive():
    """Positive test: NFR statement lacking numeric metrics."""
    text = "The platform shall respond fast under heavy user traffic."
    issues = check_missing_measurable_criteria(text, req_type="PERFORMANCE")
    assert len(issues) > 0
    assert issues[0]["category"] == "NON_TESTABILITY"


def test_missing_measurable_criteria_negative():
    """Negative test: NFR statement with explicit numeric metric 'within 1.5 seconds under 500 users'."""
    text = "The platform shall respond to authentication requests within 1.5 seconds under 500 concurrent users."
    issues = check_missing_measurable_criteria(text, req_type="PERFORMANCE")
    assert len(issues) == 0


# --- 5. Non-Atomic (Compound) Rules ---

def test_non_atomic_positive():
    """Positive test: statement combining multiple 'shall' requirements."""
    text = "The system shall log user attempts and shall send email alerts."
    issues = check_non_atomic(text)
    assert len(issues) > 0
    assert issues[0]["category"] == "NON_ATOMIC"


def test_non_atomic_negative():
    """Negative test: single atomic requirement statement."""
    text = "The system shall send email alerts upon failed login."
    issues = check_non_atomic(text)
    assert len(issues) == 0


# --- 6. Untestable Wording Rules ---

def test_untestable_wording_positive():
    """Positive test: subjective claim 'never crash'."""
    text = "The system shall be robust and never crash under any circumstances."
    issues = check_untestable_wording(text)
    assert len(issues) > 0
    assert issues[0]["category"] == "NON_TESTABILITY"
    assert issues[0]["severity"] == "CRITICAL"


def test_untestable_wording_negative():
    """Negative test: verifiable deterministic requirement."""
    text = "The system shall maintain 99.9% uptime during business hours."
    issues = check_untestable_wording(text)
    assert len(issues) == 0


# --- 7. Quality Scoring Calculation Tests ---

def test_scoring_formula_good_requirement():
    """Clean statement should receive a GOOD quality score >= 80.0."""
    text = "The system shall automatically lock a user account after 5 consecutive failed login attempts within 10 minutes."
    issues = analyze_requirement_quality(text, req_type="FUNCTIONAL")
    score, label, _ = calculate_quality_score(issues)
    assert score >= 80.0
    assert label == "GOOD"


def test_scoring_formula_poor_requirement():
    """Vague & untestable statement should receive a degraded quality score (< 70.0) and non-GOOD label."""
    text = "The application should be user-friendly, fast, and never crash."
    issues = analyze_requirement_quality(text, req_type="PERFORMANCE")
    score, label, _ = calculate_quality_score(issues)
    assert score < 70.0
    assert label != "GOOD"
