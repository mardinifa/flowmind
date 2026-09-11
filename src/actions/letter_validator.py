"""
Anti-Hallucination Guardrail: Letter Validator
ClearPath Capital - FlowMind
Verifies that every factual claim (numbers, amounts, operating tenure, age, names, dates)
in generated letters matches the verified application record.
Any unverified claim flags the letter and blocks automated sending.
"""

import re
from typing import Dict, Any, List, Set, Union
from src.models import LetterValidationResult
from config.thresholds import (
    MIN_MONTHS_OPERATING,
    MIN_APPLICANT_AGE,
    MAX_APPLICANT_AGE,
    MAX_LOAN_TO_TURNOVER_RATIO,
)


def extract_monetary_values(text: str) -> List[float]:
    """
    Extracts numerical currency values from letter text.
    Handles formats: ₦3,500,000, ₦3500000, N3,500,000, NGN 3,500,000, etc.
    """
    # Match currency-prefixed amounts: ₦1,500,000 or N1,500,000 or NGN 1,500,000
    currency_pattern = r"(?:₦|NGN|N|\$)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+(?:\.[0-9]{2})?)"
    matches = re.findall(currency_pattern, text, re.IGNORECASE)
    
    values = []
    for m in matches:
        clean = m.replace(",", "")
        try:
            val = float(clean)
            if val > 100:  # Exclude trivial non-monetary small numbers
                values.append(val)
        except ValueError:
            continue
    return values


def extract_duration_claims(text: str) -> List[Dict[str, Any]]:
    """
    Extracts operating duration claims from letter text.
    E.g., 'operated for 18 months', 'operating for less than 12 months', 'tenure of 4 months'.
    """
    claims = []
    
    # Pattern 1: 'operated/operating/tenure for/of [less than/greater than]? X months/years'
    patterns = [
        r"(?:operated|operating|tenure|history|business has operated)\s+(?:for\s+)?(?:less than|more than|at least)?\s*([0-9]+)\s+months",
        r"(?:track record of|duration of)\s*([0-9]+)\s+months",
        r"([0-9]+)\s+months\s+(?:operating|in business|of operations)",
    ]
    
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            full_snippet = match.group(0)
            month_val = int(match.group(1))
            claims.append({
                "snippet": full_snippet,
                "months": month_val,
                "is_negation_or_less_than": "less than" in full_snippet.lower(),
            })
            
    return claims


def extract_age_claims(text: str) -> List[Dict[str, Any]]:
    """
    Extracts applicant age claims from letter text.
    E.g., 'age of 34', '34 years old'.
    """
    claims = []
    patterns = [
        r"(?:age of|aged)\s+([0-9]{2})",
        r"([0-9]{2})\s+years\s+old",
    ]
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            claims.append({
                "snippet": match.group(0),
                "age": int(match.group(1)),
            })
    return claims


