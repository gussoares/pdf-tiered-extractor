from typing import Any

class TextFormatter:
    """Formatador de saída para Texto Puro (.txt)."""

    @staticmethod
    def format(result: Any) -> str:
        lines = []
        for page in result.pages:
            lines.append(f"--- PÁGINA {page.page_num + 1} (Tier {page.tier_used} - {page.engine}) ---")
            lines.append(page.text)
            lines.append("")
        return "\n".join(lines)
