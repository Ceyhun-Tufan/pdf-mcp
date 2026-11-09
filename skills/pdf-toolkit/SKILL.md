---
name: pdf-toolkit
description: >-
  Use this skill whenever the user asks to read, inspect, search, compare, or generate
  PDF documents or reports. Provides standard workflows, performance best practices,
  Markdown-to-PDF compilation, and report generation schemas for the pdf-toolkit MCP server.
---

# PDF-Toolkit: Best Practices & Workflow Guide

This skill guides the agent in effectively using the **`pdf-toolkit`** MCP server to analyze, search, and generate publication-quality PDF documents.

---

## 🛠️ Available MCP Tools

1. **`pdf_read_text`**: Extracts formatted text. Use `start_page` and `end_page` to prevent context window bloat on large documents.
2. **`pdf_get_metadata`**: Checks total pages, file size, title, and author before performing heavy operations.
3. **`pdf_search_batch`**: Scans multiple PDFs (e.g. `*.pdf`) for keywords/regex and returns page numbers with snippet previews.
4. **`pdf_compare_files`**: Page-by-page textual comparison of two PDFs.
5. **`pdf_from_markdown`** *(Recommended for Document Generation)*: Compiles a `.md` file (`markdown_file`) or raw Markdown string (`markdown_text`) directly into a publication-grade A4 PDF with cover page, headers/footers, styled Q&A cards, LaTeX block & inline math equations (`$$...$$`, `$x^2$`), shaded code blocks, styled tables, alert callouts, embedded images, and full Turkish/Unicode support. **Never write intermediate Python scripts to dump JSON when you can write or pass Markdown directly!**
6. **`pdf_generate_report`**: Generates a PDF document from structured JSON data or an external file path (`input_file`). Supports item types: `qa`, `paragraph`, `bullet`, `code`, `math`, `table`, `callout`, and `image`.

---

## 🚀 Recommended Workflows

### 1. Generating a PDF from Markdown (Fastest & Cleanest Workflow)
Write a `.md` file or pass `markdown_text` directly to `pdf_from_markdown`:

```markdown
---
title: CLOUD ARCHITECTURE AUDIT
subtitle: Security & Performance Review
category: TECHNICAL REPORT
description: Comprehensive overview of distributed services and latency metrics.
theme: navy_blue
Author: Engineering Team
Date: 2026
---

# SECTION 1: CORE ARCHITECTURE

## Question 1.1: How does caching improve API throughput?
Edge caching reduces database load by serving frequently requested payloads directly from memory.

> [!TIP] Performance Tip
> Enable connection pooling before scaling worker instances.

- **Gateway Layer:** Handles authentication and rate limiting.
- **Service Mesh:** Manages internal service-to-service communication.

```sql
SELECT service_id, AVG(response_ms) FROM metrics GROUP BY service_id;
```

| Service ID | Component | SLA |
| :--- | :--- | :--- |
| SVC-01 | Auth Gateway | 99.99% |

![System Diagram](assets/diagram.png)
```

Then call `pdf_from_markdown`:
```json
{
  "output_path": "C:/path/to/Output_Report.pdf",
  "markdown_file": "C:/path/to/draft.md"
}
```

### 2. Generating a Styled PDF via Structured JSON (`pdf_generate_report`)
Supported item types inside `sections[].items`:
- `qa`: `{"type": "qa", "q_num": "1.1", "question": "...", "answer": "..."}`
- `paragraph`: `{"type": "paragraph", "bold_prefix": "Note:", "text": "..."}`
- `bullet`: `{"type": "bullet", "title": "Title", "text": "..."}`
- `code`: `{"type": "code", "code": "SELECT 1;"}`
- `math`: `{"type": "math", "equation": "\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}", "caption": "Gaussian Integral", "label": "1.1"}`
- `table`: `{"type": "table", "headers": ["A", "B"], "rows": [["1", "2"]]}`
- `callout`: `{"type": "callout", "kind": "note|tip|warning|important|caution", "title": "...", "text": "..."}`
- `image`: `{"type": "image", "image_path": "C:/path/to/img.png", "caption": "Figure 1"}`

You can also pass `"input_file": "C:/path/to/payload.json"` to avoid serializing huge JSON payloads in tool arguments.

### Supported Themes:
- `navy_blue` (Default): Deep navy blue with clean modern blue accents.
- `emerald`: Forest green with emerald accents.
- `slate`: Minimalist charcoal and slate grey.

---

## ⚠️ Best Practices & Edge Cases
- **Avoid Context Overload:** Never read more than 20-30 pages of raw text in a single tool call unless explicitly required.
- **Prefer Markdown Compilation:** For long reports, write a `.md` file using `write_file` and compile it with `pdf_from_markdown(markdown_file=..., output_path=...)` in a single step.
- **Turkish Characters:** The generator handles `ç, ğ, ı, ö, ş, ü, İ, Ğ, Ş` automatically via TrueType fonts (`Arial`, `Consolas`).
