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
import io
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from fpdf import FPDF
from fpdf.enums import XPos, YPos, MethodReturnValue
from fpdf.fonts import FontFace

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

try:
    from matplotlib import mathtext
except ImportError:
    mathtext = None

logger = logging.getLogger("pdf_mcp.writer")


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

GREEK_MAP = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\varepsilon": "ε", r"\zeta": "ζ", r"\eta": "η",
    r"\theta": "θ", r"\vartheta": "ϑ", r"\iota": "ι", r"\kappa": "κ",
    r"\lambda": "λ", r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ",
    r"\pi": "π", r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ",
    r"\upsilon": "υ", r"\phi": "φ", r"\varphi": "ϕ", r"\chi": "χ",
    r"\psi": "ψ", r"\omega": "ω",
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ",
    r"\Xi": "Ξ", r"\Pi": "Π", r"\Sigma": "Σ", r"\Upsilon": "Υ",
    r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
}

MATH_SYMBOL_MAP = {
    r"\times": "×", r"\cdot": "·", r"\div": "÷", r"\pm": "±", r"\mp": "∓",
    r"\leq": "≤", r"\le": "≤", r"\geq": "≥", r"\ge": "≥",
    r"\neq": "≠", r"\ne": "≠", r"\approx": "≈", r"\sim": "~",
    r"\equiv": "≡", r"\propto": "∝",
    r"\infty": "∞", r"\partial": "∂", r"\nabla": "∇",
    r"\in": "∈", r"\notin": "∉",
    r"\subset": "⊂", r"\subseteq": "⊆", r"\supset": "⊃", r"\supseteq": "⊇",
    r"\cap": "∩", r"\cup": "∪",
    r"\forall": "∀", r"\exists": "∃", r"\nexists": "∄", r"\neg": "¬",
    r"\to": "→", r"\rightarrow": "→", r"\leftarrow": "←",
    r"\Rightarrow": "⇒", r"\Leftarrow": "⇐", r"\Leftrightarrow": "⇔",
    r"\sum": "∑", r"\prod": "∏", r"\int": "∫",
    r"\circ": "°", r"\bullet": "•",
}

SUP_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "+", "-": "-", "=": "=", "(": "(", ")": ")",
    "n": "ⁿ", "i": "ⁱ", "x": "ˣ", "y": "ʸ",
}

SUB_MAP = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "+", "-": "-", "=": "=", "(": "(", ")": ")",
}


def _convert_math_fragment(s: str) -> str:
    """Convert a single LaTeX math fragment into a clean readable Unicode representation."""
    # LaTeX text styling macros
    s = re.sub(r"\\(?:textbf|mathbf)\{([^}]+)\}", r"**\1**", s)
    s = re.sub(r"\\(?:textit|mathit)\{([^}]+)\}", r"*\1*", s)
    s = re.sub(r"\\(?:text|mathrm|operatorname)\{([^}]+)\}", r"\1", s)

    # Fractions: \frac{a}{b} -> (a)/(b)
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", s)

    # Roots: \sqrt[n]{x} -> (n)√(x), \sqrt{x} -> √(x)
    s = re.sub(r"\\sqrt\[([^\]]+)\]\{([^{}]+)\}", r"(\1)√(\2)", s)
    s = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", s)

    # Greek letters
    for cmd, sym in sorted(GREEK_MAP.items(), key=lambda x: -len(x[0])):
        s = re.sub(re.escape(cmd) + r"(?![a-zA-Z])", sym, s)

    # Math symbols
    for cmd, sym in sorted(MATH_SYMBOL_MAP.items(), key=lambda x: -len(x[0])):
        s = re.sub(re.escape(cmd) + r"(?![a-zA-Z])", sym, s)

    # Superscripts: ^{123} or ^2
    def replace_sup(m):
        content = m.group(1) or m.group(2)
        return "".join(SUP_MAP.get(c, c) for c in content)
    s = re.sub(r"\^\{([^}]+)\}|\^([0-9nixy+\-])", replace_sup, s)

    # Subscripts: _{123} or _2
    def replace_sub(m):
        content = m.group(1) or m.group(2)
        return "".join(SUB_MAP.get(c, c) for c in content)
    s = re.sub(r"\_\{([^}]+)\}|\_([0-9+\-])", replace_sub, s)

    return s.strip()


