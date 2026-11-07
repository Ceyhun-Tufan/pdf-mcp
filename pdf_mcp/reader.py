# -*- coding: utf-8 -*-
"""
PDF Reader, Searcher, and Metadata Extractor module.
Uses pypdf for robust cross-platform text extraction and analysis.
"""

import os
import glob
import re
from typing import Dict, List, Any, Optional
from pypdf import PdfReader


def get_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract technical and document metadata from a PDF file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    meta = reader.metadata or {}
    return {
        "file_name": os.path.basename(file_path),
        "file_path": os.path.abspath(file_path),
        "file_size_bytes": file_size,
        "file_size_kb": round(file_size / 1024, 2),
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "total_pages": total_pages,
        "title": meta.title if meta.title else None,
        "author": meta.author if meta.author else None,
        "creator": meta.creator if meta.creator else None,
        "producer": meta.producer if meta.producer else None,
        "is_encrypted": reader.is_encrypted,
    }


def extract_pdf_text(
    file_path: str,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extract text from a PDF file across specified page boundaries.
    Pages are 1-based (start_page=1 is the first page).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    if total_pages == 0:
        return {
            "file_name": os.path.basename(file_path),
            "total_pages": 0,
            "pages": [],
            "full_text": ""
        }

    s_idx = max(0, (start_page - 1) if start_page else 0)
    e_idx = min(total_pages, end_page if end_page else total_pages)

    extracted_pages = []
    full_text_parts = []

    for idx in range(s_idx, e_idx):
        try:
            page = reader.pages[idx]
            page_text = page.extract_text() or ""
        except Exception as e:
            page_text = f"[Error extracting text from page {idx+1}: {e}]"

        extracted_pages.append({
            "page_number": idx + 1,
            "char_count": len(page_text),
            "text": page_text
        })
        full_text_parts.append(f"--- Sayfa {idx+1} ---\n{page_text}")

    return {
        "file_name": os.path.basename(file_path),
        "file_path": os.path.abspath(file_path),
        "total_pages": total_pages,
        "extracted_page_count": len(extracted_pages),
        "start_page": s_idx + 1,
        "end_page": e_idx,
        "pages": extracted_pages,
        "full_text": "\n\n".join(full_text_parts)
    }


def search_pdfs(
    directory: str,
    pattern: str = "*.pdf",
    query: str = "",
    case_sensitive: bool = False,
    max_results: int = 200
) -> Dict[str, Any]:
    """
    Search across multiple PDF files in a directory matching a glob pattern
    for a keyword or regular expression.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Directory not found: {directory}")

    search_path = os.path.join(directory, pattern)
    matched_files = sorted(glob.glob(search_path))

    if not query:
        # Just return list of matched PDF files and their page counts
        file_list = []
        for f in matched_files:
            try:
                reader = PdfReader(f)
                file_list.append({"file": os.path.basename(f), "path": f, "pages": len(reader.pages)})
            except Exception:
                file_list.append({"file": os.path.basename(f), "path": f, "pages": None})
        return {
            "directory": os.path.abspath(directory),
            "pattern": pattern,
            "matched_files_count": len(matched_files),
            "files": file_list
        }

    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(re.escape(query) if not query.startswith("regex:") else query[6:], flags)

    results = []
    total_matches = 0

    for fpath in matched_files:
        try:
            reader = PdfReader(fpath)
            fname = os.path.basename(fpath)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if regex.search(text):
                    matching_lines = [
                        line.strip() for line in text.splitlines()
                        if regex.search(line)
                    ]
                    results.append({
                        "file_name": fname,
                        "file_path": os.path.abspath(fpath),
                        "page_number": page_idx + 1,
                        "match_count_on_page": len(matching_lines),
                        "matching_lines": matching_lines[:5],
                        "preview": " | ".join(matching_lines[:3])[:250]
                    })
                    total_matches += len(matching_lines)
                    if len(results) >= max_results:
                        break
        except Exception as e:
            results.append({
                "file_name": os.path.basename(fpath),
                "file_path": os.path.abspath(fpath),
                "error": str(e)
            })

        if len(results) >= max_results:
            break

    return {
        "directory": os.path.abspath(directory),
        "pattern": pattern,
        "query": query,
        "scanned_files_count": len(matched_files),
        "pages_with_matches": len(results),
        "total_matching_lines": total_matches,
        "matches": results
    }


def compare_pdfs(file1: str, file2: str) -> Dict[str, Any]:
    """
    Compare two PDF files page by page to find differences in text content.
    """
    for f in [file1, file2]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"File not found: {f}")

    r1 = PdfReader(file1)
    r2 = PdfReader(file2)

    len1 = len(r1.pages)
    len2 = len(r2.pages)

    max_pages = max(len1, len2)
    diffs = []

    for p in range(max_pages):
        t1 = r1.pages[p].extract_text() if p < len1 else None
        t2 = r2.pages[p].extract_text() if p < len2 else None

        if t1 != t2:
            diffs.append({
                "page_number": p + 1,
                "in_file1": t1 is not None,
                "in_file2": t2 is not None,
                "file1_char_count": len(t1) if t1 else 0,
                "file2_char_count": len(t2) if t2 else 0,
                "file1_snippet": (t1[:120].strip() if t1 else "[PAGE MISSING]"),
                "file2_snippet": (t2[:120].strip() if t2 else "[PAGE MISSING]"),
            })

    return {
        "file1": os.path.basename(file1),
        "file2": os.path.basename(file2),
        "file1_pages": len1,
        "file2_pages": len2,
        "is_identical": len(diffs) == 0 and len1 == len2,
        "differing_pages_count": len(diffs),
        "differences": diffs
    }
