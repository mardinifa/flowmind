"""
Deliverable D4 Test Suite: Anti-Hallucination Guardrail & Deliberate Failure Injection
ClearPath Capital - FlowMind
"""

import pytest
from src.actions.letter_validator import validate_letter
from src.actions.letter_generator import (
    generate_conditional_approval_letter,
    generate_decline_letter,
)

@pytest.fixture
def base_application_record():
    return {
        "id": "APP-TEST-001",
        "applicant_name": "Tolu Adebayo",
        "applicant_age": 32,
        "business_name": "Adebayo Logistics Hub",
        "business_registration_number": "RC-7729104",
        "operating_months": 18,
        "loan_amount": 2000000.0,
        "monthly_turnover": 400000.0,
        "purpose": "Fleet maintenance and tyre acquisition",
        "purpose_category": "equipment_acquisition",
        "bank_statement_account_name": "Adebayo Logistics Hub",
    }


def test_accurate_letter_passes_validation(base_application_record):
    """
    Verifies that a genuine letter referencing accurate ground-truth facts passes the guardrail.
    """
    letter = generate_conditional_approval_letter(base_application_record)
    result = validate_letter(letter, base_application_record)

    assert result.is_valid is True
    assert result.can_send_automatically is True
    assert len(result.hallucinations) == 0
    assert len(result.verified_claims) >= 2


def test_deliberate_failure_injected_operating_tenure(base_application_record):
    """
    DAY 5 STEP 2 — Deliberate Failure Test (Deliverable D4):
    Inject a fake claim: "your business has operated for less than 12 months"
    when the application record says 18 months.
    The validator MUST catch it, flag hallucination, and prevent automatic dispatch.
    """
    # Record has operating_months = 18
    assert base_application_record["operating_months"] == 18

    # Injected letter with false claim
    fake_letter = """ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear Tolu Adebayo,

We regret to inform you that your application for ₦2,000,000 for Adebayo Logistics Hub has been declined because your business has operated for less than 12 months. ClearPath Capital requires a minimum of 12 months in business.

Sincerely,
Credit Operations Team
"""
    result = validate_letter(fake_letter, base_application_record)

    # Assert guardrail caught the hallucination
    assert result.is_valid is False
    assert result.can_send_automatically is False
    assert len(result.hallucinations) > 0
    assert any("FACTUAL CONTRADICTION / HALLUCINATION" in h for h in result.hallucinations)
    assert any("18 months" in h for h in result.hallucinations)


def test_deliberate_failure_injected_monetary_amount(base_application_record):
    """
    Tests injection of an unverified monetary amount (₦9,500,000 instead of ₦2,000,000).
    The validator must flag it and block auto-send.
    """
    fake_letter = """ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear Tolu Adebayo,

We are pleased to approve your loan facility of ₦9,500,000 for Adebayo Logistics Hub. Your operating track record of 18 months is satisfactory.

Sincerely,
Credit Operations Team
"""
    result = validate_letter(fake_letter, base_application_record)

    assert result.is_valid is False
    assert result.can_send_automatically is False
    assert any("₦9,500,000.00" in h for h in result.hallucinations)


def test_deliberate_failure_injected_applicant_age(base_application_record):
    """
    Tests injection of an unverified applicant age (55 years old instead of 32).
    """
    fake_letter = """ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear Tolu Adebayo,

Your application for Adebayo Logistics Hub (₦2,000,000) was reviewed. Given the applicant is 55 years old, additional verification is required.

Sincerely,
Credit Operations Team
"""
    result = validate_letter(fake_letter, base_application_record)

    assert result.is_valid is False
    assert result.can_send_automatically is False
    assert any("55 years" in h for h in result.hallucinations)


def test_empty_letter_fails_gracefully(base_application_record):
    """
    Tests that empty or blank letter inputs fail safely.
    """
    result = validate_letter("", base_application_record)
    assert result.is_valid is False
    assert result.can_send_automatically is False
