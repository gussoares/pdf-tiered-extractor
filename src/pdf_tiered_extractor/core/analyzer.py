import fitz
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PageComplexityReport(BaseModel):
    page_num: int
    char_count: int
    word_count: int
    image_count: int
    max_image_area_ratio: float = 0.0
    drawing_count: int
    table_count: int
    is_scanned: bool = False
    has_complex_drawings: bool = False
    has_tables: bool = False
    recommended_tier: int = 1  # 1: PyMuPDF, 2: Docling/Layout, 3: OCR
    details: Dict[str, Any] = Field(default_factory=dict)

class PageComplexityAnalyzer:
    """
    Analisador de complexidade de páginas de PDF via PyMuPDF.
    Calcula se a página é texto simples, layout com gráficos/tabelas ou imagem digitalizada (scan).
    """

    def __init__(
        self,
        min_char_threshold: int = 20,
        scanned_img_area_threshold: float = 0.70,
        drawing_complexity_threshold: int = 25,
    ):
        self.min_char_threshold = min_char_threshold
        self.scanned_img_area_threshold = scanned_img_area_threshold
        self.drawing_complexity_threshold = drawing_complexity_threshold

    def analyze_page(self, page: fitz.Page, page_num: int = 0) -> PageComplexityReport:
        rect = page.rect
        page_area = rect.width * rect.height if rect.width and rect.height else 1.0

        text = page.get_text("text") or ""
        char_count = len(text.strip())
        words = text.split()
        word_count = len(words)

        images = page.get_images() or []
        image_count = len(images)
        max_img_ratio = 0.0

        for img in images:
            xref = img[0]
            try:
                img_rects = page.get_image_rects(xref)
                for r in img_rects:
                    img_area = r.width * r.height
                    ratio = img_area / page_area
                    if ratio > max_img_ratio:
                        max_img_ratio = ratio
            except Exception:
                pass

        drawings = page.get_drawings() or []
        drawing_count = len(drawings)

        # Verificar presença de tabelas via detector do fitz
        table_count = 0
        try:
            tabs = page.find_tables()
            if tabs and hasattr(tabs, "tables"):
                table_count = len(tabs.tables)
        except Exception:
            table_count = 0

        # Uma página é considerada escaneada (Tier 3) se não possui texto nativo (char_count == 0)
        # OU se o texto é extremamente curto E há uma imagem ocupando a página (scan com OCR parcial).
        is_scanned = (char_count == 0) or (
            char_count < self.min_char_threshold and (image_count > 0 or max_img_ratio > self.scanned_img_area_threshold)
        )
        has_complex_drawings = drawing_count >= self.drawing_complexity_threshold
        has_tables = table_count > 0

        # Decisão do Tier Recomendado
        if is_scanned:
            recommended_tier = 3
        elif has_complex_drawings or (has_tables and max_img_ratio > 0.15):
            recommended_tier = 2
        else:
            recommended_tier = 1

        return PageComplexityReport(
            page_num=page_num,
            char_count=char_count,
            word_count=word_count,
            image_count=image_count,
            max_image_area_ratio=round(max_img_ratio, 4),
            drawing_count=drawing_count,
            table_count=table_count,
            is_scanned=is_scanned,
            has_complex_drawings=has_complex_drawings,
            has_tables=has_tables,
            recommended_tier=recommended_tier,
            details={
                "page_width": rect.width,
                "page_height": rect.height,
            }
        )
