import fitz
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Tier1PyMuPDFExtractor:
    """
    Extrator Tier 1 (Ultrarrápido / Determinístico).
    Utiliza PyMuPDF (`fitz`) e `pymupdf4llm` para extrair texto, blocos e tabelas de páginas nativas.
    """

    def __init__(self):
        self._has_pymupdf4llm = False
        try:
            import pymupdf4llm
            self._has_pymupdf4llm = True
        except ImportError:
            self._has_pymupdf4llm = False

    def extract_page(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """
        Extrai o conteúdo de uma página utilizando PyMuPDF.
        Retorna dicionário contendo texto, markdown e blocos estruturados.
        """
        text_plain = page.get_text("text") or ""
        
        # Tentar extrair Markdown via pymupdf4llm se disponível, ou fallback para get_text("markdown")
        markdown_content = ""
        if self._has_pymupdf4llm:
            try:
                import pymupdf4llm
                doc = page.parent
                # pymupdf4llm.to_markdown aceita lista de páginas 0-indexed
                md_res = pymupdf4llm.to_markdown(doc, pages=[page_num])
                if isinstance(md_res, str):
                    markdown_content = md_res
            except Exception as e:
                logger.debug(f"Falha no pymupdf4llm para página {page_num}: {e}")
        
        if not markdown_content:
            try:
                markdown_content = page.get_text("markdown") or text_plain
            except Exception:
                markdown_content = text_plain

        # Extração de blocos para JSON AST
        blocks_data = []
        raw_blocks = page.get_text("blocks") or []
        for b in raw_blocks:
            # b: (x0, y0, x1, y1, text, block_no, block_type)
            if len(b) >= 7:
                blocks_data.append({
                    "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
                    "text": b[4].strip(),
                    "block_no": b[5],
                    "type": "image" if b[6] == 1 else "text"
                })

        # Extração de tabelas nativas
        tables_data = []
        try:
            tabs = page.find_tables()
            if tabs and hasattr(tabs, "tables"):
                for tab in tabs.tables:
                    tables_data.append({
                        "bbox": tab.bbox,
                        "rows": tab.extract(),
                        "row_count": len(tab.rows),
                        "col_count": len(tab.header.names) if hasattr(tab, "header") and tab.header else 0
                    })
        except Exception as e:
            logger.debug(f"Falha ao extrair tabelas nativas fitz página {page_num}: {e}")

        return {
            "tier_used": 1,
            "text": text_plain.strip(),
            "markdown": markdown_content.strip(),
            "blocks": blocks_data,
            "tables": tables_data,
            "engine": "PyMuPDF (fitz)" + (" + pymupdf4llm" if self._has_pymupdf4llm else "")
        }
