import fitz
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Tier2DoclingExtractor:
    """
    Extrator Tier 2 (Estruturado / Layout AI).
    Utiliza IBM Docling para parser avançado de documentos com tabelas complexas e layouts ricos.
    Caso o módulo docling não esteja instalado, realiza fallback gracioso para o Tier 1 com aviso.
    """

    def __init__(self):
        self.docling_available = False
        try:
            from docling.document_converter import DocumentConverter
            self.DocumentConverter = DocumentConverter
            self.docling_available = True
        except ImportError:
            self.docling_available = False

    def extract_page(self, page: fitz.Page, page_num: int, pdf_path: str = None) -> Dict[str, Any]:
        """
        Extrai o conteúdo de uma página via Docling ou Fallback.
        """
        if self.docling_available and pdf_path:
            try:
                converter = self.DocumentConverter()
                # Em Docling 2.x, a faixa de páginas específica é passada via page_range=(start, end)
                page_1indexed = page_num + 1
                result = converter.convert(pdf_path, page_range=(page_1indexed, page_1indexed))
                doc = result.document
                md_text = doc.export_to_markdown()
                return {
                    "tier_used": 2,
                    "text": md_text.strip(),
                    "markdown": md_text.strip(),
                    "blocks": [],
                    "tables": [],
                    "engine": "IBM Docling"
                }
            except Exception as e:
                logger.warning(f"Erro no processamento do Docling na página {page_num}: {e}. Ativando fallback.")

        # Fallback gracioso usando PyMuPDF
        text_plain = page.get_text("text") or ""
        md_text = page.get_text("markdown") or text_plain
        return {
            "tier_used": 2,
            "text": text_plain.strip(),
            "markdown": md_text.strip(),
            "blocks": [],
            "tables": [],
            "engine": "Docling (fallback PyMuPDF - docling ausente ou erro)"
        }
