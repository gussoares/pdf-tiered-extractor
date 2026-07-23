"""
pdf_tiered_extractor
--------------------
Biblioteca para extração progressiva/em cascata de documentos PDF para TXT, Markdown e JSON.
"""

from .core.pipeline import TieredPDFExtractor, ExtractionConfig, ExtractionResult, PageResult
from .core.analyzer import PageComplexityAnalyzer, PageComplexityReport
from .core.validator import DocumentValidator, CompletenessReport

__version__ = "0.1.0"
__all__ = [
    "TieredPDFExtractor",
    "ExtractionConfig",
    "ExtractionResult",
    "PageResult",
    "PageComplexityAnalyzer",
    "PageComplexityReport",
    "DocumentValidator",
    "CompletenessReport",
]
