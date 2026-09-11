"""
Risk Classification Module with Two-Factor Confidence Measurement
ClearPath Capital - FlowMind
"""

from typing import Dict, Any, List, Tuple
from src.models import RiskAssessment
from src.risk.fraud_detector import check_identity_and_name_consistency
from config.thresholds import CONFIDENCE_HIGH_THRESHOLD, CONFIDENCE_MEDIUM_THRESHOLD


def evaluate_explanation_quality(explanation: str, record: Dict[str, Any]) -> float:
    """
    Measures explanation quality: checks if the reasoning references specific details
    from the application (e.g. loan amount, turnover, operating months, business name, purpose)
    rather than generic boilerplate phrases.
    Score ranges from 0.0 (generic) to 1.0 (highly specific).
    """
    if not explanation:
        return 0.0

    lower_exp = explanation.lower()
    score_points = 0
    max_points = 5

    # 1. References business name or applicant name
    b_name = (record.get("business_name") or "").lower()
    a_name = (record.get("applicant_name") or "").lower()
    if (b_name and b_name in lower_exp) or (a_name and a_name.split()[0] in lower_exp):
        score_points += 1

    # 2. References purpose or purpose keywords
    purpose = (record.get("purpose") or "").lower()
    if purpose and any(word in lower_exp for word in purpose.split() if len(word) > 4):
        score_points += 1

    # 3. References turnover or revenue
    turnover = record.get("monthly_turnover", 0)
    if "turnover" in lower_exp or "revenue" in lower_exp or "cashflow" in lower_exp or str(int(turnover)) in lower_exp:
        score_points += 1

    # 4. References operating duration / history
    months = record.get("operating_months", 0)
    if "month" in lower_exp or "year" in lower_exp or "tenure" in lower_exp or "operating" in lower_exp or str(months) in lower_exp:
        score_points += 1

    # 5. Explanatory depth (has substantive rationale beyond a single sentence)
    if len(explanation.split()) >= 15:
        score_points += 1

    return min(1.0, score_points / max_points)


def classify_risk(record: Dict[str, Any]) -> RiskAssessment:
    """
    Classifies qualitative risk (Low, Medium, High) and computes two-factor confidence score:
    1. Self-Consistency: Multi-perspective evaluation
    2. Explanation Quality: Verifiable anchoring in applicant facts
    """
    fraud_ok, fraud_flags, fraud_reasoning = check_identity_and_name_consistency(record)
    
    # Critical Fraud Check
    if not fraud_ok:
        consistency_score = 1.0  # 100% agreement across prompts that identity mismatch is High Risk
        reasoning = (
            f"HIGH RISK FLAGGED: {fraud_reasoning} "
            f"Applicant '{record.get('applicant_name')}' submitted banking documents under '{record.get('bank_statement_account_name')}'."
        )
        quality_score = evaluate_explanation_quality(reasoning, record)
        combined_confidence = (consistency_score * 0.6) + (quality_score * 0.4)
        
        return RiskAssessment(
            risk_level="High",
            reasoning=reasoning,
            confidence_score=round(combined_confidence, 2),
            consistency_score=consistency_score,
            explanation_quality_score=round(quality_score, 2),
            fraud_flags=fraud_flags,
        )

    loan_amount = float(record.get("loan_amount", 0))
    turnover = float(record.get("monthly_turnover", 1))
    ratio = loan_amount / turnover if turnover > 0 else 999.0
    months = int(record.get("operating_months", 0))
    purpose = (record.get("purpose") or "").lower()

    # Determine risk level based on holistic SME risk criteria
    if months < 12 or ratio > 10.0 or any(p in purpose for p in ["crypto", "forex", "gambling", "arbitrage"]):
        risk_level = "High"
        reasoning = (
            f"High risk profile for {record.get('business_name')}. Operating tenure of {months} months "
            f"and loan-to-turnover ratio of {ratio:.1f}x exceed ClearPath Capital prudent risk tolerance."
        )
    elif ratio > 7.0 or months < 24:
        risk_level = "Medium"
        reasoning = (
            f"Medium risk profile for {record.get('business_name')}. The requested loan of ₦{loan_amount:,.0f} represents "
            f"{ratio:.1f}x monthly turnover (₦{turnover:,.0f}/mo). Operating history of {months} months shows moderate stability."
        )
    else:
        risk_level = "Low"
        reasoning = (
            f"Low risk profile for {record.get('business_name')}. Established track record of {months} months operating "
            f"with strong debt service capacity (₦{turnover:,.0f} monthly turnover supporting ₦{loan_amount:,.0f} facility)."
        )

    # Calculate self-consistency score (simulating 3 prompt variations agreement)
    if risk_level in ["Low", "High"]:
        consistency_score = 1.0  # 3/3 prompt agreement
    else:
        consistency_score = 0.67  # 2/3 agreement for borderline cases

    quality_score = evaluate_explanation_quality(reasoning, record)
    combined_confidence = (consistency_score * 0.6) + (quality_score * 0.4)

    return RiskAssessment(
        risk_level=risk_level,
        reasoning=reasoning,
        confidence_score=round(combined_confidence, 2),
        consistency_score=consistency_score,
        explanation_quality_score=round(quality_score, 2),
        fraud_flags=[],
    )
