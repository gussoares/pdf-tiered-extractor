# PDF Tiered Extractor (`pdf-tiered-extractor`)

Biblioteca Python e ferramenta CLI para extração progressiva/em cascata (*waterfall*) de conteúdo de documentos PDF em formatos **Texto (.txt)**, **Markdown (.md)** e **JSON (.json)**, com suporte a **Validação de Completitude do Processo** e **OCR Híbrido em Imagens**.

## 🚀 Como Funciona

A biblioteca analisa cada página do documento PDF individualmente e seleciona o motor de extração mais adequado com base na complexidade visual e estrutural do conteúdo:

1. **Validador de Completitude (`DocumentValidator`)**:
   - Analisa previamente o arquivo PDF para detectar se está completo, se o cabeçalho é válido, se possui 0 bytes ou se contém páginas com corrupção de estrutura.
2. **Tier 1 (Ultrarrápido - PyMuPDF / pymupdf4llm)**:
   - Para páginas com texto digital nativo e formatação padrão.
   - Execução em milissegundos (<10ms por página).
3. **Tier 2 (Estruturado - IBM Docling / Layout AI)**:
   - Para páginas com múltiplos fluxos de texto, gráficos vetoriais ou tabelas complexas.
   - Preserva hierarquia de títulos e tabelas estruturadas.
4. **Tier 3 (OCR multiestágio / Visão e Fallback de Imagens)**:
   - Para páginas escaneadas/digitalizadas sem camada de texto nativo.
   - Executa uma cadeia resiliente de OCR (PyMuPDF OCR -> Pytesseract Pixmap -> OCR em Imagens Embutidas -> Scan Detector).
   - O OCR em imagens isoladas atua como fallback robusto para PDFs com recortes e figuras.

---

## 🛠️ Instalação

```bash
# Instalação básica (Tier 1 PyMuPDF)
pip install -e .

# Instalação com suporte completo a Tier 2 (Docling)
pip install -e .[docling]
```

---

## 💻 Uso via Linha de Comando (CLI)

```bash
# Extrair em formato Markdown (padrão) com verificação automática de integridade
pdf-extract process documento.pdf

# Ativar modo estrito (falhar se PDF estiver corrompido ou incompleto)
pdf-extract process documento.pdf --strict-verify

# Extrair em JSON AST com metadados por bloco
pdf-extract process documento.pdf --format json

# Limitar o processamento máximo até o Tier 2 (impede a execução de OCR pesado do Tier 3)
pdf-extract process documento.pdf --max-tier 2

# Exportar em todos os formatos (txt, md, json) salvando em diretório específico
pdf-extract process documento.pdf --format all --output-dir ./saida
```

---

## 🐍 Uso via Código Python

```python
from pdf_tiered_extractor import TieredPDFExtractor, ExtractionConfig, DocumentValidator

# 1. Validar completitude do documento previamente (opcional)
report = DocumentValidator.validate_pdf("exemplo.pdf")
print(f"Status da integridade: {report.is_complete} (Problemas: {report.issues})")

# 2. Inicializar extrator com verificação automática, limite de tier e OCR híbrido em imagens
config = ExtractionConfig(
    max_tier=3, # Define o teto máximo de processamento (1, 2 ou 3)
    verify_completeness=True,
    extract_image_text_on_demand=True
)
extractor = TieredPDFExtractor(config=config)

# Processar arquivo PDF
result = extractor.process_pdf("exemplo.pdf")

print(f"Páginas: {result.total_pages}")
print(f"Distribuição de Tiers: {result.tier_distribution}")

# Exportar em diferentes formatos
texto_puro = result.to_text()
markdown = result.to_markdown()
json_ast = result.to_json()
```

---

## 📄 Licença

MIT License
