"""
FlowMind Configuration & Operational Thresholds
ClearPath Capital - Lagos, Nigeria
"""

from typing import Dict, Any, List

# Core Eligibility Thresholds
MIN_MONTHS_OPERATING: int = 12          # Business registered >= 12 months
MIN_APPLICANT_AGE: int = 21            # Minimum age 21
MAX_APPLICANT_AGE: int = 65            # Maximum age 65
MAX_LOAN_TO_TURNOVER_RATIO: float = 10.0  # Loan amount <= 10x average monthly turnover

# Approved and Prohibited Loan Purpose Categories
APPROVED_PURPOSE_CATEGORIES: List[str] = [
    "inventory_purchase",
    "equipment_acquisition",
    "working_capital",
    "business_expansion",
    "agriculture_supply",
    "raw_materials",
    "store_renovation",
    "logistics_and_transport",
]

PROHIBITED_PURPOSE_CATEGORIES: List[str] = [
    "cryptocurrency",
    "speculative_trading",
    "gambling",
    "personal_debt_refinancing",
    "luxury_goods",
    "unspecified_personal_use",
]

# Risk Classification & Confidence Thresholds
CONFIDENCE_HIGH_THRESHOLD: float = 0.85
CONFIDENCE_MEDIUM_THRESHOLD: float = 0.65

# Autonomous Decision Thresholds
AUTO_DECLINE_FAILED_CRITERIA_COUNT: int = 2  # Fail >= 2 criteria with high confidence -> Auto Decline
AUTO_APPROVE_ALLOWED_RISK: str = "Low"       # Auto approve only if risk is Low & 100% criteria pass

# Target System Metrics
TARGET_ESCALATION_RATE_MIN: float = 0.25     # Target 25-35% escalations
TARGET_ESCALATION_RATE_MAX: float = 0.35
MAX_ACCEPTABLE_OVERRIDE_RATE: float = 0.10   # Overrides should be < 10%

def get_current_thresholds() -> Dict[str, Any]:
    """Returns active operational thresholds."""
    return {
        "min_months_operating": MIN_MONTHS_OPERATING,
        "min_applicant_age": MIN_APPLICANT_AGE,
        "max_applicant_age": MAX_APPLICANT_AGE,
        "max_loan_to_turnover_ratio": MAX_LOAN_TO_TURNOVER_RATIO,
        "confidence_high_threshold": CONFIDENCE_HIGH_THRESHOLD,
        "confidence_medium_threshold": CONFIDENCE_MEDIUM_THRESHOLD,
        "auto_decline_failed_criteria_count": AUTO_DECLINE_FAILED_CRITERIA_COUNT,
        "target_escalation_rate_range": (TARGET_ESCALATION_RATE_MIN, TARGET_ESCALATION_RATE_MAX),
        "max_acceptable_override_rate": MAX_ACCEPTABLE_OVERRIDE_RATE,
    }

def analyze_calibration(
    total_apps: int,
    escalated_count: int,
    autonomous_count: int,
    human_overrides_count: int,
) -> Dict[str, Any]:
    """
    Analyzes whether current thresholds are too tight (causing excessive escalations)
    or too loose (causing high human override rates on autonomous decisions).
    """
    if total_apps == 0:
        return {
            "status": "INSUFFICIENT_DATA",
            "escalation_rate": 0.0,
            "override_rate": 0.0,
            "assessment": "No applications processed yet.",
            "recommendations": [],
        }

    escalation_rate = escalated_count / total_apps
    override_rate = (human_overrides_count / autonomous_count) if autonomous_count > 0 else 0.0

    recommendations = []
    status = "WELL_CALIBRATED"

    # Check for queue explosion (Thresholds too tight / conservative)
    if escalation_rate > TARGET_ESCALATION_RATE_MAX:
        status = "TOO_CONSERVATIVE"
        recommendations.append(
            f"Escalation rate ({escalation_rate:.1%}) exceeds target max ({TARGET_ESCALATION_RATE_MAX:.1%}). "
            "Consider loosening confidence bounds on standard retail inventory loans or adjusting turnover ratio tolerances."
        )

    # Check for excessive false confidence / human overrides (Thresholds too loose)
    if override_rate > MAX_ACCEPTABLE_OVERRIDE_RATE:
        status = "TOO_LOOSE_HIGH_OVERRIDES"
        recommendations.append(
            f"Human override rate ({override_rate:.1%}) exceeds threshold ({MAX_ACCEPTABLE_OVERRIDE_RATE:.1%}). "
            "Autonomous approvals are approving risky applications. Tighten self-consistency requirements."
        )

    if not recommendations:
        recommendations.append("System is operating within optimal bounds (25%-35% escalation, <10% override rate).")

    return {
        "status": status,
        "total_applications": total_apps,
        "escalation_rate": round(escalation_rate, 4),
        "override_rate": round(override_rate, 4),
        "recommendations": recommendations,
    }
