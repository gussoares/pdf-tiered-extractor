import os
import sys
import click
import logging
from .core.pipeline import TieredPDFExtractor, ExtractionConfig

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@click.group()
def cli():
    """CLI para extração progressiva/em cascata de PDFs (pdf-tiered-extractor)."""
    pass

@cli.command(name="process")
@click.argument("pdf_path", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--format", "-f", "output_format", type=click.Choice(["txt", "md", "json", "all"]), default="md", help="Formato de saída desejado.")
@click.option("--output-dir", "-o", type=click.Path(file_okay=False, dir_okay=True), default=None, help="Diretório para salvar os arquivos gerados.")
@click.option("--tier", "-t", type=int, default=None, help="Forçar uso de um Tier específico (1: PyMuPDF, 2: Docling, 3: OCR).")
@click.option("--max-tier", type=click.IntRange(1, 3), default=3, help="Teto máximo de Tier permitido (1: PyMuPDF apenas, 2: até Docling, 3: até OCR).")
@click.option("--max-pages", "-m", type=int, default=None, help="Número máximo de páginas a processar.")
@click.option("--verify/--no-verify", default=True, help="Executar validação de completitude/integridade do PDF.")
@click.option("--strict-verify", is_flag=True, help="Interromper execução caso ocorra falha na validação de completitude.")
@click.option("--image-ocr/--no-image-ocr", default=True, help="Ativar busca garantida de texto em imagens se a página for vazia ou tiver imagens.")
@click.option("--verbose", "-v", is_flag=True, help="Exibir informações detalhadas durante o processamento.")
def process(pdf_path: str, output_format: str, output_dir: str, tier: int, max_tier: int, max_pages: int, verify: bool, strict_verify: bool, image_ocr: bool, verbose: bool):
    """Processa um arquivo PDF aplicando o pipeline em cascata por página."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    click.echo(f"[+] Iniciando extracao de: {pdf_path}")
    config = ExtractionConfig(
        max_tier=max_tier,
        forced_tier=tier,
        max_pages=max_pages,
        verify_completeness=verify,
        strict_completeness=strict_verify,
        extract_image_text_on_demand=image_ocr
    )
    extractor = TieredPDFExtractor(config=config)

    try:
        result = extractor.process_pdf(pdf_path)
    except Exception as e:
        click.echo(f"[ERROR] Erro no processamento: {e}", err=True)
        sys.exit(1)

    if result.completeness:
        status_str = "COMPLETO" if result.completeness.is_complete else "ALERTA/INCOMPLETO"
        click.echo(f"[+] Integridade do PDF: {status_str} ({result.completeness.file_size_bytes} bytes, {result.completeness.total_pages} paginas).")
        if result.completeness.issues:
            for issue in result.completeness.issues:
                click.echo(f"    [!] Problema: {issue}", err=True)

    click.echo(f"[+] Concluido em {result.elapsed_seconds:.3f}s ({result.total_pages} paginas).")
    click.echo(f"[+] Distribuição de Tiers: Tier 1={result.tier_distribution['tier1']} | Tier 2={result.tier_distribution['tier2']} | Tier 3={result.tier_distribution['tier3']}")

    # Definir pasta de saída
    target_dir = output_dir or os.path.dirname(os.path.abspath(pdf_path)) or "."
    os.makedirs(target_dir, exist_ok=True)
    base_name = os.path.splitext(result.file_name)[0]

    formats_to_generate = ["txt", "md", "json"] if output_format == "all" else [output_format]

    for fmt in formats_to_generate:
        out_file = os.path.join(target_dir, f"{base_name}.{fmt}")
        if fmt == "txt":
            content = result.to_text()
        elif fmt == "md":
            content = result.to_markdown()
        else:
            content = result.to_json()

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"[OK] Arquivo gerado: {out_file}")

if __name__ == "__main__":
    cli()
