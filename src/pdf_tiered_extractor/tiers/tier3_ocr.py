import io
import fitz
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Tier3OCRExtractor:
    """
    Extrator Tier 3 (OCR / Visão para Páginas Escaneadas e Imagens).
    Utiliza PyMuPDF OCR (get_textpage_ocr / Tesseract) e/ou pytesseract em pixmaps para extração em imagens.
    """

    def __init__(self, language: str = "por+eng"):
        self.language = language
        self._has_pytesseract = False
        try:
            import pytesseract
            from PIL import Image
            self._has_pytesseract = True
        except ImportError:
            self._has_pytesseract = False

    def extract_images_from_page(self, page: fitz.Page) -> List[str]:
        """
        Extrai texto especificamente de cada imagem embutida na página via OCR/Pixmap.
        """
        extracted_texts = []
        images = page.get_images() or []

        for idx, img_info in enumerate(images):
            xref = img_info[0]
            try:
                base_image = page.parent.extract_image(xref)
                if not base_image:
                    continue
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                if self._has_pytesseract:
                    import pytesseract
                    from PIL import Image
                    image_obj = Image.open(io.BytesIO(image_bytes))
                    txt = pytesseract.image_to_string(image_obj, lang=self.language.replace("+", "+"))
                    if txt.strip():
                        extracted_texts.append(f"[TEXTO EXTRAÍDO DA IMAGEM {idx+1} (xref {xref})]:\n{txt.strip()}")
            except Exception as e:
                logger.debug(f"Falha ao executar OCR embutido na imagem xref {xref}: {e}")

        return extracted_texts

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
            logger.debug(f"PyMuPDF OCR não disponível para página {page_num}: {e}. Tentando extrações secundárias.")

            # Tentativa via pytesseract no pixmap da página
            if self._has_pytesseract:
                try:
                    import pytesseract
                    from PIL import Image
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang=self.language.replace("+", "+")) or ""
                    if ocr_text.strip():
                        engine = "Pytesseract (Pixmap Page OCR)"
                except Exception as py_err:
                    logger.debug(f"Falha no pytesseract pixmap página {page_num}: {py_err}")

            if not ocr_text.strip():
                # Tentar extrair de imagens embutidas individualmente
                img_texts = self.extract_images_from_page(page)
                if img_texts:
                    ocr_text = "\n\n".join(img_texts)
                    engine = "Embedded Image Extractor (Pytesseract)"

            if not ocr_text.strip():
                raw_text = page.get_text("text") or ""
                if raw_text.strip():
                    ocr_text = raw_text
                    engine = "PyMuPDF Direct (Fallback - Tesseract não configurado)"
                else:
                    ocr_text = f"[PÁGINA DIGITALIZADA / SCAN - PÁGINA {page_num + 1}]"
                    engine = "Scan Detector (OCR indisponível)"

        return {
            "tier_used": 3,
            "text": ocr_text.strip(),
            "markdown": ocr_text.strip(),
            "blocks": [],
            "tables": [],
            "engine": engine
        }
