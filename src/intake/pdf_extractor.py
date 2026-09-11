"""
Resilient PDF Intake & Extraction Module
Handles standard text PDFs, flat scanned/image-only PDFs, and truncated/corrupt files.
"""

import io
from typing import Union, Dict, Any
import pymupdf as fitz
from src.models import DocumentIntakeResult


def extract_text_from_pdf(pdf_source: Union[bytes, str, io.BytesIO]) -> DocumentIntakeResult:
    """
    Extracts text from a PDF file path or raw bytes with graceful edge case handling:
    - Corrupt / Truncated PDF: caught safely, flags file without crashing.
    - Scanned / Image-only PDF: detects lack of text stream, flags for manual OCR / inspection.
    - Standard PDF: extracts text and metadata cleanly.
    """
    flags = []
    metadata: Dict[str, Any] = {}

    try:
        # Load PDF from bytes or file path
        if isinstance(pdf_source, bytes):
            doc = fitz.open(stream=pdf_source, filetype="pdf")
        elif isinstance(pdf_source, io.BytesIO):
            doc = fitz.open(stream=pdf_source.getvalue(), filetype="pdf")
        elif isinstance(pdf_source, str):
            doc = fitz.open(pdf_source)
        else:
            return DocumentIntakeResult(
                is_successful=False,
                is_corrupted=True,
                extraction_status="corrupted_file",
                flags=["INVALID_PDF_SOURCE_TYPE"],
                metadata={"error": "Unsupported source type"},
            )

        page_count = len(doc)
        metadata["page_count"] = page_count

        if page_count == 0:
            return DocumentIntakeResult(
                is_successful=False,
                is_corrupted=True,
                extraction_status="corrupted_file",
                flags=["CORRUPTED_OR_TRUNCATED_PDF", "EMPTY_PDF_NO_PAGES"],
                metadata=metadata,
            )

        full_text = []
        has_images = False

        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                full_text.append(text)
            
            image_list = page.get_images()
            if image_list:
                has_images = True

        combined_text = "\n\n".join(full_text).strip()
        metadata["character_count"] = len(combined_text)
        metadata["has_embedded_images"] = has_images

        # Check for Scanned / Image-Only Edge Case
        # If there are pages/images but practically zero extractable character stream
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

        return DocumentIntakeResult(
            is_successful=True,
            extracted_text=combined_text,
            is_scanned=False,
            is_corrupted=False,
            extraction_status="completed",
            flags=[],
            metadata=metadata,
        )

    except (fitz.FileDataError, fitz.EmptyFileError, ValueError, IOError, Exception) as e:
        # Graceful degradation on corrupted / truncated files
        return DocumentIntakeResult(
            is_successful=False,
            extracted_text="",
            is_scanned=False,
            is_corrupted=True,
            extraction_status="corrupted_file",
            flags=["CORRUPTED_OR_TRUNCATED_PDF", f"PARSE_ERROR: {str(e)}"],
            metadata={"error_detail": str(e)},
        )
