"""
ClearPath Capital - Eligibility Rules Engine
Four independent, clean, testable criteria functions.
"""

from typing import Dict, Any, Tuple
from src.models import CriterionResult, EligibilityAssessment
from config.thresholds import (
    MIN_MONTHS_OPERATING,
    MIN_APPLICANT_AGE,
    MAX_APPLICANT_AGE,
    MAX_LOAN_TO_TURNOVER_RATIO,
    APPROVED_PURPOSE_CATEGORIES,
    PROHIBITED_PURPOSE_CATEGORIES,
)


def check_business_registration(record: Dict[str, Any]) -> CriterionResult:
    """
    Criterion 1: Business must be registered and operating for at least 12 months.
    """
    months = record.get("operating_months")
    rc_number = record.get("business_registration_number")

    if months is None:
        return CriterionResult(
            criterion_name="business_registration",
            passed=False,
            confidence="low",
            evidence="Operating duration missing from record.",
            reason="Cannot evaluate business registration without verified operating duration.",
        )

    if months < 0:
        return CriterionResult(
            criterion_name="business_registration",
            passed=False,
            confidence="low",
            evidence=f"Invalid operating duration: {months} months.",
            reason="Operating duration cannot be negative.",
        )

    passed = months >= MIN_MONTHS_OPERATING
    confidence = "high" if rc_number else "medium"
    evidence = f"Business operating for {months} months (Minimum required: {MIN_MONTHS_OPERATING} months). CAC Reg: {rc_number or 'Unspecified'}."
    
    if passed:
        reason = f"Meets tenure requirement ({months} months >= {MIN_MONTHS_OPERATING} months)."
    else:
        reason = f"Fails tenure requirement: operating for {months} months, less than the mandatory {MIN_MONTHS_OPERATING} months."

    return CriterionResult(
        criterion_name="business_registration",
        passed=passed,
        confidence=confidence,
        evidence=evidence,
        reason=reason,
    )


def check_applicant_age(record: Dict[str, Any]) -> CriterionResult:
    """
    Criterion 2: Applicant must be between 21 and 65 years old.
    """
    age = record.get("applicant_age")

    if age is None:
        return CriterionResult(
            criterion_name="applicant_age",
            passed=False,
            confidence="low",
            evidence="Applicant age missing from submission.",
            reason="Cannot evaluate age criterion without date of birth or age.",
        )

    passed = MIN_APPLICANT_AGE <= age <= MAX_APPLICANT_AGE
    evidence = f"Applicant age: {age} years (Allowable range: {MIN_APPLICANT_AGE} to {MAX_APPLICANT_AGE} years)."

    if passed:
        reason = f"Applicant age ({age} years) falls within allowable threshold [{MIN_APPLICANT_AGE}-{MAX_APPLICANT_AGE}]."
    else:
        if age < MIN_APPLICANT_AGE:
            reason = f"Applicant is {age} years old, below the minimum age of {MIN_APPLICANT_AGE}."
        else:
            reason = f"Applicant is {age} years old, exceeding the maximum age limit of {MAX_APPLICANT_AGE}."

    return CriterionResult(
        criterion_name="applicant_age",
        passed=passed,
        confidence="high",
        evidence=evidence,
        reason=reason,
    )


