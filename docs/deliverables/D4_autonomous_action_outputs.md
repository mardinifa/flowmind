# Deliverable D4: Autonomous Action Outputs & Anti-Hallucination Guardrail

**Client:** ClearPath Capital (Lagos, Nigeria)  
**System:** FlowMind Intelligent Credit Decisioning Engine  
**Module:** `src/actions/letter_generator.py` & `src/actions/letter_validator.py`

---

## 1. Executive Summary

ClearPath Capital's autonomous action layer produces personalized conditional approval and specific decline notices. Because an inaccurate rejection or false approval letter causes severe regulatory, operational, and customer trust damage, FlowMind incorporates a deterministic **Anti-Hallucination Guardrail** (`validate_letter`).

Before any letter is transmitted to an applicant:
1. Every monetary amount (₦), operating duration (months), applicant age, and business identity claim is extracted.
2. Every extracted claim is strictly cross-referenced against the verified structured application record.
3. If **any** claim contradicts the record or cannot be verified, the letter is blocked from automated sending and routed immediately to the human loan officer review queue with an explicit diagnostic alert.

---

## 2. Test Case Scenarios & Generated Letters

### Scenario 1: Autonomous Conditional Approval (Low Risk, Clean Eligible)

**Application Record:**
- **Applicant:** Emeka Nnamdi
- **Business:** Nnamdi Auto Spares Ltd (RC-4482019)
- **Requested Loan:** ₦2,500,000.00
- **Monthly Turnover:** ₦850,000.00 (Ratio: 2.94x)
- **Tenure:** 48 months | **Age:** 39 years

**Generated Letter Output:**
```text
ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear Emeka Nnamdi,

Re: Conditional Loan Approval for Nnamdi Auto Spares Ltd

We are pleased to inform you that your application for a microfinance credit facility in the amount of ₦2,500,000.00 has received conditional approval from ClearPath Capital.

Our assessment confirmed your verified operating track record of 48 months and an average demonstrated monthly turnover of ₦850,000.00. Based on your stated business requirements, our credit committee has approved your facility in principle.

Next Steps:
1. An account officer will reach out within 24 hours to schedule a brief on-site physical verification of Nnamdi Auto Spares Ltd.
2. Please prepare original copies of your CAC certificate and valid national ID for inspection.
3. Upon completion of documentation, loan disbursement will be credited to your verified commercial bank account.

Thank you for choosing ClearPath Capital as your growth partner.

Sincerely,
Credit Operations Team
ClearPath Capital Microfinance
```

**Guardrail Validation Result:**
- **`is_valid`**: `True`
- **`can_send_automatically`**: `True`
- **Verified Claims:**
  - `Monetary claim ₦2,500,000.00 verified in record.`
  - `Monetary claim ₦850,000.00 verified in record.`
  - `Operating tenure claim (48 months) matches record exactly.`
  - `Entity identity (Nnamdi Auto Spares Ltd / Emeka Nnamdi) verified.`

---

### Scenario 2: Autonomous Specific Decline (Failed Tenure & Prohibited Purpose)

**Application Record:**
- **Applicant:** Femi Adeleke
- **Business:** CryptoWave Ventures
- **Requested Loan:** ₦4,000,000.00 | **Turnover:** ₦200,000.00 (Ratio: 20x)
- **Tenure:** 4 months (Fails <12 mos rule)
- **Purpose:** Cryptocurrency arbitrage (Prohibited category)

**Generated Letter Output:**
```text
ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear Femi Adeleke,

Re: Loan Application Decision for CryptoWave Ventures (Requested: ₦4,000,000.00)

Thank you for taking the time to apply for a credit facility with ClearPath Capital. We appreciate the opportunity to review your business profile.

Following a thorough review of your submission against our published credit guidelines, we regret to inform you that we are unable to approve your loan request at this time.

Specific Reasons for Decision:
- Business Registration: Fails tenure requirement: operating for 4 months, less than the mandatory 12 months.
- Turnover Ratio: Loan amount is 20.00x monthly turnover, exceeding the maximum 10.0x limit.
- Loan Purpose: Prohibited loan purpose category: Cryptocurrency.

Our lending guidelines are designed to protect both the institution and our clients from over-indebtedness. We encourage you to re-apply once your business meets the tenure and turnover thresholds outlined above.

We wish CryptoWave Ventures continued growth and success.

Sincerely,
Credit Risk Management
ClearPath Capital Microfinance
```

**Guardrail Validation Result:**
- **`is_valid`**: `True`
- **`can_send_automatically`**: `True`
- **Verified Claims:**
  - `Monetary claim ₦4,000,000.00 verified in record.`
  - `Tenure failure claim 'operating for 4 months' matches record (4 months < 12).`
  - `Policy tenure requirement reference (12 months) verified.`

---

## 3. Deliberate Failure Injection Test (The Anti-Hallucination Proof)

### Objective:
Verify that if an LLM hallucinates a false claim into a decline or approval letter (e.g. stating the business has operated for less than 12 months when ground truth records show 18 months), the `validate_letter` function **must intercept the error, reject auto-sending, and flag the application for human review**.

### Test Input:
- **Ground Truth Application Record:**
  - `applicant_name`: "Tolu Adebayo"
  - `business_name`: "Adebayo Logistics Hub"
  - `operating_months`: **18** (Registered for 18 months, passes 12-month rule!)
  - `loan_amount`: ₦2,000,000.00

- **Injected Hallucinated Letter:**
```text
Dear Tolu Adebayo,

We regret to inform you that your application for ₦2,000,000 for Adebayo Logistics Hub has been declined because your business has operated for less than 12 months. ClearPath Capital requires a minimum of 12 months in business.

Sincerely,
Credit Operations Team
```

### Guardrail Interception & Diagnostic Output:
```json
{
  "is_valid": false,
  "can_send_automatically": false,
  "verified_claims": [
    "Monetary claim ₦2,000,000.00 verified in record."
  ],
  "unverified_claims": [
    "operated for less than 12 months"
  ],
  "hallucinations": [
    "FACTUAL CONTRADICTION / HALLUCINATION: Letter claims 'operated for less than 12 months' but verified application record shows business has operated for 18 months."
  ],
  "explanation": "GUARDRAIL FAILED — FLAGGED FOR HUMAN REVIEW: Detected 1 hallucination(s) and 1 unverified claim(s). Letter cannot be sent automatically."
}
```

### Outcome:
- **Action Taken:** Autonomous transmission blocked. Application escalated to the Streamlit Review Queue with a prominent guardrail warning banner.
- **Automated Test:** Passed (`tests/test_letter_validator.py::test_deliberate_failure_injected_operating_tenure`).
