"""
FlowMind FastAPI Server
ClearPath Capital - Lagos, Nigeria
Provides HTTP endpoints for n8n workflows, external webhooks, and credit decisioning.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.pipeline import process_application
from db.database import (
    supabase,
    load_briefing,
    save_human_decision,
    update_status,
    get_dashboard_metrics,
)

app = FastAPI(
    title="FlowMind Intelligent Credit Decision API",
    description="HTTP Orchestration & Webhook Endpoints for ClearPath Capital (Compatible with n8n via host.docker.internal:8000)",
    version="1.0.0",
)

# Enable CORS for local web forms & dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Pydantic Request / Response Schemas ----------------

class ApplicationSubmissionRequest(BaseModel):
    id: Optional[str] = None
    applicant_name: str
    applicant_age: int
    business_name: str
    business_registration_number: Optional[str] = None
    operating_months: int
    loan_amount: float
    monthly_turnover: float
    purpose: str
    purpose_category: str
    bank_statement_account_name: Optional[str] = None

class HumanDecisionRequest(BaseModel):
    decision: str  # 'human_approved', 'human_declined', 'human_info_requested'
    officer_id: str = "officer_1"
    notes: Optional[str] = ""


# ---------------- API Routes ----------------

@app.get("/health", tags=["System"])
def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "FlowMind Credit Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/applications/process", tags=["Pipeline"])
def run_pipeline(payload: ApplicationSubmissionRequest):
    """
    Main n8n Webhook Endpoint.
    Executes the 5-stage intelligent credit decision workflow on an application.
    """
    app_data = payload.model_dump()
    result = process_application(app_data, save_to_db=True)
    return result


@app.post("/api/v1/applications/submit", tags=["Pipeline"])
async def submit_application_multipart(
    applicant_name: str = Form(...),
    applicant_age: int = Form(...),
    business_name: str = Form(...),
    operating_months: int = Form(...),
    loan_amount: float = Form(...),
    monthly_turnover: float = Form(...),
    purpose: str = Form(...),
    purpose_category: str = Form(...),
    business_registration_number: Optional[str] = Form(None),
    bank_statement_account_name: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
):
    """
    Form submission endpoint supporting multipart document (PDF) uploads.
    """
    doc_bytes = None
    if document:
        doc_bytes = await document.read()

    app_data = {
        "applicant_name": applicant_name,
        "applicant_age": applicant_age,
        "business_name": business_name,
        "operating_months": operating_months,
        "loan_amount": loan_amount,
        "monthly_turnover": monthly_turnover,
        "purpose": purpose,
        "purpose_category": purpose_category,
        "business_registration_number": business_registration_number,
        "bank_statement_account_name": bank_statement_account_name or business_name,
    }

    result = process_application(app_data, document_bytes=doc_bytes, save_to_db=True)
    return result


@app.get("/api/v1/applications/{app_id}", tags=["Applications"])
def get_application(app_id: str):
    """Fetches an application record from the database."""
    res = supabase.table("applications").select("*").eq("id", app_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found.")
    return res.data[0]


@app.get("/api/v1/applications/{app_id}/briefing", tags=["Applications"])
def get_briefing(app_id: str):
    """Retrieves the pre-generated loan officer briefing."""
    briefing = load_briefing(app_id)
    if briefing == "Application not found.":
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found.")
    return {"application_id": app_id, "briefing_text": briefing}


@app.post("/api/v1/applications/{app_id}/decision", tags=["Human Review"])
def record_decision(app_id: str, payload: HumanDecisionRequest):
    """Records a human loan officer decision on an escalated application."""
    if payload.decision not in ["human_approved", "human_declined", "human_info_requested"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid decision. Must be 'human_approved', 'human_declined', or 'human_info_requested'.",
        )

    try:
        res = save_human_decision(
            application_id=app_id,
            decision=payload.decision,
            officer_id=payload.officer_id,
            notes=payload.notes or "",
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/metrics", tags=["Analytics"])
def get_metrics():
    """Computes real-time admin operational KPIs from the database."""
    return get_dashboard_metrics()
