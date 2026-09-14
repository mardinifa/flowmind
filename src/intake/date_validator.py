"""
Validates the reported operating duration against source dates.

Day 7 challenge:
Prevent a confidently wrong eligibility decision caused by a
misread business-registration or bank-statement date.
"""

from datetime import date, datetime
from typing import Any, Dict


def _parse_date(value: str) -> date:
    """Convert an ISO date such as 2025-01-15 into a date object."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def calculate_completed_months(start_date: date, end_date: date) -> int:
    """Calculate the number of fully completed months between two dates."""
    months = (
        (end_date.year - start_date.year) * 12
        + end_date.month
        - start_date.month
    )

    if end_date.day < start_date.day:
        months -= 1

    return months


def validate_operating_duration(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cross-check operating_months against business source dates.

    Missing dates do not invalidate older records, but validation is marked
    as not performed. Contradictory or invalid dates must trigger escalation.
    """
    reported_months = record.get("operating_months")
    start_value = record.get("business_start_date")
    assessment_value = record.get("assessment_date")

    if not start_value or not assessment_value:
        return {
            "is_valid": True,
            "was_checked": False,
            "reported_months": reported_months,
            "calculated_months": None,
            "reason": "Source dates were not supplied; cross-validation was not performed.",
        }

    try:
        start_date = _parse_date(start_value)
        assessment_date = _parse_date(assessment_value)
    except (TypeError, ValueError):
        return {
            "is_valid": False,
            "was_checked": True,
            "reported_months": reported_months,
            "calculated_months": None,
            "reason": "A source date is missing or has an invalid format.",
        }

    if start_date > assessment_date:
        return {
            "is_valid": False,
            "was_checked": True,
            "reported_months": reported_months,
            "calculated_months": None,
            "reason": "Business start date occurs after the assessment date.",
        }

    calculated_months = calculate_completed_months(
        start_date,
        assessment_date,
    )

    if reported_months is None:
        return {
            "is_valid": False,
            "was_checked": True,
            "reported_months": None,
            "calculated_months": calculated_months,
            "reason": "Operating duration is missing from the extracted record.",
        }

    difference = abs(reported_months - calculated_months)

    # A one-month tolerance accommodates partially completed months.
    is_valid = difference <= 1

    if is_valid:
        reason = (
            f"Reported duration ({reported_months} months) agrees with "
            f"the source-date calculation ({calculated_months} months)."
        )
    else:
        reason = (
            f"Operating-duration contradiction: extraction reported "
            f"{reported_months} months, but source dates indicate "
            f"{calculated_months} months. Human review is required."
        )

    return {
        "is_valid": is_valid,
        "was_checked": True,
        "reported_months": reported_months,
        "calculated_months": calculated_months,
        "reason": reason,
    }