"""Configurable lexicon of vague, ambiguous, subjective, and non-testable terms."""

# Ambiguous / Vague Words (ISO/IEC/IEEE 29148 Clear & Unambiguous)
VAGUE_TERMS = {
    "quickly", "fast", "slow", "easy", "user-friendly", "user friendly",
    "seamless", "seamlessly", "robust", "robustness", "secure", "sufficient",
    "appropriate", "appropriately", "adequate", "adequately", "efficient",
    "efficiently", "flexible", "flexibility", "state-of-the-art", "state of the art",
    "modern", "attractive", "intuitive", "effective", "effectively",
    "as much as possible", "as far as possible", "as appropriate", "if necessary",
    "where applicable", "etc", "etc.", "and/or", "TBD", "TBC", "to be decided",
    "to be confirmed", "reasonably", "timely", "promptly", "normal", "ordinarily"
}

# Weak Modal Verbs (ISO/IEC/IEEE 29148 Mandatory Language)
WEAK_MODALS = {
    "should", "may", "can", "could", "might", "ought to", "would"
}

# Subjective / Untestable Wording
UNTESTABLE_TERMS = {
    "user-friendly", "modern", "attractive", "state-of-the-art", "never crash",
    "100% bug free", "infinite", "instantaneous", "completely secure",
    "error-free", "bug-free", "perfectly", "zero downtime", "beautiful"
}

# Measurable Units / Criteria Pattern for Non-Functional Requirements
MEASURABLE_UNITS_REGEX = r"\b(\d+(?:\.\d+)?\s*(?:seconds|second|sec|ms|s|minutes|min|hours|hrs|gb|mb|kb|%|percent|users|requests|concurrent|tps|transactions|uptime))\b"
