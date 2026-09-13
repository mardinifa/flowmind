"""
Eligibility Criteria Test Suite
Tests all 4 independent eligibility functions against boundary conditions.
"""

import pytest
from eligibility.checks import check_eligibility


def test_01_everything_passes():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert all(result["passed"] for result in results)


def test_02_registration_five_months():
    record = {
        "age": 30,
        "months_registered": 5,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[0]["passed"] is False


def test_03_age_19():
    record = {
        "age": 19,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[1]["passed"] is False


def test_04_age_70():
    record = {
        "age": 70,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[1]["passed"] is False


def test_05_loan_too_large():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 6000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[2]["passed"] is False


def test_06_invalid_purpose():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "cryptocurrency"
    }

    results = check_eligibility(record)

    assert results[3]["passed"] is False


def test_07_registration_and_age_fail():
    record = {
        "age": 19,
        "months_registered": 5,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[0]["passed"] is False
    assert results[1]["passed"] is False


def test_08_loan_and_purpose_fail():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 6000000,
        "avg_monthly_turnover": 500000,
        "purpose": "cryptocurrency"
    }

    results = check_eligibility(record)

    assert results[2]["passed"] is False
    assert results[3]["passed"] is False


def test_09_missing_age():
    record = {
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[1]["passed"] is False
    assert results[1]["confidence"] == "low"


def test_10_missing_turnover():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 2000000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[2]["passed"] is False
    assert results[2]["confidence"] == "low"


def test_11_turnover_zero():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 0,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[2]["passed"] is False


def test_12_age_exactly_21():
    record = {
        "age": 21,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[1]["passed"] is True


def test_13_age_exactly_65():
    record = {
        "age": 65,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[1]["passed"] is True


def test_14_loan_exactly_ten_times_turnover():
    record = {
        "age": 30,
        "months_registered": 24,
        "loan_amount": 5000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[2]["passed"] is True


def test_15_several_fields_missing():
    record = {
        "purpose": "inventory"
    }

    results = check_eligibility(record)

    assert results[0]["passed"] is False
    assert results[1]["passed"] is False
    assert results[2]["passed"] is False