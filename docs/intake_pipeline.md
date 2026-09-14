# FlowMind Intake and Document-Extraction Pipeline

## Purpose

The intake stage receives a loan application, reads any attached PDF and
converts the submitted information into a structured record for eligibility
checking, risk classification and decision routing.

## Input Methods

FlowMind supports two application-entry methods:

1. Structured JSON submitted to the FastAPI processing endpoint.
2. Multipart form submission containing application fields and an optional
   PDF document.

The main endpoints are:

- `POST /api/v1/applications/process`
- `POST /api/v1/applications/submit`

## Structured Application Record

Each application contains fields such as:

- application ID;
- applicant name and age;
- business name and registration number;
- operating duration;
- requested loan amount;
- average monthly turnover;
- loan purpose and category;
- bank-statement account name;
- processing status and audit information.

The Pydantic schemas are defined in `src/models.py`.

## PDF Extraction

PDF processing is implemented in:

`src/intake/pdf_extractor.py`

PyMuPDF extracts text and document metadata. The intake module identifies:

- standard searchable PDFs;
- image-only or scanned PDFs requiring OCR;
- corrupted or truncated files;
- documents that cannot be interpreted safely.

A document failure does not crash the entire workflow. Instead, the application
is escalated for human inspection or document resubmission.

## Operating-Duration Validation

The Day 7 adversarial review found that the original eligibility engine trusted
the extracted `operating_months` value without checking its source.

The module `src/intake/date_validator.py` now compares the reported duration
with the completed months calculated from:

- `business_start_date`;
- `assessment_date`.

If the difference is greater than one month, FlowMind treats the record as
contradictory and prevents autonomous approval or decline. The application is
sent to a loan officer with an explanation.

## Intake Flow

1. The application enters FastAPI.
2. A unique application ID is assigned if none was supplied.
3. Any attached PDF is passed to the extraction module.
4. Document status and warning flags are recorded.
5. Operating duration is cross-checked when source dates are available.
6. Structured data is passed to the eligibility and risk modules.
7. Unreadable or contradictory records are escalated.
8. The application and final action are stored in the database.

## Fault-Tolerance Tests

The automated test suite covers:

- searchable PDF extraction;
- scanned image-only PDFs;
- corrupted or truncated PDF data;
- contradictory operating duration;
- missing or invalid application information.

Relevant tests include:

- `tests/test_intake_edge_cases.py`
- `tests/test_day7_challenges.py`
- `tests/test_full_integration.py`

## Current Limitations

- Image-only PDFs are identified but full OCR is not included.
- Extracted free text is not yet mapped automatically into every structured
  application field.
- Source dates are optional for compatibility with existing records.
- Production deployment would require malware scanning, file-size limits,
  encryption, authentication and secure document retention.

## Conclusion

The intake pipeline converts submitted information into a traceable structured
record and fails safely when documents are corrupted, scanned or contradictory.
It does not allow uncertain document evidence to silently produce an
autonomous decision.
