# Feature Specification: PDF Tiered Extractor (`pdf-tiered-extractor`)

**Feature Branch**: `001-pdf-tiered-extractor`  
**Created**: 2026-07-22  
**Status**: Approved  
**Input**: Biblioteca de extração em cascata para documentos PDF (TXT, Markdown, JSON AST)

## User Scenarios & Testing

### User Story 1 - Extração em Cascata Baseada em Complexidade (Priority: P1)

Como desenvolvedor ou analista jurídico, quero processar arquivos PDF de forma que páginas simples sejam extraídas em milissegundos via PyMuPDF e páginas complexas (tabelas, imagens, escaneadas) sejam roteadas para motores mais avançados (Docling/OCR), minimizando tempo de execução e consumo computacional.

**Why this priority**: É a essência da biblioteca: balancear velocidade, fidelidade e custo no processamento de PDFs.

**Independent Test**: Pode ser testado executando o `TieredPDFExtractor` em um PDF de 3 páginas (página 1: texto simples; página 2: gráfico/vetores; página 3: imagem escaneada) e verificando que cada página utiliza o Tier correto.

**Acceptance Scenarios**:
1. **Given** um PDF com texto nativo limpo, **When** processado pela biblioteca, **Then** o Tier 1 (PyMuPDF) é utilizado para todas as páginas com velocidade < 50ms/página.
2. **Given** um PDF digitalizado/escaneado sem camada de texto, **When** analisado pelo `PageComplexityAnalyzer`, **Then** a flag `is_scanned=True` é ativada e a página é roteada para o Tier 3 (OCR).

---

### User Story 2 - Formatação Multiformato (TXT, MD, JSON AST) (Priority: P2)

Como usuário da biblioteca, quero obter a saída nos formatos Texto Puro (`.txt`), Markdown Estruturado (`.md`) com tabelas e frontmatter YAML, ou JSON AST contendo metadados completos por bloco e página.

**Why this priority**: Permite alimentar diferentes etapas do sistema (RAG, banco vetorial, visualização, armazenamento).

**Independent Test**: Passar um objeto `ExtractionResult` pelos formatadores `text_formatter`, `markdown_formatter` e `json_formatter` e validar a estrutura e integridade do conteúdo retornado.

---

### User Story 3 - CLI e Modulardade sem Dependência Rígida (Priority: P3)

Como administrador ou usuário final, quero executar `pdf-extract` via linha de comando e ter a garantia de que a biblioteca funciona com instalação básica (PyMuPDF), oferecendo mensagens claras se bibliotecas opcionais de Tier 2/3 (como `docling`) não estiverem instaladas.

**Why this priority**: Garante resiliência e facilidade de instalação em qualquer ambiente sem quebrar o pipeline.

---

## Functional Requirements

- **FR-001**: O sistema DEVE analisar cada página de um PDF individualmente calculando um score de complexidade (`PageComplexityReport`).
- **FR-002**: O sistema DEVE detectar cobertura de imagens raster (`xref`), quantidade de elementos vetoriais (`drawings`), densidade de caracteres e tabelas.
- **FR-003**: O sistema DEVE executar o Tier 1 (PyMuPDF / PyMuPDF4LLM) para extração nativa direta.
- **FR-004**: O sistema DEVE disparar o Tier 2 (Docling) se instalado e a página contiver gráficos ou tabelas complexas.
- **FR-005**: O sistema DEVE disparar o Tier 3 (OCR) quando a densidade de texto for inferior a um limite configurável.
- **FR-006**: O sistema DEVE exportar o resultado final nos formatos TXT, Markdown e JSON AST.

## Success Criteria

- **SC-001**: Processamento de PDFs de texto nativo em menos de 100ms por página no Tier 1.
- **SC-002**: 100% de cobertura nos testes unitários dos módulos de análise e formatação.
- **SC-003**: Fallback transparente e sem exceções não tratadas quando pacotes opcionais não estiverem instalados.
