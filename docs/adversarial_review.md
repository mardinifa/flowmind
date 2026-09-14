# Day 7 Challenge Testing and Adversarial Review

**Project:** FlowMind  
**Client:** ClearPath Capital  
**Review date:** 14 September 2026  
**Test environment:** Windows, Python 3.12.5, pytest 9.1.1

## Test Summary

The automated test suite was executed before and after implementing the
Day 7 operating-duration guardrail.

- Original automated tests: 35 passed
- New Day 7 challenge test: 1 passed
- Final regression result: 36 passed
- Failed tests: 0
- Non-blocking deprecation warnings: 2

The manual Ollama letter test was excluded from automated pytest collection
because it requires a running local Ollama model and performs an interactive
external-model operation.

---

## Challenge 1: High-Confidence Wrong Decision

### Problem

The eligibility engine accepted `operating_months` as a trusted value. It did
not compare the value with the business-registration and assessment dates.

A document-extraction error reported that a business had operated for 8 months,
although the source dates showed that it had operated for 18 months. The
eligibility engine therefore returned a failed registration criterion with
high confidence.

### Risk

An eligible applicant could be rejected because the system was confident in an
incorrectly extracted value.

### Correction

A new validation module was created:

`src/intake/date_validator.py`

The validator independently calculates completed operating months from
`business_start_date` and `assessment_date`. It compares the calculated result
with the extracted `operating_months` value.

A difference greater than one month is treated as a contradiction.

### Safe Outcome

When a contradiction is detected:

1. autonomous processing stops;
2. the application is escalated;
3. the contradiction appears in the loan-officer briefing;
4. the officer is instructed to verify the source documents.

### Test Evidence

Test:

`test_confident_wrong_duration_is_caught_and_escalated`

Test data:

- Extracted duration: 8 months
- Source-date duration: 18 months
- Validation result: invalid
- Final routing decision: escalated
- Test outcome: passed

### Historical Audit Limitation

Existing database records do not contain both `business_start_date` and
`assessment_date`. Therefore, their operating durations cannot be
retrospectively verified from the stored data alone.

A production deployment should make these source dates mandatory and retain
the relevant document-extraction evidence.

### Lesson

High confidence means that the system is certain about the information it
received. It does not prove that the information or decision is correct.

---

## Challenge 2: Excessive Escalations

### Scenario

A simulated week contained:

- 100 total applications;
- 70 escalated applications;
- 30 autonomous decisions;
- 1 human override.

This produced a 70% escalation rate, compared with the target range of 25%–35%.

### System Response

The calibration module classified the system as:

`TOO_CONSERVATIVE`

It correctly recommended reviewing confidence boundaries and turnover-ratio
tolerances.

### Decision

The production confidence threshold was not changed blindly from the current
0.85 value. A permanent change without representative test data could increase
unsafe approvals.

The threshold should be evaluated during the Day 8 twenty-application stress
test. If ordinary, complete and low-risk applications are unnecessarily
escalated, a controlled reduction should be tested and its override rate
compared with the original configuration.

### Test Evidence

Test:

`test_too_conservative_thresholds`

Outcome: passed.

---

## Challenge 3: Decline Letter Containing a False Fact

### Scenario

False information was deliberately inserted into generated letters, including:

- claiming that an 18-month-old business had operated for less than 12 months;
- changing a requested loan from ₦2,000,000 to ₦9,500,000;
- changing an applicant’s age from 32 to 55.

### System Response

The post-generation validation layer compared the letter with the structured
application record.

Each contradiction was identified as a hallucination, and automatic sending
was blocked.

### Test Evidence

The following tests passed:

- `test_deliberate_failure_injected_operating_tenure`
- `test_deliberate_failure_injected_monetary_amount`
- `test_deliberate_failure_injected_applicant_age`
- `test_empty_letter_fails_gracefully`

### Lesson

Generated letters must never be sent based only on fluent or convincing
language. Every factual claim must be verified against structured source data.

---

## Challenge 4: Loan Officer Frequently Overrides the AI

### Scenario

A simulated result contained:

- 80 autonomous decisions;
- 16 human overrides;
- override rate: 20%;
- maximum acceptable override rate: 10%.

### System Response

The calibration module classified the system as:

`TOO_LOOSE_HIGH_OVERRIDES`

### Interpretation

A high override rate does not automatically prove that the AI is wrong.

Each override should be classified as one of the following:

1. **AI error:** The recommendation conflicts with verified application
   evidence. The model, rules or confidence threshold should be corrected.
2. **Officer risk preference:** The AI recommendation is evidence-based, but
   the officer applies a stricter or more flexible risk policy.
3. **Insufficient information:** The AI and officer acted using different
   information. The intake and briefing process should be improved.

The feedback loop should retain the officer’s decision, explanation and the
evidence used. Officer preferences should not automatically be labelled as
model errors.

### Test Evidence

Test:

`test_too_loose_high_override_rate`

Outcome: passed.

---

## Adversarial Cross-Review Findings

### Finding 1: Extracted Operating Duration Was Trusted

- **Problem:** `operating_months` was treated as ground truth.
- **Correct source:** Business-registration and assessment dates.
- **Likely cause:** Eligibility rules were separated from document-source
  validation.
- **Resolution:** Added independent duration validation and mandatory
  escalation for contradictions.

### Finding 2: Manual Test Blocks Normal Collection

- **Problem:** `tests/test_letters_manual.py` can wait for the local Ollama
  model during pytest collection.
- **Likely cause:** Model-dependent operations occur during module import.
- **Recommendation:** Convert the file into explicit test functions and mark
  them with `@pytest.mark.manual` or `@pytest.mark.integration`.

### Finding 3: Duplicate Application Modules

- **Problem:** Letter code exists under both `actions` and `src/actions`.
- **Risk:** Developers may update or import different implementations.
- **Recommendation:** Select `src` as the canonical application package and
  remove or clearly deprecate the duplicate module after confirming it is
  unused.

### Finding 4: Empty Root Files

- **Problem:** Root `app.py` and `supabase_client.py` are empty.
- **Risk:** New contributors may assume these are the application entry points.
- **Recommendation:** Remove them or add comments directing users to
  `dashboard/app.py` and `db/database.py`.

### Finding 5: Character-Encoding Problems

- **Problem:** Some terminal output and source text display the naira symbol as
  corrupted characters.
- **Likely cause:** A mismatch between UTF-8 source files and the Windows
  terminal encoding.
- **Recommendation:** Save Python and Markdown files as UTF-8 and test the
  generated letters on Windows before submission.

---

## Day 7 Conclusion

All four mandatory challenge scenarios have been reviewed. The most serious
new issue—an incorrect operating duration producing a high-confidence
eligibility failure—was reproduced, corrected and covered by an automated
regression test.

The project now passes 36 automated tests. The remaining recommendations
should be reviewed during the Day 8 stress test and final documentation stage.
