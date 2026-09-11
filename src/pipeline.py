"""
FlowMind Pipeline Orchestrator
Wired end-to-end: Intake -> Eligibility -> Risk -> Action Routing -> Letter Validation Guardrail.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from src.models import (
    ApplicationRecord,
    EligibilityAssessment,
    RiskAssessment,
    LetterValidationResult,
    EscalationBriefing,
)
from src.eligibility.rules import evaluate_all_eligibility
from src.risk.classifier import classify_risk
from src.actions.letter_generator import (
    generate_conditional_approval_letter,
    generate_decline_letter,
)
from src.actions.letter_validator import validate_letter
from src.briefing.briefing_generator import generate_escalation_briefing
from src.intake.pdf_extractor import extract_text_from_pdf
from config.thresholds import (
    AUTO_DECLINE_FAILED_CRITERIA_COUNT,
    AUTO_APPROVE_ALLOWED_RISK,
    CONFIDENCE_HIGH_THRESHOLD,
)
from db.database import supabase


def process_application(
    application_data: Dict[str, Any],
    document_bytes: Optional[bytes] = None,
    save_to_db: bool = True,
) -> Dict[str, Any]:
    """
    Executes the full 5-stage FlowMind intelligent decision workflow:
    1. Document intake (if document attached)
    2. Eligibility evaluation (4 criteria)
    3. Qualitative risk assessment & confidence scoring
    4. Decision routing (Autonomous action vs Escalation briefing)
    5. Anti-hallucination letter validation guardrail
    6. Persistence to database
    """
    record = application_data.copy()
    app_id = record.get("id") or f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    record["id"] = app_id

    intake_result = None
    flags = []

    # 1. Document Intake (if PDF provided)
    if document_bytes:
        intake_result = extract_text_from_pdf(document_bytes)
        if intake_result.is_corrupted:
            flags.append("CORRUPTED_DOCUMENT_UPLOAD")
        elif intake_result.is_scanned:
            flags.append("SCANNED_DOCUMENT_REQUIRES_OCR")

    # 2. Eligibility Evaluation
    eligibility: EligibilityAssessment = evaluate_all_eligibility(record)

    # 3. Risk Classification
    risk: RiskAssessment = classify_risk(record)

    # 4. Decision & Routing Logic
    status = "escalated"
    ai_recommendation = ""
    generated_letter = None
    validation_result: Optional[LetterValidationResult] = None
    briefing_text = None

    # Check for document intake edge cases
    if intake_result and (intake_result.is_corrupted or intake_result.is_scanned):
        status = "escalated"
        ai_recommendation = f"Escalated due to document intake issue ({intake_result.extraction_status})."
        briefing = generate_escalation_briefing(
            record,
            eligibility,
            risk,
            unresolved_questions=[
                f"Document issue: {', '.join(intake_result.flags)}",
                "Manual document inspection required by loan officer.",
            ],
            recommended_action="Inspect raw document file or request clean resubmission from applicant.",
        )
        briefing_text = briefing.formatted_briefing_text

    # Route A: High Confidence Clear Decline (fails >= 2 criteria or high risk fraud)
    elif eligibility.failed_count >= AUTO_DECLINE_FAILED_CRITERIA_COUNT:
        failed_reasons = [
            f"{c.criterion_name.replace('_', ' ').title()}: {c.reason}"
            for c in eligibility.criteria.values()
            if not c.passed
        ]
        raw_letter = generate_decline_letter(record, failed_reasons)
        
        # Run Anti-Hallucination Guardrail
        validation_result = validate_letter(raw_letter, record)
        
        if validation_result.can_send_automatically:
            status = "auto_declined"
            ai_recommendation = "Autonomous Decline"
            generated_letter = raw_letter
            letter_status = "passed"
            briefing_text = f"Processed autonomously. Failed {eligibility.failed_count} criteria. Decline letter validated and sent."
        else:
            # Guardrail caught a hallucination! Escalate to human
            status = "escalated"
            ai_recommendation = "Escalated: Guardrail flagged hallucination in generated decline notice."
            briefing = generate_escalation_briefing(
                record,
                eligibility,
                risk,
                unresolved_questions=validation_result.hallucinations,
                recommended_action="Review generated letter and correct factual claims before dispatch.",
            )
            briefing_text = briefing.formatted_briefing_text
            generated_letter = raw_letter
            letter_status = "flagged_hallucination"

    # Route B: High Confidence Clear Approval (Passes all 4 criteria, Risk is Low, high confidence)
    elif (
        eligibility.overall_passed
        and eligibility.overall_confidence == "high"
        and risk.risk_level == AUTO_APPROVE_ALLOWED_RISK
        and risk.confidence_score >= CONFIDENCE_HIGH_THRESHOLD
        and not risk.fraud_flags
    ):
        raw_letter = generate_conditional_approval_letter(record)
        
        # Run Anti-Hallucination Guardrail
        validation_result = validate_letter(raw_letter, record)

        if validation_result.can_send_automatically:
            status = "auto_approved"
            ai_recommendation = "Autonomous Approval"
            generated_letter = raw_letter
            letter_status = "passed"
            briefing_text = "Processed autonomously. Passed all criteria with high confidence. Approval letter validated and sent."
        else:
            # Guardrail caught a hallucination! Escalate to human
            status = "escalated"
            ai_recommendation = "Escalated: Guardrail flagged hallucination in generated approval letter."
            briefing = generate_escalation_briefing(
                record,
                eligibility,
                risk,
                unresolved_questions=validation_result.hallucinations,
                recommended_action="Review approval letter details against record before sending.",
            )
            briefing_text = briefing.formatted_briefing_text
            generated_letter = raw_letter
            letter_status = "flagged_hallucination"

    # Route C: Escalation (Ambiguous criteria, Medium/High Risk, Fraud flags, or Low Confidence)
    else:
        status = "escalated"
        unresolved = []
        if risk.fraud_flags:
            unresolved.extend(risk.fraud_flags)
        if eligibility.ambiguous_count > 0:
            unresolved.append("One or more criteria returned ambiguous confidence.")
        if risk.risk_level in ["Medium", "High"]:
            unresolved.append(f"Risk classified as {risk.risk_level}: {risk.reasoning}")

        briefing = generate_escalation_briefing(record, eligibility, risk, unresolved_questions=unresolved)
        briefing_text = briefing.formatted_briefing_text
        ai_recommendation = f"Escalate for human review ({risk.risk_level} risk, {eligibility.failed_count} failures)."
        letter_status = "not_generated"

    # Update record
    record["status"] = status
    record["ai_recommendation"] = ai_recommendation
    record["briefing_text"] = briefing_text
    record["generated_letter"] = generated_letter
    record["letter_validation_status"] = (
        "passed" if validation_result and validation_result.is_valid
        else ("flagged_hallucination" if validation_result and not validation_result.is_valid else None)
    )
    record["created_at"] = record.get("created_at", datetime.now().isoformat())
    record["updated_at"] = datetime.now().isoformat()

    if save_to_db:
        supabase.table("applications").insert(record).execute()

    return {
        "application_id": app_id,
        "status": status,
        "eligibility": eligibility.model_dump(),
        "risk": risk.model_dump(),
        "validation": validation_result.model_dump() if validation_result else None,
        "briefing_text": briefing_text,
        "generated_letter": generated_letter,
        "record": record,
    }