def check_turnover_ratio(record: Dict[str, Any]) -> CriterionResult:
    """
    Criterion 3: The loan amount must not exceed 10 times the average monthly turnover.
    """
    loan_amount = record.get("loan_amount")
    turnover = record.get("monthly_turnover")

    if loan_amount is None or turnover is None:
        return CriterionResult(
            criterion_name="turnover_ratio",
            passed=False,
            confidence="low",
            evidence="Loan amount or monthly turnover is missing.",
            reason="Cannot compute turnover ratio without both requested loan amount and monthly turnover.",
        )

    if turnover <= 0:
        return CriterionResult(
            criterion_name="turnover_ratio",
            passed=False,
            confidence="high",
            evidence=f"Monthly turnover is ₦{turnover:,.2f}.",
            reason="Monthly turnover must be greater than zero.",
        )

    ratio = loan_amount / turnover
    passed = ratio <= MAX_LOAN_TO_TURNOVER_RATIO
    confidence = "high"

    evidence = (
        f"Loan Amount: ₦{loan_amount:,.2f}, Average Monthly Turnover: ₦{turnover:,.2f}. "
        f"Computed Ratio: {ratio:.2f}x (Maximum allowable: {MAX_LOAN_TO_TURNOVER_RATIO:.1f}x)."
    )

    if passed:
        reason = f"Loan amount is {ratio:.2f}x monthly turnover, within the {MAX_LOAN_TO_TURNOVER_RATIO:.1f}x ceiling."
    else:
        reason = f"Loan amount is {ratio:.2f}x monthly turnover, exceeding the maximum {MAX_LOAN_TO_TURNOVER_RATIO:.1f}x limit."

    return CriterionResult(
        criterion_name="turnover_ratio",
        passed=passed,
        confidence=confidence,
        evidence=evidence,
        reason=reason,
    )


def check_loan_purpose(record: Dict[str, Any]) -> CriterionResult:
    """
    Criterion 4: Loan purpose must fall within approved categories and not be prohibited.
    """
    purpose = (record.get("purpose") or "").strip().lower()
    category = (record.get("purpose_category") or "").strip().lower()

    if not purpose and not category:
        return CriterionResult(
            criterion_name="loan_purpose",
            passed=False,
            confidence="low",
            evidence="Loan purpose is empty.",
            reason="Application does not state any loan purpose.",
        )

    # Check for prohibited keywords or categories
    for prohibited in PROHIBITED_PURPOSE_CATEGORIES:
        if prohibited in category or prohibited in purpose:
            return CriterionResult(
                criterion_name="loan_purpose",
                passed=False,
                confidence="high",
                evidence=f"Purpose: '{record.get('purpose')}' matched prohibited category '{prohibited}'.",
                reason=f"Prohibited loan purpose category: {prohibited.replace('_', ' ').title()}.",
            )

    # Check for approved category
    is_approved = any(cat in category for cat in APPROVED_PURPOSE_CATEGORIES) or any(
        cat.replace("_", " ") in purpose for cat in APPROVED_PURPOSE_CATEGORIES
    )

    if is_approved:
        return CriterionResult(
            criterion_name="loan_purpose",
            passed=True,
            confidence="high",
            evidence=f"Purpose: '{record.get('purpose')}' classified as '{category or 'approved business purpose'}'.",
            reason="Loan purpose falls within approved productive SME categories.",
        )
    else:
        # Ambiguous / unclassified purpose
        return CriterionResult(
            criterion_name="loan_purpose",
            passed=True,
            confidence="medium",
            evidence=f"Purpose stated: '{record.get('purpose')}'. Category: '{category}'.",
            reason="Purpose is not in prohibited list but requires qualitative loan officer review.",
        )


def evaluate_all_eligibility(record: Dict[str, Any]) -> EligibilityAssessment:
    """
    Runs all 4 eligibility checks on the record and aggregates the result.
    """
    c1 = check_business_registration(record)
    c2 = check_applicant_age(record)
    c3 = check_turnover_ratio(record)
    c4 = check_loan_purpose(record)

    criteria_dict = {
        "business_registration": c1,
        "applicant_age": c2,
        "turnover_ratio": c3,
        "loan_purpose": c4,
    }

    passed_count = sum(1 for c in criteria_dict.values() if c.passed)
    failed_count = sum(1 for c in criteria_dict.values() if not c.passed)
    ambiguous_count = sum(1 for c in criteria_dict.values() if c.confidence in ["medium", "low"])

    overall_passed = failed_count == 0
    if ambiguous_count > 0:
        overall_confidence = "medium" if ambiguous_count == 1 else "low"
    else:
        overall_confidence = "high"

    return EligibilityAssessment(
        overall_passed=overall_passed,
        passed_count=passed_count,
        failed_count=failed_count,
        ambiguous_count=ambiguous_count,
        overall_confidence=overall_confidence,
        criteria=criteria_dict,
    )
