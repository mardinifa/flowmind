"""
Escalation Briefing Generator
Builds actionable, structured briefings for loan officers to review complex/ambiguous applications.
"""

from typing import Dict, Any, List
from src.models import EscalationBriefing, EligibilityAssessment, RiskAssessment


def generate_escalation_briefing(
    record: Dict[str, Any],
    eligibility: EligibilityAssessment,
    risk: RiskAssessment,
    unresolved_questions: List[str] = None,
    recommended_action: str = None,
) -> EscalationBriefing:
    """
    Generates a structured briefing adhering to ClearPath Capital standards:
    - Summary Header
    - Eligibility checklist with verified evidence
    - Risk classification & reasoning
    - Core unresolved ambiguity / document flags
    - Actionable recommendation for the loan officer
    """
    app_id = record.get("id", "APP-UNKNOWN")
    b_name = record.get("business_name", "Unknown Business")
    a_name = record.get("applicant_name", "Unknown Applicant")
    amount = float(record.get("loan_amount", 0))
    turnover = float(record.get("monthly_turnover", 0))

    summary = (
        f"Application {app_id} by {a_name} ({b_name}) requesting ₦{amount:,.2f} "
        f"against ₦{turnover:,.2f}/mo average turnover."
    )

    # Build Eligibility Breakdown
    eligibility_lines = []
    for crit_key, crit in eligibility.criteria.items():
        status_icon = "[PASS]" if crit.passed else "[FAIL]"
        conf_tag = f"({crit.confidence.upper()} CONFIDENCE)"
        eligibility_lines.append(f"{status_icon} **{crit.criterion_name.replace('_', ' ').title()}**: {crit.reason} {conf_tag}")
        eligibility_lines.append(f"   *Evidence:* {crit.evidence}")
    eligibility_breakdown = "\n".join(eligibility_lines)

    # Build Risk Assessment Text
    fraud_warning = ""
    if risk.fraud_flags:
        fraud_warning = f"\n[!] **CRITICAL FRAUD / ANOMALY FLAGS**: {', '.join(risk.fraud_flags)}"

    risk_text = (
        f"**Risk Level:** {risk.risk_level} (Combined Confidence: {risk.confidence_score:.2f} | "
        f"Consistency: {risk.consistency_score:.2f} | Quality: {risk.explanation_quality_score:.2f})\n"
        f"**LLM Reasoning:** {risk.reasoning}{fraud_warning}"
    )

    # Unresolved Questions
    if not unresolved_questions:
        unresolved_questions = []
        if risk.risk_level == "High":
            unresolved_questions.append("High risk profile requires manual officer discretion on risk mitigation.")
        if eligibility.ambiguous_count > 0:
            unresolved_questions.append("One or more eligibility criteria have ambiguous documentation or borderline ratios.")
        if not unresolved_questions:
            unresolved_questions.append("Review standard terms before final disbursement authorization.")

    # Recommended Action
    if not recommended_action:
        if risk.fraud_flags or eligibility.failed_count >= 2:
            recommended_action = "Decline application or issue formal Request for Information for compliance audit."
        elif eligibility.overall_passed and risk.risk_level == "Medium":
            recommended_action = "Approve with standard covenants or request collateral verification."
        else:
            recommended_action = "Loan officer discretion required to decide Approve, Decline, or Request Info."

    # Formatted Markdown Briefing Text
    formatted_text = f"""### FlowMind Loan Officer Briefing
**Application ID:** {app_id} | **Business:** {b_name} | **Applicant:** {a_name}
**Requested Facility:** ₦{amount:,.2f} | **Monthly Turnover:** ₦{turnover:,.2f}

---

#### 1. Summary
{summary}

#### 2. Eligibility Assessment & Verifiable Evidence
{eligibility_breakdown}

#### 3. Risk Assessment & Model Reasoning
{risk_text}

#### 4. Unresolved Ambiguity & Key Questions
{chr(10).join(f"- {q}" for q in unresolved_questions)}

#### 5. Recommended Action
**Recommendation:** {recommended_action}
"""

    return EscalationBriefing(
        application_id=app_id,
        business_name=b_name,
        applicant_name=a_name,
        loan_amount=amount,
        summary=summary,
        eligibility_breakdown=eligibility_breakdown,
        risk_assessment=risk_text,
        unresolved_questions=unresolved_questions,
        recommended_action=recommended_action,
        formatted_briefing_text=formatted_text.strip(),
    )
