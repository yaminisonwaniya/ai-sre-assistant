# Requirement Quality Scoring Specification

This document defines the mathematical formula, criteria weights, and quality label thresholds used by the **AI-Powered Software Requirements Engineering Assistant** per the **ISO/IEC/IEEE 29148:2018** standard.

---

## 1. Aggregate Score Formula

The overall requirement Quality Score \(Q\) is a weighted linear combination of four sub-scores, bounded between `0.0` and `100.0`:

\[
Q = (S_{\text{unambiguous}} \times 0.30) + (S_{\text{verifiable}} \times 0.30) + (S_{\text{complete}} \times 0.20) + (S_{\text{atomic}} \times 0.20)
\]

---

## 2. Sub-Score Criteria & Weights

| Sub-Score Criteria | Weight | Monitored ISO/IEC/IEEE 29148 Characteristics |
| :--- | :--- | :--- |
| **Unambiguous (\(S_{\text{unambiguous}}\))** | **30%** | Clear, unambiguous lexicon, absence of vague terms (`quickly`, `fast`, `user-friendly`, `robust`, `etc.`), active voice syntax, mandatory modal verbs (`shall`). |
| **Verifiable (\(S_{\text{verifiable}}\))** | **30%** | Deterministic testability, presence of quantifiable measurable units (e.g. `seconds`, `MB`, `%`), absence of untestable claims (`never crash`, `modern`). |
| **Complete (\(S_{\text{complete}}\))** | **20%** | Explicit subject actor (`The system`, `The patient`, etc.), no missing parameters. |
| **Atomic (\(S_{\text{atomic}}\))** | **20%** | Singular capability requirement, single modal verb per statement (`shall`), no compound conjoint statements (`shall ... and also shall ...`). |

---

## 3. Issue Severity Deductions

Each detected quality flaw subtracts points from its respective sub-score (clamped to a minimum of 0.0):

- **CRITICAL Severity**: `-35.0 points` (e.g., untestable subjective claims like `never crash`).
- **HIGH Severity**: `-25.0 points` (e.g., weak modal verbs `should`/`may`, missing actor, missing measurable criteria).
- **MEDIUM Severity**: `-15.0 points` (e.g., vague lexicon `user-friendly`, non-atomic compound `shall ... and shall ...`).
- **LOW Severity**: `-10.0 points` (e.g., passive voice syntax).

---

## 4. Quality Status Labels

| Quality Score Range | Quality Label | Description |
| :--- | :--- | :--- |
| **80.0 - 100.0** | **`GOOD`** | High quality, clear, testable, and compliant with ISO/IEC/IEEE 29148. |
| **50.0 - 79.9** | **`NEEDS_IMPROVEMENT`** | Contains ambiguity, passive voice, or weak wording requiring review. |
| **0.0 - 49.9** | **`POOR`** | Critical flaws, non-testable, vague, or non-atomic statement requiring rewriting. |
