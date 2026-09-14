# Deliverable D7: Day 8 Stress-Test Results and Retrospective

**Generated:** 2026-09-14T09:51:07  
**Applications tested:** 20  
**Correctly routed:** 20  
**Incorrect or errored:** 0

## Performance Summary

| Metric | Result |
|---|---:|
| Autonomous approvals | 7 |
| Autonomous declines | 6 |
| Total autonomous actions | 13 |
| Human escalations | 7 |
| Autonomous decision rate | 65.0% |
| Escalation rate | 35.0% |
| Correct routing rate | 100.0% |

## Application-Level Results

| ID | Scenario | Expected | Actual | Risk | Confidence | Result |
|---|---|---|---|---|---:|---|
| STRESS-001 | Established equipment business with low loan ratio | auto_approved | auto_approved | Low | 1.0 | PASS |
| STRESS-002 | Established inventory business | auto_approved | auto_approved | Low | 0.92 | PASS |
| STRESS-003 | Agricultural supplier with strong turnover | auto_approved | auto_approved | Low | 1.0 | PASS |
| STRESS-004 | Manufacturing business requesting raw materials | auto_approved | auto_approved | Low | 0.92 | PASS |
| STRESS-005 | Retail store renovation with low exposure | auto_approved | auto_approved | Low | 0.92 | PASS |
| STRESS-006 | Logistics business with established history | auto_approved | auto_approved | Low | 0.92 | PASS |
| STRESS-007 | Working-capital request within safe ratio | auto_approved | auto_approved | Low | 0.92 | PASS |
| STRESS-008 | Underage applicant and newly established business | auto_declined | auto_declined | High | 1.0 | PASS |
| STRESS-009 | Excessive loan ratio and cryptocurrency purpose | auto_declined | auto_declined | High | 0.92 | PASS |
| STRESS-010 | Applicant above age limit with gambling purpose | auto_declined | auto_declined | High | 0.92 | PASS |
| STRESS-011 | New business with zero demonstrated turnover | auto_declined | auto_declined | High | 1.0 | PASS |
| STRESS-012 | Underage applicant requesting personal debt refinancing | auto_declined | auto_declined | Low | 0.92 | PASS |
| STRESS-013 | Insufficient operating history and excessive loan ratio | auto_declined | auto_declined | High | 1.0 | PASS |
| STRESS-014 | Unclassified and ambiguous loan purpose | escalated | escalated | Low | 1.0 | PASS |
| STRESS-015 | Borderline loan-to-turnover ratio | escalated | escalated | Medium | 0.8 | PASS |
| STRESS-016 | Eligible business with limited operating history | escalated | escalated | Medium | 0.8 | PASS |
| STRESS-017 | Missing bank-statement account name | escalated | escalated | High | 0.76 | PASS |
| STRESS-018 | Potential fraud caused by account-name mismatch | escalated | escalated | High | 0.84 | PASS |
| STRESS-019 | Contradictory operating duration | escalated | escalated | High | 1.0 | PASS |
| STRESS-020 | Corrupted supporting PDF | escalated | escalated | Low | 1.0 | PASS |

## Coverage

The stress test included clearly eligible applications, clearly ineligible applications, ambiguous purposes, medium-risk cases, missing information, identity inconsistencies, contradictory source dates and a corrupted supporting document.

## Retrospective

### What worked

- Clear low-risk applications were routed for autonomous approval.
- Applications failing multiple eligibility rules were declined.
- Borderline and ambiguous applications were escalated.
- Identity mismatches and missing account names triggered review.
- The Day 7 duration guardrail caught contradictory source dates.
- Corrupted documents were prevented from autonomous processing.

### Limitations

- Risk classification currently uses deterministic rules rather than three independent live LLM classifications.
- Historical records without source dates cannot be audited for duration-extraction errors.
- The stress data is fabricated and does not represent a validated credit-risk dataset.
- Human override behaviour requires a longer operational dataset.

### Production recommendations

- Require source dates and document references for every extracted fact.
- Mark Ollama-dependent tests separately from automated unit tests.
- Encrypt personal and financial information at rest and in transit.
- Conduct fairness, security and regulatory reviews before deployment.
- Continue monitoring escalation and human-override rates.

## Conclusion

FlowMind correctly routed 20 of 20 stress-test applications. The test produced an escalation rate of 35.0% and an autonomous decision rate of 65.0%. Any failed cases shown above must be investigated before final submission.
