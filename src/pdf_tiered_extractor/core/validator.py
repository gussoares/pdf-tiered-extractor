import os
import fitz
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CompletenessReport(BaseModel):
    file_path: str
    file_name: str
    file_size_bytes: int
    is_complete: bool
    total_pages: int = 0
    is_encrypted: bool = False
    is_repaired: bool = False
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)

class DocumentValidator:
    """
    Validador de integridade e completitude de arquivos PDF de processos.
    Verifica integridade do cabeçalho, estrutura das páginas e ausência de corrupção.
    """

    @staticmethod
    def validate_pdf(pdf_path: str) -> CompletenessReport:
        abs_path = os.path.abspath(pdf_path)
        base_name = os.path.basename(pdf_path)

        if not os.path.exists(abs_path):
            return CompletenessReport(
                file_path=abs_path,
                file_name=base_name,
                file_size_bytes=0,
                is_complete=False,
                issues=[f"Arquivo não encontrado: {pdf_path}"]
            )

        file_size = os.path.getsize(abs_path)
        if file_size == 0:
            return CompletenessReport(
                file_path=abs_path,
                file_name=base_name,
                file_size_bytes=0,
                is_complete=False,
                issues=["Arquivo de PDF está vazio (0 bytes)."]
            )

        issues: List[str] = []
        warnings: List[str] = []
        is_encrypted = False
        is_repaired = False
        total_pages = 0
        header_valid = False

        # Verificar assinatura PDF
        try:
            with open(abs_path, "rb") as f:
                header = f.read(1024)
                if b"%PDF-" in header:
                    header_valid = True
                else:
                    issues.append("Assinatura válida de PDF (%PDF-) não encontrada no cabeçalho.")
        except Exception as e:
            issues.append(f"Erro ao ler cabeçalho do arquivo: {e}")

        # Tentar abrir documento via PyMuPDF
        doc = None
        try:
            doc = fitz.open(abs_path)
            is_encrypted = doc.is_encrypted
            is_repaired = getattr(doc, "is_repaired", False)

            if is_encrypted and doc.needs_pass:
                issues.append("Arquivo PDF está criptografado e requer senha.")

            if is_repaired:
                warnings.append("Documento PDF possui estrutura danificada e foi reparado automaticamente ao abrir.")

            total_pages = len(doc)
            if total_pages == 0:
                issues.append("Documento PDF possui 0 páginas.")

            # Testar integridade de cada página
            corrupted_pages = []
            for p_idx in range(total_pages):
                try:
                    page = doc[p_idx]
                    _ = page.rect
                    _ = page.get_images()
                except Exception as p_err:
                    corrupted_pages.append(p_idx + 1)
                    logger.warning(f"Erro de integridade na página {p_idx + 1} de {base_name}: {p_err}")

            if corrupted_pages:
                issues.append(f"Falha de integridade detectada nas páginas: {corrupted_pages}")

        except Exception as doc_err:
            issues.append(f"Falha crítica ao abrir/parsear o arquivo PDF: {doc_err}")
        finally:
            if doc:
                try:
                    doc.close()
                except Exception:
                    pass

        is_complete = len(issues) == 0

        return CompletenessReport(
            file_path=abs_path,
            file_name=base_name,
            file_size_bytes=file_size,
            is_complete=is_complete,
            total_pages=total_pages,
            is_encrypted=is_encrypted,
            is_repaired=is_repaired,
            issues=issues,
            warnings=warnings,
            details={
                "header_valid": header_valid,
            }
        )
