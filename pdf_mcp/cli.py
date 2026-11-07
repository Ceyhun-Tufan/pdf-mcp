# -*- coding: utf-8 -*-
"""
Command Line Interface (CLI) for PDF-MCP Toolkit.
Allows direct terminal execution for reading, searching, diffing, compiling Markdown/JSON to PDF, and starting the MCP server.
"""

import sys
import os
import argparse
import json
try:
    from .reader import (
        extract_pdf_text,
        get_pdf_metadata,
        search_pdfs,
        compare_pdfs,
    )
    from .writer import build_pdf_document, build_pdf_from_markdown
    from .server import MCPServer
except (ImportError, ValueError):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(cur_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from pdf_mcp.reader import (
        extract_pdf_text,
        get_pdf_metadata,
        search_pdfs,
        compare_pdfs,
    )
    from pdf_mcp.writer import build_pdf_document, build_pdf_from_markdown
    from pdf_mcp.server import MCPServer


def main():
    parser = argparse.ArgumentParser(
        prog="pdf-mcp",
        description="PDF-MCP: CLI Toolkit and MCP Server for PDF operations."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: read
    p_read = subparsers.add_parser("read", help="Extract text from a PDF file")
    p_read.add_argument("file", help="Path to PDF file")
    p_read.add_argument("--start", type=int, default=None, help="Start page (1-based)")
    p_read.add_argument("--end", type=int, default=None, help="End page (1-based)")
    p_read.add_argument("--json", action="store_true", help="Output results as JSON")

    # Command: meta
    p_meta = subparsers.add_parser("meta", help="Show technical metadata of a PDF file")
    p_meta.add_argument("file", help="Path to PDF file")

    # Command: search
    p_search = subparsers.add_parser("search", help="Search multiple PDFs for keywords or regex")
    p_search.add_argument("dir", help="Directory path to search")
    p_search.add_argument("--pattern", default="*.pdf", help="Glob pattern (default: *.pdf)")
    p_search.add_argument("--query", "-q", default="", help="Query or keyword to search")
    p_search.add_argument("--case-sensitive", action="store_true", help="Case-sensitive search")
    p_search.add_argument("--limit", type=int, default=100, help="Max results limit")

    # Command: diff
    p_diff = subparsers.add_parser("diff", help="Compare two PDF files page by page")
    p_diff.add_argument("file1", help="First PDF file")
    p_diff.add_argument("file2", help="Second PDF file")

    # Command: from-md
    p_md = subparsers.add_parser("from-md", help="Compile a Markdown (.md) file into a styled PDF report")
    p_md.add_argument("input_md", help="Path to input Markdown (.md) file")
    p_md.add_argument("output_pdf", help="Path to output PDF file")
    p_md.add_argument("--title", default=None, help="Override document title")
    p_md.add_argument("--subtitle", default="", help="Document subtitle")
    p_md.add_argument("--category", default="DOKÜMAN RAPORU", help="Cover category banner")
    p_md.add_argument("--theme", default="navy_blue", choices=["navy_blue", "emerald", "slate"], help="Color theme")

    # Command: generate
    p_gen = subparsers.add_parser("generate", help="Generate a PDF report from a JSON payload file")
    p_gen.add_argument("input_json", help="Path to input JSON file")
    p_gen.add_argument("output_pdf", help="Path to output PDF file")

    # Command: server (MCP)
    subparsers.add_parser("server", help="Start the MCP Server on Stdio")

    args = parser.parse_args()

    if not args.command or args.command == "server":
        server = MCPServer()
        server.run()
        return

    if args.command == "read":
        res = extract_pdf_text(args.file, args.start, args.end)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"=== {res['file_name']} (Pages {res['start_page']}-{res['end_page']}/{res['total_pages']}) ===\n")
            print(res["full_text"])

    elif args.command == "meta":
        res = get_pdf_metadata(args.file)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "search":
        res = search_pdfs(
            directory=args.dir,
            pattern=args.pattern,
            query=args.query,
            case_sensitive=args.case_sensitive,
            max_results=args.limit
        )
        print(f"Scanned {res['scanned_files_count']} files, found {res['pages_with_matches']} pages matching '{args.query}':\n")
        for m in res["matches"]:
            print(f"[{m['file_name']}] Page {m['page_number']}: {m['preview']}")

    elif args.command == "diff":
        res = compare_pdfs(args.file1, args.file2)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "from-md":
        out = build_pdf_from_markdown(
            output_path=args.output_pdf,
            markdown_file=args.input_md,
            title=args.title,
            subtitle=args.subtitle,
            category=args.category,
            theme=args.theme
        )
        print(f"Successfully compiled Markdown to PDF: {out}")

    elif args.command == "generate":
        out = build_pdf_document({"input_file": args.input_json}, args.output_pdf)
        print(f"Successfully generated PDF from JSON: {out}")


if __name__ == "__main__":
    main()
