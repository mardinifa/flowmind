# Eligibility Engine and Action Letters

## Eligibility Criteria

FlowMind evaluates four independent lending criteria. Each check returns:

- whether the criterion passed;
- confidence level;
- supporting evidence;
- a human-readable reason.

The rules are implemented in `src/eligibility/rules.py`.

### 1. Business Registration

The business must have operated for at least 12 months.

Where available, the extracted operating duration is checked against source
dates before an autonomous action is permitted.

### 2. Applicant Age

The applicant must be between 21 and 65 years old, inclusive.

A missing age produces low confidence and requires human review.

### 3. Loan-to-Turnover Ratio

The requested loan must not exceed ten times the demonstrated average monthly
turnover.

A missing or non-positive turnover cannot support automatic approval.

### 4. Loan Purpose

The purpose must belong to an approved productive small-business category and
must not match prohibited purposes such as gambling, cryptocurrency or
speculative trading.

Unclassified but non-prohibited purposes are treated as ambiguous and sent for
human review.

## Eligibility Aggregation

The engine calculates:

- number of passed criteria;
- number of failed criteria;
- number of ambiguous criteria;
- overall pass status;
- overall confidence level.

A record is not considered fully eligible when any criterion fails.

## Autonomous Decline

An application may be declined automatically when it fails at least two
eligibility criteria.

The decline notice must identify the specific failed criteria. A generic or
unsupported explanation is not accepted.

## Conditional Approval

An application may receive conditional approval when:

- all eligibility criteria pass;
- all eligibility results have high confidence;
- qualitative risk is Low;
- risk confidence meets the configured high-confidence threshold;
- no fraud flags are present;
- the generated letter passes factual validation.

## Letter Generation

Letter generation is implemented in:

`src/actions/letter_generator.py`

The system produces:

- personalised decline notices;
- conditional approval notices.

A separate legacy/manual Ollama demonstration exists under
`actions/letters.py` and `scripts/manual_letters_demo.py`.

## Anti-Hallucination Validation

Before a letter is sent, `src/actions/letter_validator.py` checks its factual
claims against the structured application record.

The validator examines information such as:

- applicant and business identity;
- requested loan amount;
- monthly turnover;
- applicant age;
- operating duration;
- eligibility reasons.

If a contradiction or unverifiable claim is detected:

1. the letter is blocked;
2. automatic sending is disabled;
3. the problem is recorded;
4. the application is escalated to a loan officer.

## Validation Tests

The test suite deliberately injected incorrect claims, including:

- describing an 18-month business as operating for less than 12 months;
- changing a ₦2,000,000 request to ₦9,500,000;
- changing an applicant’s age from 32 to 55;
- submitting an empty letter.

All false or empty letters were blocked successfully.

Relevant tests include:

- `tests/test_eligibility.py`
- `tests/test_letter_validator.py`
- `tests/test_full_integration.py`

## Current Limitations

The letter validator uses deterministic checks and cannot guarantee detection
of every possible misleading phrase. Production use would require additional
template restrictions, approval policies, monitoring and periodic audits.

## Conclusion

FlowMind separates decision rules from generated language. Eligibility is
determined from structured evidence, while every generated letter must pass a
second factual-validation layer before it can be sent automatically.
