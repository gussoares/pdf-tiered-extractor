import fitz
import pytest
from pdf_tiered_extractor.core.analyzer import PageComplexityAnalyzer

def test_analyzer_with_synthetic_pdf():
    # Criar um PDF sintético em memória via fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), "Este é um teste de texto nativo em PDF para validação do Tier 1.")
    
    analyzer = PageComplexityAnalyzer()
    report = analyzer.analyze_page(page, page_num=0)
    
    assert report.page_num == 0
    assert report.word_count > 5
    assert report.recommended_tier == 1
    assert report.is_scanned is False
    doc.close()

def test_analyzer_detects_empty_scanned_page():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    # Página sem texto
    analyzer = PageComplexityAnalyzer(min_char_threshold=20)
    report = analyzer.analyze_page(page, page_num=0)
    
    assert report.char_count == 0
    # Como não tem texto e imagem = 0, cai para scanned ou tier 3
    assert report.recommended_tier == 3
    doc.close()
