"""
Intake Edge Cases Test Suite
Tests scanned/image-only PDFs and truncated/corrupt PDFs.
Must fail gracefully with clear flags, never crash.
"""

import pytest
import pymupdf as fitz
from src.intake.pdf_extractor import extract_text_from_pdf


def test_standard_searchable_pdf():
    """
    Verifies that standard digital PDFs with text are parsed successfully.
    """
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "CAC Certificate of Incorporation\nRC-982104\nBusiness: Golden Grains Ltd")
    pdf_bytes = doc.write()
    doc.close()

    result = extract_text_from_pdf(pdf_bytes)

    assert result.is_successful is True
    assert result.is_scanned is False
    assert result.is_corrupted is False
    assert "Golden Grains Ltd" in result.extracted_text
    assert result.extraction_status == "completed"


def test_scanned_image_only_pdf_fails_gracefully():
    """
    Intake Edge Case 1: Scanned/image-only PDF with no selectable text layer.
    Must not crash. Must return is_scanned=True, extraction_status='requires_ocr'.
    """
    # Create an empty or image-only blank canvas PDF
    doc = fitz.open()
    doc.new_page()  # Page with 0 text characters
    pdf_bytes = doc.write()
    doc.close()

    result = extract_text_from_pdf(pdf_bytes)

    assert result.is_successful is False
    assert result.is_scanned is True
    assert result.is_corrupted is False
    assert result.extraction_status == "requires_ocr"
    assert "SCANNED_IMAGE_ONLY_NO_TEXT" in result.flags


def test_truncated_corrupt_pdf_fails_gracefully():
    """
    Intake Edge Case 2: Truncated / malformed byte stream.
    Must catch EOFError / FileDataError gracefully and never crash.
    """
    # Malformed / truncated PDF byte stream
    corrupted_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n[TRUNCATED_EOF"

    result = extract_text_from_pdf(corrupted_bytes)

    assert result.is_successful is False
    assert result.is_corrupted is True
    assert result.extraction_status == "corrupted_file"
    assert any("CORRUPTED_OR_TRUNCATED_PDF" in f or "PARSE_ERROR" in f for f in result.flags)
