import os
import fitz
import tempfile
import pytest
from pdf_tiered_extractor.core.validator import DocumentValidator

def test_validator_valid_pdf():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 100), "Página de teste válida.")
    doc.save(pdf_path)
    doc.close()

    try:
        report = DocumentValidator.validate_pdf(pdf_path)
        assert report.is_complete is True
        assert report.total_pages == 1
        assert report.file_size_bytes > 0
        assert len(report.issues) == 0
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

def test_validator_empty_file():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    try:
        report = DocumentValidator.validate_pdf(pdf_path)
        assert report.is_complete is False
        assert report.file_size_bytes == 0
        assert any("vazio" in issue for issue in report.issues)
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

def test_validator_corrupted_file():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"Este nao e um arquivo PDF valido!")
        pdf_path = tmp.name

    try:
        report = DocumentValidator.validate_pdf(pdf_path)
        assert report.is_complete is False
        assert len(report.issues) > 0
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
