# -*- coding: utf-8 -*-
"""
Model Context Protocol (MCP) Server for PDF-MCP.
Exposes standard MCP tools over Stdio (JSON-RPC 2.0).
Zero external framework dependencies for maximum stability and speed.
"""

import sys
import os
import json
import traceback
from typing import Dict, Any, List

try:
    from .reader import (
        extract_pdf_text,
        get_pdf_metadata,
        search_pdfs,
        compare_pdfs,
    )
    from .writer import build_pdf_document, build_pdf_from_markdown
except (ImportError, ValueError):
    # Fallback when executed directly as script
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


SERVER_INFO = {
    "name": "pdf-toolkit-mcp",
    "version": "1.1.0",
}

PROTOCOL_VERSION = "2024-11-05"

TOOLS_DEFINITIONS = [
    {
        "name": "pdf_read_text",
        "description": "Extract readable text from a PDF file with optional page range boundaries (1-based index).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the PDF file."
                },
                "start_page": {
                    "type": "integer",
                    "description": "First page to extract (1-based, inclusive). Optional."
                },
                "end_page": {
                    "type": "integer",
                    "description": "Last page to extract (1-based, inclusive). Optional."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "pdf_get_metadata",
        "description": "Retrieve technical metadata, total page count, file size, title, and author of a PDF file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the PDF file."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "pdf_search_batch",
        "description": "Search across multiple PDF files in a directory matching a pattern (e.g. '*.pdf', 'L*.pdf') for a keyword or regex.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path containing the PDF files."
                },
                "pattern": {
                    "type": "string",
                    "description": "Filename glob pattern (default: '*.pdf').",
                    "default": "*.pdf"
                },
                "query": {
                    "type": "string",
                    "description": "Keyword or regex to search for in page content."
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether the search should be case sensitive (default: false).",
                    "default": False
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of page matches to return (default: 100).",
                    "default": 100
                }
            },
            "required": ["directory"]
        }
    },
    {
        "name": "pdf_compare_files",
        "description": "Compare two PDF files page by page to detect text differences and page count mismatches.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file1": {
                    "type": "string",
                    "description": "Path to the first PDF file."
                },
                "file2": {
                    "type": "string",
                    "description": "Path to the second PDF file."
                }
            },
            "required": ["file1", "file2"]
        }
    },
    {
        "name": "pdf_generate_report",
        "description": "Generate a publication-grade, styled PDF document from structured JSON data or an external JSON/Markdown file ('input_file') with cover page, headers/footers, Q&A cards, tables, images, callouts, code blocks, and full Turkish Unicode support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "File path where the generated PDF document will be saved."
                },
                "input_file": {
                    "type": "string",
                    "description": "Optional path to a .json or .md file on disk containing the document payload."
                },
                "title": {
                    "type": "string",
                    "description": "Main document title."
                },
                "subtitle": {
                    "type": "string",
                    "description": "Document subtitle or descriptive tagline."
                },
                "category": {
                    "type": "string",
                    "description": "Top-level category banner on cover (e.g. 'DERS RAPORU', 'TEKNİK DOKÜMAN')."
                },
                "description": {
                    "type": "string",
                    "description": "Abstract / description text displayed in the cover card."
                },
                "metadata": {
                    "type": "object",
                    "description": "Key-value metadata pairs displayed on cover (e.g. Author, Date, Course)."
                },
                "theme": {
                    "type": "string",
                    "enum": ["navy_blue", "emerald", "slate"],
                    "description": "Visual color theme for accents, cards, and borders (default: 'navy_blue')."
                },
                "sections": {
                    "type": "array",
                    "description": "List of document sections. Each section has 'title', optional 'subtitle', and an 'items' array with items of type 'qa', 'paragraph', 'bullet', 'code', 'table', 'callout', or 'image'.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "subtitle": {"type": "string"},
                            "items": {"type": "array"}
                        },
                        "required": ["title", "items"]
                    }
                }
            },
            "required": ["output_path"]
        }
    },
    {
        "name": "pdf_from_markdown",
        "description": "Compile a Markdown file (.md) or raw Markdown string directly into a styled, publication-grade PDF report without needing JSON conversion. Supports YAML frontmatter, # sections, ##/### Q&A headers, ```code blocks```, | tables |, > [!NOTE] callouts, ![caption](image) figures, and bullet points.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "File path where the generated PDF document will be saved."
                },
                "markdown_file": {
                    "type": "string",
                    "description": "Path to a Markdown (.md) file to compile. Provide either 'markdown_file' or 'markdown_text'."
                },
                "markdown_text": {
                    "type": "string",
                    "description": "Raw Markdown content string to compile. Provide either 'markdown_file' or 'markdown_text'."
                },
                "title": {
                    "type": "string",
                    "description": "Optional main document title (overrides YAML frontmatter or first # H1)."
                },
                "subtitle": {
                    "type": "string",
                    "description": "Optional subtitle displayed on the cover page."
                },
                "category": {
                    "type": "string",
                    "description": "Category banner on cover (default: 'DOKÜMAN RAPORU')."
                },
                "description": {
                    "type": "string",
                    "description": "Optional overview / abstract displayed in the cover summary box."
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional key-value metadata pairs displayed at the bottom of the cover page."
                },
                "theme": {
                    "type": "string",
                    "enum": ["navy_blue", "emerald", "slate"],
                    "description": "Visual color theme (default: 'navy_blue')."
                }
            },
            "required": ["output_path"]
        }
    }
]


