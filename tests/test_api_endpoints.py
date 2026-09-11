"""
FastAPI Endpoints Test Suite
Tests webhook ingestion, processing, briefing retrieval, decision logging, and metrics.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "FlowMind" in data["service"]


def test_api_process_pipeline_endpoint():
    payload = {
        "id": "API-TEST-001",
        "applicant_name": "Tariq Danjuma",
        "applicant_age": 38,
        "business_name": "Danjuma Grain Silos",
        "business_registration_number": "RC-998811",
        "operating_months": 30,
        "loan_amount": 1500000.0,
        "monthly_turnover": 600000.0,
        "purpose": "Grain procurement",
        "purpose_category": "inventory_purchase",
        "bank_statement_account_name": "Danjuma Grain Silos",
    }
    response = client.post("/api/v1/applications/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "auto_approved"
    assert data["application_id"] == "API-TEST-001"


def test_api_escalation_briefing_and_decision_endpoint():
    # Submit ambiguous application
    payload = {
        "id": "API-TEST-002",
        "applicant_name": "Ngozi Eze",
        "applicant_age": 44,
        "business_name": "Eze Palm Oil Mills",
        "operating_months": 15,
        "loan_amount": 4000000.0,
        "monthly_turnover": 450000.0,  # 8.88x ratio -> escalated
        "purpose": "Expeller machine purchase",
        "purpose_category": "equipment_acquisition",
        "bank_statement_account_name": "Eze Palm Oil Mills",
    }
    res_proc = client.post("/api/v1/applications/process", json=payload)
    assert res_proc.status_code == 200
    assert res_proc.json()["status"] == "escalated"

    # Get briefing
    res_brief = client.get("/api/v1/applications/API-TEST-002/briefing")
    assert res_brief.status_code == 200
    assert "Eze Palm Oil Mills" in res_brief.json()["briefing_text"]

    # Submit human decision
    res_dec = client.post(
        "/api/v1/applications/API-TEST-002/decision",
        json={
            "decision": "human_approved",
            "officer_id": "officer_1",
            "notes": "Verified high seasonal margins in Imo state.",
        },
    )
    assert res_dec.status_code == 200
    assert res_dec.json()["status"] == "success"


def test_api_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert "total_applications" in metrics
    assert "autonomous_pct" in metrics
    assert "escalated_pct" in metrics
    assert "human_override_pct" in metrics
