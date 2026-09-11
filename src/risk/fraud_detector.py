"""
Fraud & Anomaly Detection Module
Detects critical red flags such as identity and bank statement account name mismatches.
"""

from typing import Dict, Any, List, Tuple
import re

def normalize_name(name: str) -> str:
    """Cleans up business and personal names for fuzzy token matching."""
    if not name:
        return ""
    # Remove common corporate suffixes
    clean = re.sub(r"\b(ltd|limited|plc|enterprises|enterprise|ventures|services|global|logistics|consulting|co|inc|and|&)\b", "", name.lower())
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", clean)
    return " ".join(clean.split())

def check_identity_and_name_consistency(record: Dict[str, Any]) -> Tuple[bool, List[str], str]:
    """
    Checks if the name on the bank statement matches either:
    1. The applicant's personal name
    2. The registered business name
    
    Returns: (is_consistent, flags, reasoning)
    """
    applicant_name = record.get("applicant_name") or ""
    business_name = record.get("business_name") or ""
    bank_account_name = record.get("bank_statement_account_name") or ""

    if not bank_account_name:
        return False, ["MISSING_BANK_ACCOUNT_NAME"], "Bank statement account name is not provided."

    norm_applicant = normalize_name(applicant_name)
    norm_business = normalize_name(business_name)
    norm_bank = normalize_name(bank_account_name)

    # Check for direct or significant token overlap
    applicant_tokens = set(norm_applicant.split())
    business_tokens = set(norm_business.split())
    bank_tokens = set(norm_bank.split())

    matches_applicant = len(applicant_tokens.intersection(bank_tokens)) >= 1
    matches_business = len(business_tokens.intersection(bank_tokens)) >= 1

    if matches_applicant or matches_business:
        return True, [], f"Bank account name ('{bank_account_name}') matches applicant or business entity."
    else:
        flag = f"CRITICAL_NAME_MISMATCH: Bank statement is in the name of '{bank_account_name}', which does not match applicant '{applicant_name}' or business '{business_name}'."
        reasoning = (
            f"Severe identity contradiction detected. The bank account holder name ('{bank_account_name}') "
            f"shares no common identifier with applicant ('{applicant_name}') or business ('{business_name}'). "
            "High probability of fraudulent or third-party financial document submission."
        )
        return False, [flag], reasoning
