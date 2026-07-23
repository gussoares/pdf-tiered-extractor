import os
import fitz
import tempfile
import pytest
from pdf_tiered_extractor import TieredPDFExtractor, ExtractionConfig

def test_pipeline_synthetic_pdf():
    # Criar PDF temporário em disco
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 100), "Primeira página do documento.")
    p2 = doc.new_page()
    p2.insert_text((50, 100), "Segunda página do documento com mais conteúdo.")
    doc.save(pdf_path)
    doc.close()

    try:
        extractor = TieredPDFExtractor()
        res = extractor.process_pdf(pdf_path)

        assert res.total_pages == 2
        assert len(res.pages) == 2
        assert res.pages[0].tier_used == 1
        assert "Primeira página" in res.pages[0].text
        
        # Testar exportação
        txt_out = res.to_text()
        md_out = res.to_markdown()
        json_out = res.to_json()

        assert "PÁGINA 1" in txt_out
        assert "source_file" in md_out
        assert '"total_pages": 2' in json_out

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
