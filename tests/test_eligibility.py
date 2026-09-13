"""
Eligibility Criteria Test Suite
Tests all 4 independent eligibility functions against boundary conditions.
"""

import pytest
from eligibility.checks import check_eligibility


def test_valid_application():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert all(result["passed"] for result in results)


def test_registration_fails():
    record = {
        "age": 30,
        "months_registered": 6,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    registration = results[0]
    assert registration["passed"] is False


def test_age_fails():
    record = {
        "age": 18,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    age = results[1]
    assert age["passed"] is False


def test_loan_to_turnover_fails():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 6000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    loan_check = results[2]
    assert loan_check["passed"] is False


def test_purpose_fails():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "cryptocurrency"
    }

    results = check_eligibility(record)

    purpose = results[3]
    assert purpose["passed"] is False


def test_missing_field():
    record = {
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    age = results[1]

    assert age["passed"] is False
    assert age["confidence"] == "low"