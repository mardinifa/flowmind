# FlowMind Edge Cases & Fault Tolerance Report

**Client:** ClearPath Capital (Lagos, Nigeria)  
**System:** FlowMind Intelligent Workflow Automation  
**Reference:** Day 5 Intake Edge Cases & Calibration Support

---

## 1. Summary of Edge Cases Tested

| Edge Case | Test Scenario | System Action | Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Scanned / Flat Image-Only PDF** | Uploaded CAC Certificate with 0 selectable text characters (flat scan). | Detected `<30` characters of extractable text stream; flagged `SCANNED_IMAGE_ONLY_NO_TEXT` & `requires_ocr`. | Escalated gracefully to loan officer with OCR alert; zero system crash. | **PASSED** |
| **2. Truncated / Corrupt PDF Byte Stream** | Incomplete PDF upload with truncated EOF / malformed xref table. | Trapped `fitz.FileDataError` / EOF within safe extractor wrapper; flagged `CORRUPTED_OR_TRUNCATED_PDF`. | Escalated gracefully to queue with file corruption diagnostic. | **PASSED** |
| **3. Identity & Bank Statement Name Mismatch** | Form submitted by "Babajide Sanwo" for "Sanwo Trading", but bank statement in the name of "Continental Mega Mining & Dredging Ltd". | Fuzzy entity normalizer detected 0 common tokens; flagged `CRITICAL_NAME_MISMATCH`. | Classified as **High Risk** (Confidence 0.94) with explicit fraud reasoning; routed to compliance. | **PASSED** |

---

## 2. Detailed Technical Deep-Dive

### Case 1: Scanned / Image-Only PDF

#### The Problem:
Many SME owners in Lagos upload smartphone photos of CAC certificates or flat photocopied documents saved as PDFs. Standard PDF text extraction (`fitz.get_text()`) returns empty strings, which could lead naive pipelines to crash or register missing fields with false certainty.

#### FlowMind Defense Implementation (`src/intake/pdf_extractor.py`):
```python
if len(combined_text) < 30:
    flags.append("SCANNED_IMAGE_ONLY_NO_TEXT")
    return DocumentIntakeResult(
        is_successful=False,
        extracted_text="",
        is_scanned=True,
        is_corrupted=False,
        extraction_status="requires_ocr",
        flags=flags,
        metadata=metadata,
    )
```

#### What the System Did:
1. PyMuPDF verified the PDF container structure.
2. The character count across all pages was detected as `<30` chars, while embedded image headers were present.
3. The system marked `is_scanned = True` and set `extraction_status = "requires_ocr"`.
4. In the pipeline, the application was routed to the **Loan Officer Queue** with a briefing instructing the officer to visually inspect the document image.
5. **Verified by Test:** `tests/test_intake_edge_cases.py::test_scanned_image_only_pdf_fails_gracefully`.

---

### Case 2: Truncated / Corrupted PDF Bytes

#### The Problem:
Network drops or incomplete form submissions can send truncated byte streams (e.g. truncated after 512 bytes). Standard libraries raise fatal `FileDataError` or `EOFError`, crashing web services if unhandled.

#### FlowMind Defense Implementation (`src/intake/pdf_extractor.py`):
```python
except (fitz.FileDataError, fitz.EmptyFileError, ValueError, IOError, Exception) as e:
    return DocumentIntakeResult(
        is_successful=False,
        extracted_text="",
        is_scanned=False,
        is_corrupted=True,
        extraction_status="corrupted_file",
        flags=["CORRUPTED_OR_TRUNCATED_PDF", f"PARSE_ERROR: {str(e)}"],
        metadata={"error_detail": str(e)},
    )
```

#### What the System Did:
1. The parser intercepted the malformed byte stream.
2. The exception was safely trapped and transformed into a structured `DocumentIntakeResult`.
3. The pipeline flagged `CORRUPTED_DOCUMENT_UPLOAD` and created an escalation record requesting a re-upload.
4. **Verified by Test:** `tests/test_intake_edge_cases.py::test_truncated_corrupt_pdf_fails_gracefully`.

---

### Case 3: Identity & Bank Statement Name Mismatch (Fraud Detection)

#### The Problem:
Loan applicants attempting to inflate eligibility may submit a third-party corporate bank statement belonging to a different company or individual.

#### FlowMind Defense Implementation (`src/risk/fraud_detector.py`):
```python
norm_applicant = normalize_name(applicant_name)
norm_business = normalize_name(business_name)
norm_bank = normalize_name(bank_account_name)

matches_applicant = len(applicant_tokens.intersection(bank_tokens)) >= 1
matches_business = len(business_tokens.intersection(bank_tokens)) >= 1

if not matches_applicant and not matches_business:
    flag = f"CRITICAL_NAME_MISMATCH: Bank statement is in the name of '{bank_account_name}', which does not match applicant '{applicant_name}' or business '{business_name}'."
    return False, [flag], reasoning
```

#### What the System Did:
1. Cross-referenced `applicant_name` ("Babajide Sanwo") and `business_name` ("Sanwo Trading Ventures") against `bank_statement_account_name` ("Continental Mega Mining & Dredging Ltd").
2. Detected a zero-token overlap.
3. Automatically classified the application as **High Risk** with 100% self-consistency confidence.
4. Generated an escalation briefing explicitly warning the loan officer:
   > *"CRITICAL ANOMALY: Bank statement account name ('Continental Mega Mining & Dredging Ltd') completely conflicts with applicant identity ('Sanwo Trading Ventures / Babajide Sanwo')."*
5. **Verified by Test:** `tests/test_fraud_detection.py::test_fraudulent_name_mismatch_application`.
