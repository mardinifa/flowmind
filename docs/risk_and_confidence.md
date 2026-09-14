# Risk Classification and Confidence Measurement

## Purpose

FlowMind performs qualitative risk classification after eligibility checking.
This is not a formal credit score. It assigns Low, Medium or High risk using
the application’s operating history, loan exposure, purpose and identity
consistency.

Implementation:

- `src/risk/classifier.py`
- `src/risk/fraud_detector.py`
- `config/thresholds.py`

## Risk Levels

### Low Risk

A business is generally classified as Low risk when:

- it has operated for at least 24 months;
- its loan-to-turnover ratio does not exceed 7;
- its purpose contains no prohibited risk indicators;
- no identity or bank-account mismatch is detected.

### Medium Risk

A business is generally classified as Medium risk when:

- its loan-to-turnover ratio is above 7 but not above 10; or
- it has operated for at least 12 months but less than 24 months.

Medium-risk applications are escalated for human review.

### High Risk

High-risk indicators include:

- operating for less than 12 months;
- loan-to-turnover ratio above 10;
- cryptocurrency, forex, gambling or arbitrage purposes;
- identity or bank-statement account-name mismatch;
- missing bank-account identity information.

## Fraud and Identity Checking

The fraud detector normalises applicant, business and bank-account names by
removing punctuation and common company suffixes.

It then checks for meaningful token overlap. When the bank-account name shares
no identifier with either the applicant or business, the application receives
a critical mismatch flag and is escalated.

This is an anomaly indicator, not proof of fraud. A human officer must verify
the documents before reaching a final conclusion.

## Two-Factor Confidence Measurement

FlowMind combines two confidence components.

### Self-Consistency

The current prototype simulates agreement between three prompt perspectives:

- Low and High risk receive a consistency score of 1.0.
- Borderline Medium risk receives a consistency score of 0.67.

A future production version should perform genuinely independent model calls
rather than simulate the agreement.

### Explanation Quality

The explanation is checked for references to application-specific evidence:

- applicant or business name;
- loan purpose;
- turnover or revenue;
- operating duration;
- sufficient explanatory detail.

The score ranges from 0 to 1.

### Combined Confidence

The final confidence score is calculated as:

`(self-consistency × 0.60) + (explanation quality × 0.40)`

The configured thresholds are:

- High confidence: 0.85 or higher
- Medium confidence: 0.65 or higher
- Below 0.65: Low confidence

## Calibration Metrics

The system monitors:

- autonomous decision rate;
- escalation rate;
- human override rate.

The target escalation rate is 25%–35%, while the maximum acceptable human
override rate is 10%.

A high escalation rate suggests conservative thresholds. A high override rate
suggests that autonomous thresholds may be too loose or that officers apply a
different risk policy.

## Stress-Test Result

The Day 8 test processed 20 fabricated applications:

- 7 autonomous approvals;
- 6 autonomous declines;
- 7 escalations;
- 20 correct routing outcomes;
- 35% escalation rate.

The result falls at the upper boundary of the configured target range.

## Limitations

- The current risk engine is deterministic and not a validated credit model.
- Self-consistency is simulated rather than produced by three live model runs.
- Name matching is token-based and may generate false positives or negatives.
- Fabricated test records cannot establish fairness or real-world accuracy.
- Production use requires bias, privacy, security and regulatory assessments.

## Conclusion

FlowMind uses confidence as a routing control rather than proof of correctness.
Low-confidence, medium-risk, high-risk, contradictory and suspicious cases are
sent to humans instead of being acted upon autonomously.