def _convert_inline_latex(text: str) -> str:
    """Detect inline math ($...$, \\(...\\)) and common LaTeX syntax, converting to clean Unicode."""
    if not text:
        return ""

    # Replace inline math: $...$
    def repl_dollar(m):
        return _convert_math_fragment(m.group(1))

    # Match $...$ where $ is not escaped with backslash
    text = re.sub(r"(?<!\\)\$([^\$\n]+?)(?<!\\)\$", repl_dollar, text)
    # Match \(...\)
    text = re.sub(r"\\\((.+?)\\\)", repl_dollar, text)

    # Convert any remaining unenclosed common LaTeX commands if present
    text = _convert_math_fragment(text)
    # Unescape escaped dollar signs
    text = text.replace(r"\$", "$")
    return text


def _render_latex_math(
    latex_code: str,
    dpi: int = 300,
    color: Optional[Tuple[int, int, int]] = None
) -> Tuple[Optional[io.BytesIO], float, float]:
    """
    Render a LaTeX math formula into an in-memory PNG buffer using matplotlib.mathtext.
    Returns (bytes_io, width_mm, height_mm). If rendering fails or mathtext is unavailable, returns (None, 0.0, 0.0).
    """
    if mathtext is None or PILImage is None:
        return None, 0.0, 0.0

    raw_eq = latex_code.strip()
    # Strip any enclosing math delimiters
    if raw_eq.startswith("$$") and raw_eq.endswith("$$") and len(raw_eq) >= 4:
        raw_eq = raw_eq[2:-2].strip()
    elif raw_eq.startswith(r"\[") and raw_eq.endswith(r"\]") and len(raw_eq) >= 4:
        raw_eq = raw_eq[2:-2].strip()
    elif raw_eq.startswith("$") and raw_eq.endswith("$") and len(raw_eq) >= 2:
        raw_eq = raw_eq[1:-1].strip()

    eq_formatted = f"${raw_eq}$"

    buf = io.BytesIO()
    hex_color = None
    if color:
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    try:
        mathtext.math_to_image(eq_formatted, buf, dpi=dpi, format="png", color=hex_color)
        buf.seek(0)
        with PILImage.open(buf) as img:
            px_w, px_h = img.size
        # Convert pixels to mm: 1 inch = 25.4 mm
        w_mm = (px_w / float(dpi)) * 25.4
        h_mm = (px_h / float(dpi)) * 25.4
        buf.seek(0)
        return buf, w_mm, h_mm
    except Exception as e:
        logger.warning("LaTeX mathtext rendering failed for '%s': %s", raw_eq, e)
        return None, 0.0, 0.0



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
            description = _convert_inline_latex(description)
            c_bg_r, c_bg_g, c_bg_b = self.theme["card_bg"]
            c_b_r, c_b_g, c_b_b = self.theme["card_border"]
            self.set_fill_color(c_bg_r, c_bg_g, c_bg_b)
            self.set_draw_color(c_b_r, c_b_g, c_b_b)
            self.set_line_width(0.35)

            desc_w = 154.0
            desc_line_h = 4.8
            self.set_font(self.font_sans, "", 9)
            desc_h = self.multi_cell(
                desc_w,
                desc_line_h,
                description,
                dry_run=True,
                output=MethodReturnValue.HEIGHT
            )
            title_h = 5.5
            pad_y = 4.0
            gap = 2.0
            box_h = max(24.0, pad_y * 2 + title_h + gap + desc_h)

            cur_y = self.get_y()
            self.rect(24, cur_y, 164, box_h, "DF")

            self.set_xy(28, cur_y + pad_y)
            self.set_font(self.font_sans, "B", 9.5)
            self.set_text_color(p_r, p_g, p_b)
            self.cell(desc_w, title_h, "GENEL BİLGİ VE ÖZET:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_xy(28, cur_y + pad_y + title_h + gap)
            self.set_font(self.font_sans, "", 9)
            self.set_text_color(50, 60, 75)
            self.multi_cell(desc_w, desc_line_h, description)
            self.set_y(cur_y + box_h + 8.0)

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
        title = _convert_inline_latex(title)
        if subtitle:
            subtitle = _convert_inline_latex(subtitle)

        banner_w = 174.0
        text_w = 166.0
        line_h = 5.2

        self.set_font(self.font_sans, "B", 10.5)
        title_h = self.multi_cell(
            text_w,
            line_h,
            title,
            dry_run=True,
            output=MethodReturnValue.HEIGHT
        )
        banner_h = max(11.0, title_h + 4.0)

        self.check_page_break(banner_h + (8.0 if subtitle else 4.0))
        self.ln(5)
        cur_y = self.get_y()

        p_r, p_g, p_b = self.theme["primary"]
        self.set_fill_color(p_r, p_g, p_b)
        self.rect(18, cur_y, banner_w, banner_h, "F")

        self.set_xy(22, cur_y + (banner_h - title_h) / 2.0)
        self.set_font(self.font_sans, "B", 10.5)
        self.set_text_color(255, 255, 255)
        self.multi_cell(text_w, line_h, title)

        self.set_y(cur_y + banner_h + 2.0)
        if subtitle:
            self.set_font(self.font_sans, "I", 9)
            self.set_text_color(70, 85, 105)
            self.cell(0, 5, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)

    def add_qa(self, q_num: str, question: str, answer: str):
        question = _convert_inline_latex(question)
        prefix = f"Soru {q_num}: " if q_num else ""
        full_q = f"{prefix}{question}"

        content_w = 164.0
        pad_x = 6.0
        pad_y = 3.5
        line_h = 4.8

        self.set_font(self.font_sans, "B", 9.5)
        text_h = self.multi_cell(
            content_w,
            line_h,
            full_q,
            dry_run=True,
            output=MethodReturnValue.HEIGHT
        )
        box_h = pad_y * 2 + text_h

        self.check_page_break(box_h + 4.0)
        self.ln(2.5)
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

        self.set_xy(18 + pad_x, cur_y + pad_y)
        self.set_text_color(20, 45, 80)
        self.multi_cell(content_w, line_h, full_q)
        self.set_y(cur_y + box_h + 2.5)

        if answer:
            self.add_paragraph(answer)

    def add_paragraph(self, text: str, bold_prefix: str = ""):
        text = _convert_inline_latex(text)
        if bold_prefix:
            bold_prefix = _convert_inline_latex(bold_prefix)

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
        if title:
            title = _convert_inline_latex(title)
        text = _convert_inline_latex(text)

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
        code_text = code_text.rstrip()
        if not code_text:
            return

        self.set_font(self.font_mono, "", 8.5)
        max_text_w = 162.0
        line_h = 4.6
        pad_y = 3.0
        pad_x = 4.0
        box_w = 170.0
        box_x = 22.0

        # Soft-wrap long lines to prevent horizontal overflow
        formatted_lines: List[str] = []
        for raw_line in code_text.split("\n"):
            if self.get_string_width(raw_line) <= max_text_w:
                formatted_lines.append(raw_line)
            else:
                words = raw_line.split(" ")
                cur_l = ""
                for w in words:
                    candidate = (cur_l + " " + w) if cur_l else w
                    if self.get_string_width(candidate) <= max_text_w:
                        cur_l = candidate
                    else:
                        if cur_l:
                            formatted_lines.append(cur_l)
                            cur_l = "    " + w
                        else:
                            for ch in w:
                                if self.get_string_width(cur_l + ch) <= max_text_w:
                                    cur_l += ch
                                else:
                                    formatted_lines.append(cur_l)
                                    cur_l = "    " + ch
                if cur_l:
                    formatted_lines.append(cur_l)

        c_bg_r, c_bg_g, c_bg_b = self.theme["code_bg"]
        c_b_r, c_b_g, c_b_b = self.theme["code_border"]

        # Check if entire block fits on current page; if not and fits on new page, break early
        total_h = len(formatted_lines) * line_h + pad_y * 2
        cur_y = self.get_y()
        if cur_y + total_h > 275.0 and total_h <= 245.0:
            self.add_page()
            cur_y = self.get_y()

        # Render chunk by chunk so page breaks never split the rectangle awkwardly
        line_idx = 0
        n_lines = len(formatted_lines)
        while line_idx < n_lines:
            cur_y = self.get_y()
            avail_h = 275.0 - cur_y
            lines_fit = int((avail_h - pad_y * 2) / line_h)
            if lines_fit < 1:
                self.add_page()
                cur_y = self.get_y()
                avail_h = 275.0 - cur_y
                lines_fit = max(1, int((avail_h - pad_y * 2) / line_h))

            chunk = formatted_lines[line_idx : line_idx + lines_fit]
            chunk_h = len(chunk) * line_h + pad_y * 2

            self.set_fill_color(c_bg_r, c_bg_g, c_bg_b)
            self.set_draw_color(c_b_r, c_b_g, c_b_b)
            self.set_line_width(0.3)
            self.rect(box_x, cur_y, box_w, chunk_h, "DF")

            self.set_xy(box_x + pad_x, cur_y + pad_y)
            self.set_font(self.font_mono, "", 8.5)
            self.set_text_color(30, 35, 45)
            for line in chunk:
                self.cell(box_w - pad_x * 2, line_h, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.set_x(box_x + pad_x)

            self.set_y(cur_y + chunk_h + 2.5)
            line_idx += len(chunk)

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
                    hdr_row.cell(str(_convert_inline_latex(str(h_text))))
            for r_data in rows:
                row = table.row()
                for cell_val in r_data:
                    row.cell(str(_convert_inline_latex(str(cell_val))))

        self.ln(3)

    def add_callout(self, text: str, kind: str = "note", title: str = ""):
        """Render a styled callout / alert box with dynamic height measurement to prevent overflow."""
        text = _convert_inline_latex(text)
        style = CALLOUT_STYLES.get(kind.lower(), CALLOUT_STYLES["note"])
        box_title = title if title else style["default_title"]
        if box_title:
            box_title = _convert_inline_latex(box_title)

        content_w = 162.0
        pad_x = 6.0
        pad_y = 3.5
        line_h = 4.8
        title_h = 5.0 if box_title else 0.0
        gap = 2.0 if box_title else 0.0

        # Exact multi_cell text height measurement
        self.set_font(self.font_sans, "", 8.8)
        text_h = self.multi_cell(
            content_w,
            line_h,
            text,
            dry_run=True,
            output=MethodReturnValue.HEIGHT
        )
        box_h = pad_y * 2 + title_h + gap + text_h

        self.check_page_break(box_h + 4.0)
        self.ln(2.0)
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

        inner_y = cur_y + pad_y
        if box_title:
            self.set_xy(18 + pad_x, inner_y)
            self.set_font(self.font_sans, "B", 9)
            self.set_text_color(a_r, a_g, a_b)
            self.cell(content_w, title_h, box_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            inner_y += title_h + gap

        self.set_xy(18 + pad_x, inner_y)
        self.set_font(self.font_sans, "", 8.8)
        t_r, t_g, t_b = self.theme["text_body"]
        self.set_text_color(t_r, t_g, t_b)
        self.multi_cell(content_w, line_h, text)

        self.set_y(cur_y + box_h + 3.0)

    def add_math(
        self,
        equation: str,
        caption: str = "",
        label: str = ""
    ):
        """
        Render a standalone LaTeX math equation block inside an elegant math card.
        Uses matplotlib.mathtext for publication-grade mathematical typography.
        """
        raw_eq = equation.strip()
        if not raw_eq:
            return

        buf, w_mm, h_mm = _render_latex_math(raw_eq, dpi=300, color=self.theme["text_dark"])

        # Fallback if mathtext failed or was unavailable
        if buf is None:
            display_text = _convert_inline_latex(raw_eq)
            self.add_callout(
                display_text,
                kind="note",
                title=caption or (f"DENKLEM {label}".strip() if label else "MATEMATİK DENKLEMİ")
            )
            return

        # Responsive scaling if equation is wider than available card width
        max_eq_w = 155.0
        if w_mm > max_eq_w:
            ratio = max_eq_w / w_mm
            w_mm = max_eq_w
            h_mm = h_mm * ratio

        pad_y = 4.0
        cap_h = 5.0 if caption else 0.0
        gap = 2.0 if caption else 0.0
        card_h = pad_y * 2 + h_mm + cap_h + gap
        card_w = 174.0

        self.check_page_break(card_h + 4.0)
        self.ln(2.5)
        cur_y = self.get_y()

        c_bg_r, c_bg_g, c_bg_b = self.theme["card_bg"]
        c_b_r, c_b_g, c_b_b = self.theme["card_border"]
        self.set_fill_color(c_bg_r, c_bg_g, c_bg_b)
        self.set_draw_color(c_b_r, c_b_g, c_b_b)
        self.set_line_width(0.35)
        self.rect(18, cur_y, card_w, card_h, "DF")

        a_r, a_g, a_b = self.theme["accent"]
        self.set_fill_color(a_r, a_g, a_b)
        self.rect(18, cur_y, 2.5, card_h, "F")

        eq_x = 18.0 + (card_w - w_mm) / 2.0
        eq_y = cur_y + pad_y

        self.image(buf, x=eq_x, y=eq_y, w=w_mm, h=h_mm)

        if label:
            self.set_font(self.font_sans, "B", 9)
            self.set_text_color(100, 115, 130)
            self.set_xy(18 + card_w - 20, eq_y + (h_mm - 5.0) / 2.0)
            self.cell(16, 5.0, f"({label})", align="R")

        if caption:
            self.set_xy(22, eq_y + h_mm + gap)
            self.set_font(self.font_sans, "I", 8.5)
            self.set_text_color(85, 95, 110)
            self.cell(card_w - 8.0, cap_h, caption, align="C")

        self.set_y(cur_y + card_h + 3.0)

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
    """Convert inline LaTeX math and strip inline Markdown markers (**bold**, `code`)."""
    s = _convert_inline_latex(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
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

        # 2. Block Math: $$ ... $$
        if stripped.startswith("$$"):
            flush_active_qa()
            if stripped.endswith("$$") and len(stripped) > 2:
                eq_content = stripped[2:-2].strip()
                idx += 1
            else:
                idx += 1
                eq_lines = []
                while idx < n and not lines[idx].strip().endswith("$$"):
                    eq_lines.append(lines[idx])
                    idx += 1
                if idx < n and lines[idx].strip().endswith("$$"):
                    last_l = lines[idx].strip()[:-2].strip()
                    if last_l:
                        eq_lines.append(last_l)
                    idx += 1
                eq_content = "\n".join(eq_lines).strip()
            if eq_content:
                sec = ensure_section()
                sec["items"].append({
                    "type": "math",
                    "equation": eq_content
                })
            continue

        # 3. Block Math: \[ ... \]
        if stripped.startswith(r"\["):
            flush_active_qa()
            if stripped.endswith(r"\]") and len(stripped) > 2:
                eq_content = stripped[2:-2].strip()
                idx += 1
            else:
                idx += 1
                eq_lines = []
                while idx < n and not lines[idx].strip().endswith(r"\]"):
                    eq_lines.append(lines[idx])
                    idx += 1
                if idx < n and lines[idx].strip().endswith(r"\]"):
                    last_l = lines[idx].strip()[:-2].strip()
                    if last_l:
                        eq_lines.append(last_l)
                    idx += 1
                eq_content = "\n".join(eq_lines).strip()
            if eq_content:
                sec = ensure_section()
                sec["items"].append({
                    "type": "math",
                    "equation": eq_content
                })
            continue

        # 4. Fenced Code Block: ```lang ... ```
        if stripped.startswith("```"):
            flush_active_qa()
            lang_tag = stripped[3:].strip().lower()
            idx += 1
            code_lines = []
            while idx < n and not lines[idx].strip().startswith("```"):
                code_lines.append(lines[idx])
                idx += 1
            idx += 1  # Skip closing ```
            sec = ensure_section()
            if lang_tag in ("math", "latex", "tex"):
                sec["items"].append({
                    "type": "math",
                    "equation": "\n".join(code_lines).strip()
                })
            else:
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
                or pl.startswith("$$")
                or pl.startswith(r"\[")
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
            elif item_type == "math":
                builder.add_math(
                    equation=item.get("equation", "") or item.get("code", ""),
                    caption=item.get("caption", ""),
                    label=item.get("label", "")
                )
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
