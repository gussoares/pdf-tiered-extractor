import os
import fitz
import tempfile
import pytest
from pdf_tiered_extractor import TieredPDFExtractor, ExtractionConfig

def test_pipeline_empty_page_triggers_ocr():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    # Criar uma página sem texto (vazia/escaneada)
    _ = doc.new_page()
    doc.save(pdf_path)
    doc.close()

    try:
        extractor = TieredPDFExtractor(config=ExtractionConfig(verify_completeness=True))
        result = extractor.process_pdf(pdf_path)

        assert result.total_pages == 1
        assert result.completeness is not None
        assert result.completeness.is_complete is True
        assert result.pages[0].complexity.requires_image_ocr is True
        # Como não há texto nativo, deve conter indicativo de OCR ou scan
        assert len(result.pages[0].text) > 0
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

def test_pipeline_hybrid_page_with_images():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Texto nativo da petição.")
    
    # Criar uma pequena imagem em memória e desenhar na página
    pix = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 100, 100), 0)
    pix.clear_with(255)
    page.insert_image(fitz.Rect(100, 100, 300, 300), pixmap=pix)

    doc.save(pdf_path)
    doc.close()

    try:
        extractor = TieredPDFExtractor(config=ExtractionConfig(extract_image_text_on_demand=True))
        result = extractor.process_pdf(pdf_path)

        assert result.total_pages == 1
        assert result.pages[0].complexity.has_images is True
        assert "Texto nativo" in result.pages[0].text
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
