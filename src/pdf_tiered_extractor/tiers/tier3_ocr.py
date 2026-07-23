import fitz
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Tier3OCRExtractor:
    """
    Extrator Tier 3 (OCR / Visão para Páginas Escaneadas).
    Utiliza PyMuPDF OCR (get_textpage_ocr / Tesseract) ou rotinas de OCR.
    """

    def __init__(self, language: str = "por+eng"):
        self.language = language

    def extract_page(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """
        Executa extração OCR na página.
        """
        ocr_text = ""
        engine = "PyMuPDF OCR (Tesseract)"

        try:
            # Tentar PyMuPDF get_textpage_ocr
            tp = page.get_textpage_ocr(language=self.language, full=True)
            ocr_text = tp.get_text() or ""
        except Exception as e:
            logger.debug(f"PyMuPDF OCR não disponível para página {page_num}: {e}. Tentando extração padrão de texto da imagem.")
            # Fallback para texto bruto + indicação de página digitalizada
            raw_text = page.get_text("text") or ""
            if raw_text.strip():
                ocr_text = raw_text
                engine = "PyMuPDF Direct (Fallback - Tesseract não configurado)"
            else:
                ocr_text = f"[PÁGINA DIGITALIZADA / SCAN - PÁGINA {page_num + 1}]"
                engine = "Scan Detector (OCR necessário)"

        return {
            "tier_used": 3,
            "text": ocr_text.strip(),
            "markdown": ocr_text.strip(),
            "blocks": [],
            "tables": [],
            "engine": engine
        }
