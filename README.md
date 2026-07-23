# PDF Tiered Extractor (`pdf-tiered-extractor`)

Biblioteca Python e ferramenta CLI para extração progressiva/em cascata (*waterfall*) de conteúdo de documentos PDF em formatos **Texto (.txt)**, **Markdown (.md)** e **JSON (.json)**.

## 🚀 Como Funciona

A biblioteca analisa cada página do documento PDF individualmente e seleciona o motor de extração mais adequado com base na complexidade visual e estrutural do conteúdo:

1. **Tier 1 (Ultrarrápido - PyMuPDF / pymupdf4llm)**:
   - Para páginas com texto digital nativo e formatação padrão.
   - Execução em milissegundos (<10ms por página).
2. **Tier 2 (Estruturado - IBM Docling / Layout AI)**:
   - Para páginas com múltiplos fluxos de texto, gráficos vetoriais ou tabelas complexas.
   - Preserva hierarquia de títulos e tabelas estruturadas.
3. **Tier 3 (OCR / Digitalizados)**:
   - Para páginas escaneadas/digitalizadas sem camada de texto nativo.
   - Executa rotinas de OCR (Tesseract / PyMuPDF OCR).

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
# Extrair em formato Markdown (padrão)
pdf-extract process documento.pdf

# Extrair em JSON AST com metadados por bloco
pdf-extract process documento.pdf --format json

# Exportar em todos os formatos (txt, md, json) salvando em diretório específico
pdf-extract process documento.pdf --format all --output-dir ./saida

# Forçar uso do Tier 1 para todas as páginas
pdf-extract process documento.pdf --tier 1
```

---

## 🐍 Uso via Código Python

```python
from pdf_tiered_extractor import TieredPDFExtractor, ExtractionConfig

# Inicializar extrator com configuração padrão (decisão automática por página)
extractor = TieredPDFExtractor()

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
