# -*- coding: utf-8 -*-
"""
PDF Report Generator, Markdown-to-PDF Compiler, and Styled Document Builder module.
Uses fpdf2 to build publication-grade, beautifully formatted PDF documents
with full Unicode / Turkish character support, responsive headers/footers,
question-and-answer cards, code blocks, styled tables, images, callouts,
bullet points, and cover pages.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None


THEMES = {
    "navy_blue": {
        "primary": (24, 43, 73),
        "accent": (41, 128, 185),
        "card_bg": (238, 244, 251),
        "card_border": (180, 205, 235),
        "code_bg": (245, 247, 250),
        "code_border": (210, 218, 228),
        "text_dark": (20, 35, 60),
        "text_body": (40, 45, 55),
    },
    "emerald": {
        "primary": (20, 80, 50),
        "accent": (39, 174, 96),
        "card_bg": (235, 248, 240),
        "card_border": (170, 220, 190),
        "code_bg": (246, 250, 247),
        "code_border": (210, 230, 220),
        "text_dark": (15, 60, 40),
        "text_body": (40, 45, 55),
    },
    "slate": {
        "primary": (45, 55, 72),
        "accent": (74, 85, 104),
        "card_bg": (240, 243, 246),
        "card_border": (200, 208, 218),
        "code_bg": (247, 248, 250),
        "code_border": (220, 224, 230),
        "text_dark": (26, 32, 44),
        "text_body": (45, 50, 60),
    }
}

CALLOUT_STYLES = {
    "note": {
        "accent": (41, 128, 185),
        "bg": (238, 246, 253),
        "border": (185, 215, 242),
        "default_title": "NOT / BİLGİ",
    },
    "info": {
        "accent": (41, 128, 185),
        "bg": (238, 246, 253),
        "border": (185, 215, 242),
        "default_title": "BİLGİ",
    },
    "tip": {
        "accent": (39, 174, 96),
        "bg": (236, 250, 242),
        "border": (175, 228, 198),
        "default_title": "İPUCU",
    },
    "warning": {
        "accent": (230, 126, 34),
        "bg": (254, 247, 236),
        "border": (245, 210, 165),
        "default_title": "UYARI / DİKKAT",
    },
    "important": {
        "accent": (142, 68, 173),
        "bg": (246, 238, 250),
        "border": (212, 185, 228),
        "default_title": "ÖNEMLİ",
    },
    "caution": {
        "accent": (192, 57, 43),
        "bg": (253, 238, 237),
        "border": (238, 185, 180),
        "default_title": "KRİTİK UYARI",
    },
}


class PDFReportBuilder(FPDF):
    """
    Extensible PDF Document Builder with high-aesthetic styling,
    safe font fallback, and complete UTF-8 support.
    """

    def __init__(self, header_title: str = "Doküman Raporu", theme_name: str = "navy_blue"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(18, 20, 18)
        self.set_auto_page_break(auto=True, margin=20)
        self.header_title = header_title
        self.theme = THEMES.get(theme_name, THEMES["navy_blue"])
        self.is_cover = True

        self._setup_fonts()

    def _setup_fonts(self):
        """Register TrueType Unicode fonts for cross-platform and Turkish support."""
        font_candidates = [
            (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\ariali.ttf"),
            (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf", r"C:\Windows\Fonts\calibrii.ttf"),
            (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeuii.ttf"),
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
        ]

        registered = False
        for reg, bold, italic in font_candidates:
            if os.path.exists(reg) and os.path.exists(bold):
                self.add_font("CustomSans", "", reg)
                self.add_font("CustomSans", "B", bold)
                if os.path.exists(italic):
                    self.add_font("CustomSans", "I", italic)
                else:
                    self.add_font("CustomSans", "I", reg)
                self.font_sans = "CustomSans"
                registered = True
                break

        if not registered:
            self.font_sans = "Helvetica"

        mono_candidates = [
            r"C:\Windows\Fonts\consola.ttf",
            r"C:\Windows\Fonts\cour.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
        registered_mono = False
        for mono in mono_candidates:
            if os.path.exists(mono):
                self.add_font("CustomMono", "", mono)
                self.font_mono = "CustomMono"
                registered_mono = True
                break

        if not registered_mono:
            self.font_mono = "Courier"

    def header(self):
        if self.is_cover:
            return
        self.set_font(self.font_sans, "I", 8)
        self.set_text_color(115, 125, 140)
        self.cell(0, 6, self.header_title, border=0, align="L")
        self.set_draw_color(215, 220, 230)
        self.set_line_width(0.3)
        self.line(18, 27, 192, 27)
        self.ln(4)

    def footer(self):
        if self.is_cover:
            return
        self.set_y(-15)
        self.set_draw_color(220, 225, 230)
        self.set_line_width(0.3)
        self.line(18, 282, 192, 282)
        self.set_font(self.font_sans, "", 8)
        self.set_text_color(125, 135, 150)
        self.cell(0, 8, "PDF-MCP Toolkit", align="L")
        self.set_font(self.font_sans, "B", 8)
        self.cell(0, 8, f"Sayfa {self.page_no()} / {{nb}}", align="R")

    def check_page_break(self, height: float):
        if self.get_y() + height > 275:
            self.add_page()

    def draw_cover(
        self,
        title: str,
        subtitle: str = "",
        category: str = "",
        description: str = "",
        metadata: Optional[Dict[str, str]] = None
    ):
        """Draw a sleek, publication-grade cover page."""
        self.is_cover = True
        self.add_page()

        p_r, p_g, p_b = self.theme["primary"]
        a_r, a_g, a_b = self.theme["accent"]

        self.set_fill_color(p_r, p_g, p_b)
        self.rect(0, 0, 10, 297, "F")
        self.set_fill_color(a_r, a_g, a_b)
        self.rect(10, 0, 3, 297, "F")

        self.set_left_margin(24)
        self.set_y(35)

        if category:
            self.set_font(self.font_sans, "B", 11)
            self.set_text_color(a_r, a_g, a_b)
            self.cell(0, 6, category.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(3)

        self.set_font(self.font_sans, "B", 22)
        td_r, td_g, td_b = self.theme["text_dark"]
        self.set_text_color(td_r, td_g, td_b)
        self.multi_cell(0, 10, title)

        if subtitle:
            self.ln(4)
            self.set_font(self.font_sans, "B", 12)
            self.set_text_color(90, 105, 120)
            self.cell(0, 7, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(5)
        self.set_draw_color(a_r, a_g, a_b)
        self.set_line_width(1.0)
        self.line(24, self.get_y(), 188, self.get_y())
        self.ln(10)

        if description:
            c_bg_r, c_bg_g, c_bg_b = self.theme["card_bg"]
            c_b_r, c_b_g, c_b_b = self.theme["card_border"]
            self.set_fill_color(c_bg_r, c_bg_g, c_bg_b)
            self.set_draw_color(c_b_r, c_b_g, c_b_b)
            self.set_line_width(0.35)

            desc_lines = len(description.split("\n")) + int(len(description) / 75)
            box_h = max(25, desc_lines * 5.2 + 8)

            cur_y = self.get_y()
            self.rect(24, cur_y, 164, box_h, "DF")

            self.set_xy(28, cur_y + 4)
            self.set_font(self.font_sans, "B", 9.5)
            self.set_text_color(p_r, p_g, p_b)
            self.cell(0, 5.5, "GENEL BİLGİ VE ÖZET:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_x(28)
            self.set_font(self.font_sans, "", 9)
            self.set_text_color(50, 60, 75)
            self.multi_cell(156, 4.8, description)
            self.set_y(cur_y + box_h + 8)

        if metadata:
            self.set_y(225)
            for k, v in metadata.items():
                self.set_font(self.font_sans, "B", 9)
                self.set_text_color(p_r, p_g, p_b)
                self.cell(38, 6.5, str(k) + ":", border=0)
                self.set_font(self.font_sans, "", 9)
                self.set_text_color(45, 55, 65)
                self.cell(0, 6.5, str(v), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_left_margin(18)
        self.is_cover = False

    def add_section_header(self, title: str, subtitle: str = ""):
        self.check_page_break(32)
        self.ln(5)
        cur_y = self.get_y()

        p_r, p_g, p_b = self.theme["primary"]
        self.set_fill_color(p_r, p_g, p_b)
        self.rect(18, cur_y, 174, 11, "F")

        self.set_xy(22, cur_y + 1.8)
        self.set_font(self.font_sans, "B", 10.5)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, title)

        self.set_y(cur_y + 13)
        if subtitle:
            self.set_font(self.font_sans, "I", 9)
            self.set_text_color(70, 85, 105)
            self.cell(0, 5, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)

    def add_qa(self, q_num: str, question: str, answer: str):
        self.check_page_break(25)
        self.ln(2.5)
        cur_y = self.get_y()
        self.set_font(self.font_sans, "B", 9.5)

        prefix = f"Soru {q_num}: " if q_num else ""
        full_q = f"{prefix}{question}"

        str_w = self.get_string_width(full_q)
        lines_est = max(len(full_q.split("\n")), int(str_w / 155) + 1)
        box_h = max(9.5, lines_est * 5.2 + 3.5)

        if cur_y + box_h > 275:
            self.add_page()
            cur_y = self.get_y()

        bg_r, bg_g, bg_b = self.theme["card_bg"]
        b_r, b_g, b_b = self.theme["card_border"]
        self.set_fill_color(bg_r, bg_g, bg_b)
        self.set_draw_color(b_r, b_g, b_b)
        self.set_line_width(0.35)
        self.rect(18, cur_y, 174, box_h, "DF")

        a_r, a_g, a_b = self.theme["accent"]
        self.set_fill_color(a_r, a_g, a_b)
        self.rect(18, cur_y, 2.5, box_h, "F")

        self.set_xy(23, cur_y + 1.8)
        self.set_text_color(20, 45, 80)
        self.multi_cell(166, 4.8, full_q)
        self.set_y(cur_y + box_h + 2.5)

        if answer:
            self.add_paragraph(answer)

    def add_paragraph(self, text: str, bold_prefix: str = ""):
        self.check_page_break(12)
        self.set_font(self.font_sans, "", 9)
        t_r, t_g, t_b = self.theme["text_body"]
        self.set_text_color(t_r, t_g, t_b)

        if bold_prefix:
            self.set_font(self.font_sans, "B", 9)
            self.write(5.2, bold_prefix + " ")
            self.set_font(self.font_sans, "", 9)
        self.write(5.2, text + "\n")
        self.ln(1.8)

    def add_bullet(self, title: str, text: str):
        self.check_page_break(13)
        self.set_font(self.font_sans, "B", 9)
        p_r, p_g, p_b = self.theme["primary"]
        self.set_text_color(p_r, p_g, p_b)
        self.set_x(22)
        self.cell(4, 5.2, "•", border=0)

        if title:
            self.write(5.2, title + ": ")
        self.set_font(self.font_sans, "", 9)
        t_r, t_g, t_b = self.theme["text_body"]
        self.set_text_color(t_r, t_g, t_b)
        self.write(5.2, text + "\n")
        self.ln(1.2)

    def add_code_block(self, code_text: str):
        lines = code_text.strip().split("\n")
        h = len(lines) * 4.8 + 4
        self.check_page_break(min(h + 4, 65))
        cur_y = self.get_y()

        c_bg_r, c_bg_g, c_bg_b = self.theme["code_bg"]
        c_b_r, c_b_g, c_b_b = self.theme["code_border"]
        self.set_fill_color(c_bg_r, c_bg_g, c_bg_b)
        self.set_draw_color(c_b_r, c_b_g, c_b_b)
        self.set_line_width(0.3)
        self.rect(22, cur_y, 170, h, "DF")

        self.set_xy(25, cur_y + 2)
        self.set_font(self.font_mono, "", 8.5)
        self.set_text_color(30, 35, 45)
        for line in lines:
            self.cell(0, 4.8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_x(25)
        self.set_y(cur_y + h + 2.5)

    def add_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        col_widths: Optional[List[float]] = None
    ):
        """Render a publication-grade styled table with header and zebra striping."""
        if not headers and not rows:
            return

        est_h = (len(rows) + 1) * 7 + 6
        self.check_page_break(min(est_h, 45))
        self.ln(2)

        p_r, p_g, p_b = self.theme["primary"]
        bg_r, bg_g, bg_b = self.theme["card_bg"]
        b_r, b_g, b_b = self.theme["card_border"]
        t_r, t_g, t_b = self.theme["text_body"]

        self.set_font(self.font_sans, "", 8.5)
        self.set_draw_color(b_r, b_g, b_b)
        self.set_line_width(0.3)
        self.set_text_color(t_r, t_g, t_b)

        headings_style = FontFace(
            emphasis="BOLD",
            color=(255, 255, 255),
            fill_color=(p_r, p_g, p_b),
            size_pt=9
        )

        table_kwargs: Dict[str, Any] = {
            "headings_style": headings_style,
            "cell_fill_color": (bg_r, bg_g, bg_b),
            "cell_fill_mode": "ROWS",
            "line_height": 6,
            "width": 174,
            "align": "L",
        }
        if col_widths:
            table_kwargs["col_widths"] = tuple(col_widths)

        with self.table(**table_kwargs) as table:
            if headers:
                hdr_row = table.row()
                for h_text in headers:
                    hdr_row.cell(str(h_text))
            for r_data in rows:
                row = table.row()
                for cell_val in r_data:
                    row.cell(str(cell_val))

        self.ln(3)

    def add_callout(self, text: str, kind: str = "note", title: str = ""):
        """Render a styled callout / alert box (note, tip, warning, important, caution)."""
        style = CALLOUT_STYLES.get(kind.lower(), CALLOUT_STYLES["note"])
        box_title = title if title else style["default_title"]

        self.set_font(self.font_sans, "", 9)
        str_w = self.get_string_width(text)
        lines_est = max(len(text.split("\n")), int(str_w / 152) + 1)
        box_h = max(14, lines_est * 5.0 + 10)

        self.check_page_break(box_h + 4)
        self.ln(2)
        cur_y = self.get_y()

        bg_r, bg_g, bg_b = style["bg"]
        b_r, b_g, b_b = style["border"]
        a_r, a_g, a_b = style["accent"]

        self.set_fill_color(bg_r, bg_g, bg_b)
        self.set_draw_color(b_r, b_g, b_b)
        self.set_line_width(0.35)
        self.rect(18, cur_y, 174, box_h, "DF")

        self.set_fill_color(a_r, a_g, a_b)
        self.rect(18, cur_y, 3.0, box_h, "F")

        self.set_xy(24, cur_y + 2.2)
        self.set_font(self.font_sans, "B", 9)
        self.set_text_color(a_r, a_g, a_b)
        self.cell(0, 5, box_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_x(24)
        self.set_font(self.font_sans, "", 8.8)
        t_r, t_g, t_b = self.theme["text_body"]
        self.set_text_color(t_r, t_g, t_b)
        self.multi_cell(164, 4.8, text)

        self.set_y(cur_y + box_h + 3)

    def add_image(self, image_path: str, caption: str = "", max_w: float = 160.0):
        """Embed an image with automatic aspect-ratio scaling, centering, and optional caption."""
        if not image_path or not os.path.exists(image_path):
            self.add_callout(
                f"Görsel dosyası bulunamadı: {image_path}",
                kind="warning",
                title="EKSİK GÖRSEL"
            )
            return

        disp_w = min(max_w, 170.0)
        disp_h = 65.0

        if PILImage is not None:
            try:
                with PILImage.open(image_path) as im:
                    px_w, px_h = im.size
                    if px_w > 0 and px_h > 0:
                        aspect = px_h / float(px_w)
                        disp_h = disp_w * aspect
                        if disp_h > 120.0:
                            disp_h = 120.0
                            disp_w = disp_h / aspect
            except Exception:
                pass

        total_h = disp_h + (8.0 if caption else 3.0)
        self.check_page_break(total_h)
        self.ln(2)

        x_pos = 18.0 + (174.0 - disp_w) / 2.0
        cur_y = self.get_y()

        try:
            self.image(image_path, x=x_pos, y=cur_y, w=disp_w)
            self.set_y(cur_y + disp_h + 1.5)
            if caption:
                self.set_font(self.font_sans, "I", 8.5)
                self.set_text_color(95, 105, 120)
                self.cell(0, 5, caption, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)
        except Exception as e:
            self.add_callout(
                f"Görsel işlenirken hata oluştu ({image_path}): {e}",
                kind="warning",
                title="GÖRSEL HATASI"
            )


def _clean_md_inline(text: str) -> str:
    """Strip inline Markdown markers (**bold**, `code`) for plain cell/text rendering."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    s = re.sub(r"__(.+?)__", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s.strip()


