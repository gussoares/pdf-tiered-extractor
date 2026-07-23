from typing import Any
import yaml

class MarkdownFormatter:
    """Formatador de saída para Markdown (.md) com Frontmatter YAML."""

    @staticmethod
    def format(result: Any) -> str:
        meta = {
            "source_file": result.file_name,
            "total_pages": result.total_pages,
            "elapsed_seconds": round(result.elapsed_seconds, 3),
            "tier_distribution": result.tier_distribution,
        }

        yaml_header = yaml.dump(meta, sort_keys=False, allow_unicode=True).strip()
        md_content = [f"---\n{yaml_header}\n---", ""]

        for page in result.pages:
            md_content.append(f"<!-- Page {page.page_num + 1} | Tier: {page.tier_used} | Engine: {page.engine} -->")
            md_content.append(page.markdown if page.markdown else page.text)
            md_content.append("")
            md_content.append("---")
            md_content.append("")

        return "\n".join(md_content)
