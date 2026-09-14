"""
Day 7 Mandatory Challenge Tests

Challenge 1:
A confidently wrong eligibility result caused by an incorrectly
extracted operating duration.
"""

from src.eligibility.rules import check_business_registration
from src.intake.date_validator import validate_operating_duration
from src.pipeline import process_application


def test_confident_wrong_duration_is_caught_and_escalated():
    """
    The extraction says the business has operated for 8 months,
    while the verified dates show 18 months.

    Without cross-validation, the eligibility engine confidently
    marks the business as ineligible. The new guardrail must detect
    the contradiction and route the application to a human.
    """
    application = {
        "id": "DAY7-WRONG-DATE-001",
        "applicant_name": "Amina Yusuf",
        "applicant_age": 34,
        "business_name": "Amina Agro Supplies",
        "business_registration_number": "RC-9081726",

        # Deliberately incorrect extracted value
        "operating_months": 8,

        # Verified source dates show 18 completed months
        "business_start_date": "2025-03-01",
        "assessment_date": "2026-09-01",

        "loan_amount": 1500000.0,
        "monthly_turnover": 400000.0,
        "purpose": "Purchase of agricultural supplies and raw materials",
        "purpose_category": "agriculture_supply",
        "bank_statement_account_name": "Amina Agro Supplies",
    }

    # Demonstrate the original weakness:
    # the eligibility engine trusts operating_months.
    original_result = check_business_registration(application)

    assert original_result.passed is False
    assert original_result.confidence == "high"
    assert "8 months" in original_result.evidence

    # Confirm source-date cross-validation finds the contradiction.
    duration_check = validate_operating_duration(application)

    assert duration_check["was_checked"] is True
    assert duration_check["is_valid"] is False
    assert duration_check["reported_months"] == 8
    assert duration_check["calculated_months"] == 18

    # Confirm the complete system now stops and requests human review.
    pipeline_result = process_application(
        application,
        save_to_db=False,
    )

    assert pipeline_result["status"] == "escalated"
    assert pipeline_result["duration_validation"]["is_valid"] is False
    assert "contradict" in pipeline_result["record"]["ai_recommendation"].lower()
    assert "Human review is required" in pipeline_result["briefing_text"]