def parse_markdown_to_doc_data(
    markdown_text: str,
    title: Optional[str] = None,
    subtitle: str = "",
    category: str = "DOKÜMAN RAPORU",
    description: str = "",
    metadata: Optional[Dict[str, str]] = None,
    theme: str = "navy_blue",
    base_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse standard Markdown text (with optional YAML frontmatter) into the
    structured dictionary format consumed by build_pdf_document.
    """
    meta_dict: Dict[str, str] = dict(metadata) if metadata else {}
    lines = markdown_text.replace("\r\n", "\n").split("\n")
    idx = 0
    n = len(lines)

    # 1. Parse optional YAML frontmatter
    if n > 0 and lines[0].strip() == "---":
        idx = 1
        while idx < n and lines[idx].strip() != "---":
            line = lines[idx].strip()
            if ":" in line:
                k, v = line.split(":", 1)
                k_clean = k.strip()
                v_clean = v.strip().strip('"').strip("'")
                k_low = k_clean.lower()
                if k_low == "title" and not title:
                    title = v_clean
                elif k_low == "subtitle" and not subtitle:
                    subtitle = v_clean
                elif k_low == "category":
                    category = v_clean
                elif k_low == "description" and not description:
                    description = v_clean
                elif k_low == "theme":
                    theme = v_clean
                else:
                    meta_dict[k_clean] = v_clean
            idx += 1
        idx += 1  # Skip closing '---'

    sections: List[Dict[str, Any]] = []
    current_section: Optional[Dict[str, Any]] = None
    active_qa: Optional[Dict[str, Any]] = None

    def ensure_section(default_title: str = "BÖLÜM 1: GENEL İÇERİK") -> Dict[str, Any]:
        nonlocal current_section
        if current_section is None:
            current_section = {"title": default_title, "subtitle": "", "items": []}
            sections.append(current_section)
        return current_section

    def flush_active_qa():
        nonlocal active_qa
        if active_qa is not None:
            active_qa["answer"] = "\n".join(active_qa.pop("_ans_lines", [])).strip()
            active_qa = None

    while idx < n:
        raw_line = lines[idx]
        stripped = raw_line.strip()

        # Skip empty lines or horizontal rules
        if not stripped or re.match(r"^[-*_]{3,}$", stripped):
            idx += 1
            continue

        # 2. Fenced Code Block: ```lang ... ```
        if stripped.startswith("```"):
            flush_active_qa()
            idx += 1
            code_lines = []
            while idx < n and not lines[idx].strip().startswith("```"):
                code_lines.append(lines[idx])
                idx += 1
            idx += 1  # Skip closing ```
            sec = ensure_section()
            sec["items"].append({
                "type": "code",
                "code": "\n".join(code_lines)
            })
            continue

        # 3. Markdown Table: | col1 | col2 |
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            flush_active_qa()
            table_lines = []
            while idx < n:
                tl = lines[idx].strip()
                if tl.startswith("|") and tl.endswith("|"):
                    table_lines.append(tl)
                    idx += 1
                else:
                    break

            headers: List[str] = []
            rows: List[List[str]] = []
            for t_idx, tl in enumerate(table_lines):
                cells = [_clean_md_inline(c.strip()) for c in tl.strip("|").split("|")]
                # Check if separator row like |---|---|
                if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                    continue
                if not headers and t_idx == 0:
                    headers = cells
                else:
                    rows.append(cells)

            if headers or rows:
                sec = ensure_section()
                sec["items"].append({
                    "type": "table",
                    "headers": headers,
                    "rows": rows
                })
            continue

        # 4. Blockquote / Callout: > [!NOTE] or > text
        if stripped.startswith(">"):
            flush_active_qa()
            quote_lines = []
            while idx < n and lines[idx].strip().startswith(">"):
                q_line = re.sub(r"^>\s?", "", lines[idx].strip())
                quote_lines.append(q_line)
                idx += 1

            kind = "note"
            c_title = ""
            if quote_lines:
                m_alert = re.match(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|INFO)\]\s*(.*)$", quote_lines[0], re.IGNORECASE)
                if m_alert:
                    kind = m_alert.group(1).lower()
                    c_title = _clean_md_inline(m_alert.group(2))
                    quote_lines = quote_lines[1:]

            c_text = _clean_md_inline("\n".join(quote_lines))
            if c_text or c_title:
                sec = ensure_section()
                sec["items"].append({
                    "type": "callout",
                    "kind": kind,
                    "title": c_title,
                    "text": c_text
                })
            continue

        # 5. Image: ![Caption](path)
        m_img = re.match(r"^!\[(.*?)\]\((.+?)\)$", stripped)
        if m_img:
            flush_active_qa()
            cap = m_img.group(1).strip()
            img_p = m_img.group(2).strip()
            if base_dir and not os.path.isabs(img_p):
                img_p = os.path.join(base_dir, img_p)
            sec = ensure_section()
            sec["items"].append({
                "type": "image",
                "image_path": img_p,
                "caption": cap
            })
            idx += 1
            continue

        # 6. Headings (#, ##, ###)
        m_hdr = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if m_hdr:
            flush_active_qa()
            level = len(m_hdr.group(1))
            hdr_text = _clean_md_inline(m_hdr.group(2))

            if level == 1:
                if not title and not sections and current_section is None:
                    title = hdr_text
                else:
                    current_section = {"title": hdr_text, "subtitle": "", "items": []}
                    sections.append(current_section)
            elif level == 2:
                # Check if it's a Question heading or Section heading
                m_q = re.match(r"^(?:Soru|Question|Q)\s*([0-9A-Za-z._-]*)\s*[:.-]\s*(.+)$", hdr_text, re.IGNORECASE)
                if m_q:
                    sec = ensure_section()
                    qa_item = {
                        "type": "qa",
                        "q_num": m_q.group(1).strip(),
                        "question": m_q.group(2).strip(),
                        "answer": "",
                        "_ans_lines": []
                    }
                    sec["items"].append(qa_item)
                    active_qa = qa_item
                else:
                    current_section = {"title": hdr_text, "subtitle": "", "items": []}
                    sections.append(current_section)
            else:
                # Level 3 or 4 -> QA card or bold subheading
                m_q = re.match(r"^(?:Soru|Question|Q)\s*([0-9A-Za-z._-]*)\s*[:.-]\s*(.+)$", hdr_text, re.IGNORECASE)
                sec = ensure_section()
                if m_q:
                    qa_item = {
                        "type": "qa",
                        "q_num": m_q.group(1).strip(),
                        "question": m_q.group(2).strip(),
                        "answer": "",
                        "_ans_lines": []
                    }
                else:
                    qa_item = {
                        "type": "qa",
                        "q_num": "",
                        "question": hdr_text,
                        "answer": "",
                        "_ans_lines": []
                    }
                sec["items"].append(qa_item)
                active_qa = qa_item

            idx += 1
            continue

        # 7. Bullet Lists: - item, * item, • item
        m_bul = re.match(r"^[-*•]\s+(.+)$", stripped)
        if m_bul:
            flush_active_qa()
            bul_content = m_bul.group(1).strip()
            m_btitle = re.match(r"^\*\*(.+?)\*\*\s*[:.-]?\s*(.*)$", bul_content)
            if m_btitle and m_btitle.group(2):
                b_title = _clean_md_inline(m_btitle.group(1)).rstrip(":")
                b_text = _clean_md_inline(m_btitle.group(2))
            else:
                b_title = ""
                b_text = _clean_md_inline(bul_content)

            sec = ensure_section()
            sec["items"].append({
                "type": "bullet",
                "title": b_title,
                "text": b_text
            })
            idx += 1
            continue

        # 8. Regular Paragraph (or continuation of active QA answer)
        para_lines = []
        while idx < n:
            pl = lines[idx].strip()
            if (
                not pl
                or pl.startswith("#")
                or pl.startswith("```")
                or pl.startswith(">")
                or pl.startswith("![")
                or (pl.startswith("|") and pl.endswith("|"))
                or re.match(r"^[-*•]\s+", pl)
                or re.match(r"^[-*_]{3,}$", pl)
            ):
                break
            para_lines.append(pl)
            idx += 1

        para_raw = " ".join(para_lines)
        if active_qa is not None:
            active_qa["_ans_lines"].append(_clean_md_inline(para_raw))
        else:
            sec = ensure_section()
            m_prefix = re.match(r"^\*\*(.+?)\*\*\s+(.+)$", para_raw)
            if m_prefix:
                sec["items"].append({
                    "type": "paragraph",
                    "bold_prefix": _clean_md_inline(m_prefix.group(1)),
                    "text": _clean_md_inline(m_prefix.group(2))
                })
            else:
                sec["items"].append({
                    "type": "paragraph",
                    "bold_prefix": "",
                    "text": _clean_md_inline(para_raw)
                })

    flush_active_qa()

    return {
        "title": title or "Doküman Raporu",
        "subtitle": subtitle,
        "category": category,
        "description": description,
        "metadata": meta_dict,
        "theme": theme,
        "sections": sections
    }


def build_pdf_document(doc_data: Dict[str, Any], output_path: str) -> str:
    """
    High-level entrypoint to build a PDF from structured JSON/dict data
    or from an external 'input_file' (.json or .md).
    """
    input_file = doc_data.get("input_file")
    if input_file:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        ext = os.path.splitext(input_file)[1].lower()
        if ext in (".md", ".markdown"):
            return build_pdf_from_markdown(
                output_path=output_path,
                markdown_file=input_file,
                title=doc_data.get("title"),
                subtitle=doc_data.get("subtitle", ""),
                category=doc_data.get("category", "DOKÜMAN RAPORU"),
                description=doc_data.get("description", ""),
                metadata=doc_data.get("metadata"),
                theme=doc_data.get("theme", "navy_blue")
            )
        else:
            with open(input_file, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            # Allow doc_data overrides if explicitly set
            for key in ("title", "subtitle", "category", "description", "metadata", "theme", "sections"):
                if key in doc_data and doc_data[key]:
                    loaded_data[key] = doc_data[key]
            doc_data = loaded_data

    title = doc_data.get("title", "Doküman")
    subtitle = doc_data.get("subtitle", "")
    category = doc_data.get("category", "")
    description = doc_data.get("description", "")
    metadata = doc_data.get("metadata", {})
    theme_name = doc_data.get("theme", "navy_blue")

    builder = PDFReportBuilder(header_title=title, theme_name=theme_name)
    builder.draw_cover(
        title=title,
        subtitle=subtitle,
        category=category,
        description=description,
        metadata=metadata
    )

    builder.add_page()

    sections = doc_data.get("sections", [])
    for sec in sections:
        sec_title = sec.get("title", "")
        sec_sub = sec.get("subtitle", "")
        if sec_title:
            builder.add_section_header(sec_title, sec_sub)

        for item in sec.get("items", []):
            item_type = item.get("type", "paragraph")

            if item_type == "qa":
                builder.add_qa(
                    q_num=item.get("q_num", ""),
                    question=item.get("question", ""),
                    answer=item.get("answer", "")
                )
            elif item_type == "paragraph":
                builder.add_paragraph(
                    text=item.get("text", ""),
                    bold_prefix=item.get("bold_prefix", "")
                )
            elif item_type == "bullet":
                builder.add_bullet(
                    title=item.get("title", ""),
                    text=item.get("text", "")
                )
            elif item_type == "code":
                builder.add_code_block(item.get("code", ""))
            elif item_type == "table":
                builder.add_table(
                    headers=item.get("headers", []),
                    rows=item.get("rows", []),
                    col_widths=item.get("col_widths")
                )
            elif item_type == "callout":
                builder.add_callout(
                    text=item.get("text", ""),
                    kind=item.get("kind", "note"),
                    title=item.get("title", "")
                )
            elif item_type == "image":
                builder.add_image(
                    image_path=item.get("image_path", ""),
                    caption=item.get("caption", ""),
                    max_w=float(item.get("max_width", 160.0))
                )

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    builder.output(output_path)
    return os.path.abspath(output_path)


def build_pdf_from_markdown(
    output_path: str,
    markdown_text: Optional[str] = None,
    markdown_file: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: str = "",
    category: str = "DOKÜMAN RAPORU",
    description: str = "",
    metadata: Optional[Dict[str, str]] = None,
    theme: str = "navy_blue"
) -> str:
    """
    Compile a Markdown string or Markdown file (.md) directly into a styled PDF report.
    """
    base_dir = None
    if markdown_file:
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        base_dir = os.path.dirname(os.path.abspath(markdown_file))
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_text = f.read()

    if not markdown_text:
        raise ValueError("Either 'markdown_text' or 'markdown_file' must be provided.")

    doc_data = parse_markdown_to_doc_data(
        markdown_text=markdown_text,
        title=title,
        subtitle=subtitle,
        category=category,
        description=description,
        metadata=metadata,
        theme=theme,
        base_dir=base_dir
    )
    return build_pdf_document(doc_data, output_path)