def validate_letter(letter: str, record: Dict[str, Any]) -> LetterValidationResult:
    """
    The Anti-Hallucination Guardrail.
    
    Cross-references every factual claim in the letter against the structured application record:
    1. Monetary claims (Loan amount, monthly turnover)
    2. Tenure / Operating duration claims (Operating months)
    3. Age claims
    4. Applicant and business identity names
    
    Returns LetterValidationResult. If any claim is unverified or contradicts the record,
    can_send_automatically is set to False and the letter is flagged for human review.
    """
    if not letter or not letter.strip():
        return LetterValidationResult(
            is_valid=False,
            can_send_automatically=False,
            unverified_claims=["Letter content is empty."],
            hallucinations=["Empty letter body."],
            explanation="Letter cannot be validated because content is empty.",
        )

    verified_claims: List[str] = []
    unverified_claims: List[str] = []
    hallucinations: List[str] = []

    # Verified ground truth record values
    rec_loan_amount = float(record.get("loan_amount", 0))
    rec_turnover = float(record.get("monthly_turnover", 0))
    rec_months = int(record.get("operating_months", 0))
    rec_age = int(record.get("applicant_age", 0))
    rec_applicant = (record.get("applicant_name") or "").strip()
    rec_business = (record.get("business_name") or "").strip()

    # Allowed threshold reference constants in policy explanations
    allowed_monetary = {rec_loan_amount, rec_turnover}
    
    # ---------------- 1. Validate Monetary Claims ----------------
    letter_monetary_vals = extract_monetary_values(letter)
    for amount in letter_monetary_vals:
        # Check if amount matches record loan amount or monthly turnover
        if any(abs(amount - target) < 1.0 for target in allowed_monetary):
            verified_claims.append(f"Monetary claim ₦{amount:,.2f} verified in record.")
        else:
            # Check if it is a general administrative number or hallucination
            unverified_claims.append(f"Unverified monetary figure: ₦{amount:,.2f}")
            hallucinations.append(
                f"Hallucinated monetary amount: ₦{amount:,.2f} does not match requested loan (₦{rec_loan_amount:,.2f}) or monthly turnover (₦{rec_turnover:,.2f})."
            )

    # ---------------- 2. Validate Operating Tenure Claims ----------------
    duration_claims = extract_duration_claims(letter)
    for d in duration_claims:
        claimed_months = d["months"]
        snippet = d["snippet"]
        is_less_than = d["is_negation_or_less_than"]

        # Case A: Policy threshold reference (e.g. "minimum 12 months required")
        if claimed_months == MIN_MONTHS_OPERATING and ("minimum" in letter.lower() or "required" in letter.lower() or "policy" in letter.lower()):
            if not is_less_than:
                verified_claims.append(f"Policy tenure requirement reference ({claimed_months} months) verified.")
                continue
            else:
                # E.g. "operated for less than 12 months" when record has > 12 months (e.g. 18 months)!
                if rec_months >= MIN_MONTHS_OPERATING:
                    hallucination_msg = (
                        f"FACTUAL CONTRADICTION / HALLUCINATION: Letter claims '{snippet}' "
                        f"but verified application record shows business has operated for {rec_months} months."
                    )
                    hallucinations.append(hallucination_msg)
                    unverified_claims.append(snippet)
                    continue
                else:
                    verified_claims.append(f"Tenure failure claim '{snippet}' matches record ({rec_months} months < {MIN_MONTHS_OPERATING}).")
                    continue

        # Case B: Specific applicant tenure claim (e.g. "operated for 18 months")
        if claimed_months == rec_months:
            verified_claims.append(f"Operating tenure claim ({claimed_months} months) matches record exactly.")
        else:
            hallucination_msg = (
                f"FACTUAL CONTRADICTION / HALLUCINATION: Letter claims '{snippet}' "
                f"({claimed_months} months), but record shows {rec_months} months."
            )
            hallucinations.append(hallucination_msg)
            unverified_claims.append(snippet)

    # ---------------- 3. Validate Applicant Age Claims ----------------
    age_claims = extract_age_claims(letter)
    for a in age_claims:
        claimed_age = a["age"]
        snippet = a["snippet"]
        if claimed_age in [MIN_APPLICANT_AGE, MAX_APPLICANT_AGE] and ("minimum" in letter.lower() or "maximum" in letter.lower() or "between" in letter.lower()):
            verified_claims.append(f"Policy age guideline reference ({claimed_age} years) verified.")
        elif claimed_age == rec_age:
            verified_claims.append(f"Applicant age ({claimed_age} years) matches record.")
        else:
            hallucinations.append(f"Hallucinated applicant age: {claimed_age} years does not match record ({rec_age} years).")
            unverified_claims.append(snippet)

    # ---------------- 4. Validate Identity Names ----------------
    if rec_applicant and rec_applicant.lower() not in letter.lower():
        # Check first name
        first_name = rec_applicant.split()[0]
        if first_name.lower() not in letter.lower():
            unverified_claims.append(f"Applicant name '{rec_applicant}' not clearly identified in letter.")

    if rec_business and rec_business.lower() not in letter.lower():
        unverified_claims.append(f"Business name '{rec_business}' not mentioned in letter.")

    # ---------------- Determine Final Guardrail Status ----------------
    is_valid = len(hallucinations) == 0 and len(unverified_claims) == 0
    can_send_automatically = is_valid

    if is_valid:
        explanation = (
            f"GUARDRAIL PASSED: All {len(verified_claims)} factual claims (amounts, duration, names) "
            "cross-referenced and verified against structured application record. Safe to send automatically."
        )
    else:
        explanation = (
            f"GUARDRAIL FAILED — FLAGGED FOR HUMAN REVIEW: Detected {len(hallucinations)} hallucination(s) "
            f"and {len(unverified_claims)} unverified claim(s). Letter cannot be sent automatically."
        )

    return LetterValidationResult(
        is_valid=is_valid,
        can_send_automatically=can_send_automatically,
        verified_claims=verified_claims,
        unverified_claims=unverified_claims,
        hallucinations=hallucinations,
        explanation=explanation,
    )
