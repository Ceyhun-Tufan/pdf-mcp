"""
PDF-MCP: Model Context Protocol (MCP) Server and CLI Toolkit for PDF Operations.
Provides high-performance PDF reading, batch searching, comparison, and publication-quality styled PDF report generation.
"""

__version__ = "1.1.0"
__author__ = "Ceyhun"
__license__ = "MIT"

from .reader import (
    extract_pdf_text,
    get_pdf_metadata,
    search_pdfs,
    compare_pdfs,
)
from .writer import (
    PDFReportBuilder,
    build_pdf_document,
    build_pdf_from_markdown,
    parse_markdown_to_doc_data,
)

__all__ = [
    "extract_pdf_text",
    "get_pdf_metadata",
    "search_pdfs",
    "compare_pdfs",
    "PDFReportBuilder",
    "build_pdf_document",
    "build_pdf_from_markdown",
    "parse_markdown_to_doc_data",
]