class MCPServer:
    """Standard Model Context Protocol JSON-RPC 2.0 Stdio Server."""

    def __init__(self):
        self.handlers = {
            "initialize": self.handle_initialize,
            "notifications/initialized": self.handle_initialized,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tools_call,
            "ping": self.handle_ping,
        }

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": SERVER_INFO
        }

    def handle_initialized(self, params: Dict[str, Any]) -> None:
        return None

    def handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tools": TOOLS_DEFINITIONS
        }

    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            if tool_name == "pdf_read_text":
                res = extract_pdf_text(
                    file_path=args["file_path"],
                    start_page=args.get("start_page"),
                    end_page=args.get("end_page")
                )
                return {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                    "isError": False
                }

            elif tool_name == "pdf_get_metadata":
                res = get_pdf_metadata(file_path=args["file_path"])
                return {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                    "isError": False
                }

            elif tool_name == "pdf_search_batch":
                res = search_pdfs(
                    directory=args["directory"],
                    pattern=args.get("pattern", "*.pdf"),
                    query=args.get("query", ""),
                    case_sensitive=args.get("case_sensitive", False),
                    max_results=args.get("max_results", 100)
                )
                return {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                    "isError": False
                }

            elif tool_name == "pdf_compare_files":
                res = compare_pdfs(
                    file1=args["file1"],
                    file2=args["file2"]
                )
                return {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                    "isError": False
                }

            elif tool_name == "pdf_generate_report":
                doc_data = {
                    "input_file": args.get("input_file"),
                    "title": args.get("title", ""),
                    "subtitle": args.get("subtitle", ""),
                    "category": args.get("category", ""),
                    "description": args.get("description", ""),
                    "metadata": args.get("metadata", {}),
                    "theme": args.get("theme", "navy_blue"),
                    "sections": args.get("sections", [])
                }
                out_path = build_pdf_document(doc_data, args["output_path"])
                res = {
                    "success": True,
                    "message": "PDF document successfully generated.",
                    "output_path": out_path,
                    "file_size_bytes": os.path.getsize(out_path)
                }
                return {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                    "isError": False
                }

            elif tool_name == "pdf_from_markdown":
                out_path = build_pdf_from_markdown(
                    output_path=args["output_path"],
                    markdown_text=args.get("markdown_text"),
                    markdown_file=args.get("markdown_file"),
                    title=args.get("title"),
                    subtitle=args.get("subtitle", ""),
                    category=args.get("category", "DOKÜMAN RAPORU"),
                    description=args.get("description", ""),
                    metadata=args.get("metadata"),
                    theme=args.get("theme", "navy_blue")
                )
                res = {
                    "success": True,
                    "message": "PDF document successfully compiled from Markdown.",
                    "output_path": out_path,
                    "file_size_bytes": os.path.getsize(out_path)
                }
                return {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                    "isError": False
                }

            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool: '{tool_name}'"}],
                    "isError": True
                }

        except Exception as e:
            err_msg = f"Error executing tool '{tool_name}': {str(e)}\n{traceback.format_exc()}"
            return {
                "content": [{"type": "text", "text": err_msg}],
                "isError": True
            }

    def run(self):
        """Run the JSON-RPC stdio event loop."""
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)
                req_id = request.get("id")
                method = request.get("method")
                params = request.get("params", {})

                if method in self.handlers:
                    result = self.handlers[method](params)
                    if req_id is not None:
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": result
                        }
                        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                        sys.stdout.flush()
                else:
                    if req_id is not None:
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: '{method}'"
                            }
                        }
                        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                        sys.stdout.flush()

            except json.JSONDecodeError:
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON received."
                    }
                }
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"Server exception: {e}\n")
                sys.stderr.flush()


def main():
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()
