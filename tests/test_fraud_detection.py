"""
Fraud & Anomaly Detection Test Suite
Tests identity mismatches between form submission and bank statement.
Risk must come out High with specific reasoning.
"""

import pytest
from src.risk.classifier import classify_risk
from src.risk.fraud_detector import check_identity_and_name_consistency


def test_fraudulent_name_mismatch_application():
    """
    Calibration / Fraud Requirement:
    Test a deliberately fraudulent-looking application (mismatched names between
    form and bank statement) — confirm risk comes out High with specific reasoning.
    """
    fraud_record = {
        "applicant_name": "Babajide Sanwo",
        "applicant_age": 40,
        "business_name": "Sanwo Trading Ventures",
        "operating_months": 36,
        "loan_amount": 4000000.0,
        "monthly_turnover": 800000.0,
        "purpose": "Bulk purchase of consumer packaged goods",
        "purpose_category": "inventory_purchase",
        "bank_statement_account_name": "Continental Mega Mining & Dredging Ltd",  # Completely unrelated name!
    }

    # 1. Test direct fraud detector
    is_consistent, flags, reasoning = check_identity_and_name_consistency(fraud_record)
    assert is_consistent is False
    assert len(flags) > 0
    assert "CRITICAL_NAME_MISMATCH" in flags[0]

    # 2. Test full risk classification
    assessment = classify_risk(fraud_record)
    assert assessment.risk_level == "High"
    assert "HIGH RISK FLAGGED" in assessment.reasoning
    assert "Continental Mega Mining & Dredging Ltd" in assessment.reasoning
    assert len(assessment.fraud_flags) > 0


def test_legitimate_name_consistency():
    """
    Verifies that legitimate variations (e.g. including Ltd or personal initials) pass consistency.
    """
    legit_record = {
        "applicant_name": "Amaka Okafor",
        "applicant_age": 30,
        "business_name": "Okafor Fashion & Fabrics",
        "operating_months": 24,
        "loan_amount": 1500000.0,
        "monthly_turnover": 450000.0,
        "purpose": "Fabrics acquisition",
        "purpose_category": "inventory_purchase",
        "bank_statement_account_name": "Okafor Fashion and Fabrics Ltd",
    }

    is_consistent, flags, reasoning = check_identity_and_name_consistency(legit_record)
    assert is_consistent is True
    assert len(flags) == 0

    assessment = classify_risk(legit_record)
    assert assessment.risk_level == "Low"
    assert len(assessment.fraud_flags) == 0
