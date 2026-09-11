"""
Eligibility Criteria Test Suite
Tests all 4 independent eligibility functions against boundary conditions.
"""

import pytest
from src.eligibility.rules import (
    check_business_registration,
    check_applicant_age,
    check_turnover_ratio,
    check_loan_purpose,
    evaluate_all_eligibility,
)

def test_check_business_registration():
    # Pass: >= 12 months
    assert check_business_registration({"operating_months": 12, "business_registration_number": "RC-101"}).passed is True
    assert check_business_registration({"operating_months": 36}).passed is True

    # Fail: < 12 months
    res_fail = check_business_registration({"operating_months": 6})
    assert res_fail.passed is False
    assert "Fails tenure requirement" in res_fail.reason


def test_check_applicant_age():
    # Pass: 21 <= age <= 65
    assert check_applicant_age({"applicant_age": 21}).passed is True
    assert check_applicant_age({"applicant_age": 45}).passed is True
    assert check_applicant_age({"applicant_age": 65}).passed is True

    # Fail: < 21
    res_under = check_applicant_age({"applicant_age": 19})
    assert res_under.passed is False
    assert "below the minimum age" in res_under.reason

    # Fail: > 65
    res_over = check_applicant_age({"applicant_age": 70})
    assert res_over.passed is False
    assert "exceeding the maximum age" in res_over.reason


def test_check_turnover_ratio():
    # Pass: loan <= 10x monthly turnover
    assert check_turnover_ratio({"loan_amount": 1000000.0, "monthly_turnover": 200000.0}).passed is True # 5x
    assert check_turnover_ratio({"loan_amount": 1000000.0, "monthly_turnover": 100000.0}).passed is True # 10x

    # Fail: loan > 10x monthly turnover
    res_fail = check_turnover_ratio({"loan_amount": 2500000.0, "monthly_turnover": 200000.0}) # 12.5x
    assert res_fail.passed is False
    assert "exceeding the maximum" in res_fail.reason


def test_check_loan_purpose():
    # Approved
    assert check_loan_purpose({"purpose": "Wholesale rice purchase", "purpose_category": "inventory_purchase"}).passed is True
    assert check_loan_purpose({"purpose": "Tractor spare parts", "purpose_category": "equipment_acquisition"}).passed is True

    # Prohibited
    res_prohib = check_loan_purpose({"purpose": "Crypto trading on Binance", "purpose_category": "cryptocurrency"})
    assert res_prohib.passed is False
    assert "Prohibited loan purpose" in res_prohib.reason


def test_evaluate_all_eligibility():
    clean_app = {
        "operating_months": 24,
        "business_registration_number": "RC-998",
        "applicant_age": 35,
        "loan_amount": 2000000.0,
        "monthly_turnover": 500000.0,
        "purpose": "Inventory expansion",
        "purpose_category": "inventory_purchase",
    }
    assessment = evaluate_all_eligibility(clean_app)
    assert assessment.overall_passed is True
    assert assessment.failed_count == 0
    assert assessment.overall_confidence == "high"
