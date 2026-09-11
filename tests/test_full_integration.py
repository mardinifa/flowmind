"""
Full Loop Integration Test Suite
ClearPath Capital - FlowMind
Tests all 3 application personalities end-to-end:
1. app_001 (clearly eligible, low risk) -> auto_approved with validated letter
2. app_002 (fails 2+ criteria) -> auto_declined with validated specific decline letter
3. app_003 (ambiguous) -> escalated, briefing in queue, human decision recorded
"""

import pytest
from src.pipeline import process_application
from db.database import supabase, load_briefing, save_human_decision, get_dashboard_metrics


def test_full_loop_personality_1_clearly_eligible_low_risk():
    """
    Personality 1: app_001 (clearly eligible, low risk)
    Expect:
    - Status: auto_approved
    - Generated letter: Conditional approval letter
    - Guardrail validation: passed (can_send_automatically is True)
    - Stored in database with auto_approved status
    """
    app_001 = {
        "id": "app_001",
        "applicant_name": "Kelechi Nwosu",
        "applicant_age": 35,
        "business_name": "Nwosu Metal Fabrications",
        "business_registration_number": "RC-8819201",
        "operating_months": 36,
        "loan_amount": 2000000.0,
        "monthly_turnover": 800000.0,  # 2.5x ratio
        "purpose": "Acquisition of industrial welding machines and safety gear",
        "purpose_category": "equipment_acquisition",
        "bank_statement_account_name": "Nwosu Metal Fabrications",
    }

    result = process_application(app_001, save_to_db=True)

    assert result["status"] == "auto_approved"
    assert result["eligibility"]["overall_passed"] is True
    assert result["risk"]["risk_level"] == "Low"
    assert result["generated_letter"] is not None
    assert "Conditional Loan Approval" in result["generated_letter"]
    assert result["validation"]["is_valid"] is True
    assert result["validation"]["can_send_automatically"] is True

    # Verify DB persistence
    db_res = supabase.table("applications").select("*").eq("id", "app_001").execute()
    assert len(db_res.data) == 1
    assert db_res.data[0]["status"] == "auto_approved"


def test_full_loop_personality_2_fails_multiple_criteria():
    """
    Personality 2: app_002 (fails 2+ criteria)
    Expect:
    - Status: auto_declined
    - Generated letter: Personalized decline letter citing failed criteria
    - Guardrail validation: passed (can_send_automatically is True)
    - Stored in database with auto_declined status
    """
    app_002 = {
        "id": "app_002",
        "applicant_name": "Oluwaseun Adeleke",
        "applicant_age": 23,
        "business_name": "Adeleke Crypto Arbitrage",
        "business_registration_number": "BN-449102",
        "operating_months": 3,          # Fails <12 mos
        "loan_amount": 6000000.0,
        "monthly_turnover": 150000.0,   # Fails 40x >> 10x max
        "purpose": "High frequency crypto trading and market making",  # Fails prohibited purpose
        "purpose_category": "cryptocurrency",
        "bank_statement_account_name": "Adeleke Crypto Arbitrage",
    }

    result = process_application(app_002, save_to_db=True)

    assert result["status"] == "auto_declined"
    assert result["eligibility"]["failed_count"] >= 2
    assert result["generated_letter"] is not None
    assert "unable to approve" in result["generated_letter"].lower()
    assert result["validation"]["is_valid"] is True
    assert result["validation"]["can_send_automatically"] is True

    # Verify DB persistence
    db_res = supabase.table("applications").select("*").eq("id", "app_002").execute()
    assert len(db_res.data) == 1
    assert db_res.data[0]["status"] == "auto_declined"


def test_full_loop_personality_3_ambiguous_escalated_and_decided():
    """
    Personality 3: app_003 (ambiguous / complex case)
    Expect:
    - Status: escalated
    - Briefing generated and stored in database
    - Briefing loaded by loan officer
    - Human decision recorded -> status updated to human_approved
    """
    app_003 = {
        "id": "app_003",
        "applicant_name": "Fatima Bello",
        "applicant_age": 41,
        "business_name": "Bello Agro Logistics",
        "business_registration_number": "RC-552019",
        "operating_months": 16,
        "loan_amount": 4500000.0,
        "monthly_turnover": 500000.0,  # 9.0x ratio (Borderline, near 10x cap)
        "purpose": "Procurement of cold storage refrigerated truck for perishables",
        "purpose_category": "logistics_and_transport",
        "bank_statement_account_name": "Bello Agro Logistics",
    }

    # Step 1: Run through pipeline -> routes to escalation
    result = process_application(app_003, save_to_db=True)

    assert result["status"] == "escalated"
    assert result["briefing_text"] is not None
    assert "Bello Agro Logistics" in result["briefing_text"]

    # Step 2: Loan officer loads briefing from dashboard
    briefing = load_briefing("app_003")
    assert "Loan Officer Briefing" in briefing
    assert "Fatima Bello" in briefing

    # Step 3: Loan officer reviews and submits human decision
    decision_result = save_human_decision(
        application_id="app_003",
        decision="human_approved",
        officer_id="officer_1",
        notes="Reviewed client logistics contracts in Kaduna; approved facility with quarterly audit.",
    )
    assert decision_result["status"] == "success"

    # Step 4: Verify application status updated in database
    db_res = supabase.table("applications").select("*").eq("id", "app_003").execute()
    assert len(db_res.data) == 1
    assert db_res.data[0]["status"] == "human_approved"
    assert db_res.data[0]["officer_id"] == "officer_1"
    assert "Kaduna" in db_res.data[0]["human_notes"]
