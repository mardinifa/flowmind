"""
Pydantic Data Models for FlowMind
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

ConfidenceLevel = Literal["high", "medium", "low"]
RiskLevel = Literal["Low", "Medium", "High"]
ApplicationStatus = Literal[
    "submitted",
    "auto_approved",
    "auto_declined",
    "escalated",
    "human_approved",
    "human_declined",
    "human_info_requested",
]

class CriterionResult(BaseModel):
    criterion_name: str
    passed: bool
    confidence: ConfidenceLevel
    evidence: str
    reason: str

class EligibilityAssessment(BaseModel):
    overall_passed: bool
    passed_count: int
    failed_count: int
    ambiguous_count: int
    overall_confidence: ConfidenceLevel
    criteria: Dict[str, CriterionResult]

class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    reasoning: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    consistency_score: float = Field(ge=0.0, le=1.0)
    explanation_quality_score: float = Field(ge=0.0, le=1.0)
    fraud_flags: List[str] = Field(default_factory=list)

class EscalationBriefing(BaseModel):
    application_id: str
    business_name: str
    applicant_name: str
    loan_amount: float
    summary: str
    eligibility_breakdown: str
    risk_assessment: str
    unresolved_questions: List[str]
    recommended_action: str
    formatted_briefing_text: str

class LetterValidationResult(BaseModel):
    is_valid: bool
    can_send_automatically: bool
    verified_claims: List[str] = Field(default_factory=list)
    unverified_claims: List[str] = Field(default_factory=list)
    hallucinations: List[str] = Field(default_factory=list)
    explanation: str

class DocumentIntakeResult(BaseModel):
    is_successful: bool
    extracted_text: str = ""
    is_scanned: bool = False
    is_corrupted: bool = False
    extraction_status: str = "completed"  # 'completed', 'requires_ocr', 'corrupted_file'
    flags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ApplicationRecord(BaseModel):
    id: str
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
    status: ApplicationStatus = "submitted"
    ai_recommendation: Optional[str] = None
    briefing_text: Optional[str] = None
    generated_letter: Optional[str] = None
    letter_validation_status: Optional[str] = None  # 'passed', 'flagged_hallucination', 'pending'
    human_decision: Optional[str] = None
    officer_id: Optional[str] = None
    human_notes: Optional[str] = None
    is_override: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
