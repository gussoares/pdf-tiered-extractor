import os
import time
import fitz
import logging
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from .analyzer import PageComplexityAnalyzer, PageComplexityReport
from ..tiers.tier1_pymupdf import Tier1PyMuPDFExtractor
from ..tiers.tier2_docling import Tier2DoclingExtractor
from ..tiers.tier3_ocr import Tier3OCRExtractor
from ..formatters.text_formatter import TextFormatter
from ..formatters.markdown_formatter import MarkdownFormatter
from ..formatters.json_formatter import JSONFormatter

logger = logging.getLogger(__name__)

class ExtractionConfig(BaseModel):
    forced_tier: Optional[int] = None  # None = Decisão automática por complexidade
    ocr_language: str = "por+eng"
    max_pages: Optional[int] = None
    min_char_threshold: int = 40
    drawing_threshold: int = 25

class PageResult(BaseModel):
    page_num: int
    tier_used: int
    engine: str
    text: str
    markdown: str
    blocks: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    complexity: PageComplexityReport

class ExtractionResult(BaseModel):
    file_path: str
    file_name: str
    total_pages: int
    elapsed_seconds: float
    tier_distribution: Dict[str, int]
    pages: List[PageResult]

    def to_text(self) -> str:
        return TextFormatter.format(self)

    def to_markdown(self) -> str:
        return MarkdownFormatter.format(self)

    def to_json(self, indent: int = 2) -> str:
        return JSONFormatter.format(self, indent=indent)

class TieredPDFExtractor:
    """
    Orquestrador de extração progressiva/em cascata de PDFs.
    """

    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        self.analyzer = PageComplexityAnalyzer(
            min_char_threshold=self.config.min_char_threshold,
            drawing_complexity_threshold=self.config.drawing_threshold,
        )
        self.tier1_engine = Tier1PyMuPDFExtractor()
        self.tier2_engine = Tier2DoclingExtractor()
        self.tier3_engine = Tier3OCRExtractor(language=self.config.ocr_language)

    def process_pdf(self, pdf_path: str) -> ExtractionResult:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")

        start_time = time.time()
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_process = min(total_pages, self.config.max_pages) if self.config.max_pages else total_pages

        page_results: List[PageResult] = []
        tier_counts = {"tier1": 0, "tier2": 0, "tier3": 0}

        for p_idx in range(pages_to_process):
            page = doc[p_idx]
            report = self.analyzer.analyze_page(page, page_num=p_idx)

            # Determinar o tier a ser utilizado
            selected_tier = self.config.forced_tier if self.config.forced_tier is not None else report.recommended_tier

            extracted_data = {}
            if selected_tier == 1:
                extracted_data = self.tier1_engine.extract_page(page, p_idx)
                tier_counts["tier1"] += 1
            elif selected_tier == 2:
                extracted_data = self.tier2_engine.extract_page(page, p_idx, pdf_path=pdf_path)
                tier_counts["tier2"] += 1
            else:
                extracted_data = self.tier3_engine.extract_page(page, p_idx)
                tier_counts["tier3"] += 1

            page_results.append(PageResult(
                page_num=p_idx,
                tier_used=extracted_data.get("tier_used", selected_tier),
                engine=extracted_data.get("engine", f"Tier {selected_tier}"),
                text=extracted_data.get("text", ""),
                markdown=extracted_data.get("markdown", ""),
                blocks=extracted_data.get("blocks", []),
                tables=extracted_data.get("tables", []),
                complexity=report
            ))

        doc.close()
        elapsed = time.time() - start_time

        return ExtractionResult(
            file_path=os.path.abspath(pdf_path),
            file_name=os.path.basename(pdf_path),
            total_pages=pages_to_process,
            elapsed_seconds=elapsed,
            tier_distribution=tier_counts,
            pages=page_results
        )
