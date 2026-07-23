import json
from typing import Any

class JSONFormatter:
    """Formatador de saída para JSON AST (.json)."""

    @staticmethod
    def format(result: Any, indent: int = 2) -> str:
        data = {
            "metadata": {
                "file_path": result.file_path,
                "file_name": result.file_name,
                "total_pages": result.total_pages,
                "elapsed_seconds": round(result.elapsed_seconds, 4),
                "tier_distribution": result.tier_distribution,
            },
            "pages": [page.model_dump() if hasattr(page, "model_dump") else page.dict() for page in result.pages]
        }
        return json.dumps(data, ensure_ascii=False, indent=indent)
