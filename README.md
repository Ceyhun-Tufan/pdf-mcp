# PDF-MCP (v1.1.0): Model Context Protocol (MCP) Server & CLI Toolkit

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![Version 1.1.0](https://img.shields.io/badge/version-1.1.0-emerald.svg)]()

### 🌐 [**🇬🇧 English Documentation**](#-english-documentation) &nbsp;|&nbsp; [**🇹🇷 Türkçe Dokümantasyon**](#-türkçe-dokümantasyon)

</div>

---

<a name="-english-documentation"></a>

# 🇬🇧 English Documentation

**PDF-MCP** is a lightweight, high-performance **Model Context Protocol (MCP)** server and command-line (CLI) toolkit designed for AI coding assistants (**Google Antigravity**, **Claude Desktop**, **Cursor**) and developers.

It empowers AI agents to natively inspect, batch-search, and diff PDF documents, as well as compile **publication-grade A4 PDF reports directly from Markdown (`.md`) or structured JSON**—complete with cover pages, Q&A cards, code blocks, zebra-striped tables, callout alerts, embedded diagrams, and full UTF-8/Turkish typography support—without writing intermediate dump scripts.

---

## 🆕 What's New in v1.1.0

- **📝 Markdown-First PDF Compiler (`pdf_from_markdown`)**: Pass a standard Markdown file or string; the engine automatically compiles YAML frontmatter, `#` sections, `##` Q&A cards, ` ``` ` code blocks, `| tables |`, `> [!NOTE]` callouts, and `![caption](img)` figures into a styled PDF.
- **📊 Native Styled Table Engine (`table`)**: Automatic column sizing, primary-colored headers, and alternating row backgrounds (zebra striping).
- **💡 Rich Alert / Callout Boxes (`callout`)**: Left-accented callout panels for `NOTE`, `TIP`, `WARNING`, `IMPORTANT`, and `CAUTION`.
- **🖼️ Smart Image & Diagram Embedding (`image`)**: Aspect-ratio preserving centered image rendering with italic captions and graceful fallback placeholders if an image path is missing.
- **📂 Direct File Input (`input_file`)**: Pass a disk path (`.md` or `.json`) to `pdf_generate_report` instead of serializing 100KB+ payloads into the LLM context window.

---

## ✨ Core Tools & Capabilities

| Tool Name | Description |
| :--- | :--- |
| **`pdf_from_markdown`** | ***(New)*** Compiles a `.md` file or raw Markdown string directly into a publication-grade styled PDF report. |
| **`pdf_generate_report`** | Builds a styled PDF from structured JSON data or an external `input_file` (`qa`, `table`, `callout`, `image`, `code`, `bullet`). |
| **`pdf_read_text`** | Extracts clean text from an entire PDF or specific page ranges (`start_page` - `end_page`, 1-based). |
| **`pdf_search_batch`** | Rapidly searches across dozens of PDFs in a directory (`*.pdf`, `L*.pdf`) using keywords or regular expressions. |
| **`pdf_get_metadata`** | Retrieves total page count, file size, title, author, and encryption status. |
| **`pdf_compare_files`** | Compares two PDF files page-by-page to pinpoint textual differences. |
| **Full Unicode / Turkish** | Native TrueType font support (`Arial`, `Calibri`, `Segoe UI`, `Consolas`, `DejaVu`) for flawless `ç, ğ, ı, ö, ş, ü, İ, Ğ, Ş` rendering. |

---

## 🚀 Quick Start & Installation (EN)

### 1. Install Dependencies

PDF-MCP requires only two lightweight packages (`pypdf` and `fpdf2`):

```bash
git clone https://github.com/your-username/pdf-mcp.git
cd pdf-mcp
pip install -r requirements.txt
```

*(Optional) Install in editable mode for global `pdf-mcp` CLI access:*

```bash
pip install -e .
```

### 2. MCP Server Configuration

#### Google Antigravity (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "pdf-toolkit": {
      "command": "python",
      "args": [
        "C:/path/to/pdf-mcp/pdf_mcp/server.py"
      ],
      "disabled": false
    }
  }
}
```

#### Claude Desktop / Cursor (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "pdf-toolkit": {
      "command": "python",
      "args": [
        "C:/path/to/pdf-mcp/pdf_mcp/server.py"
      ]
    }
  }
}
```

---

## ⚡ Instant Usage Guide (Markdown $\rightarrow$ PDF)

### Scenario: Compile Markdown to PDF in One Step (Recommended)

Create a `.md` file with optional YAML frontmatter to configure the cover page and theme (`navy_blue`, `emerald`, `slate`):

````markdown
---
title: DATABASE MANAGEMENT SYSTEMS
subtitle: Past Exam Questions & Comprehensive Solutions
category: COURSE NOTES
description: Complete solution guide covering relational algebra, ER modeling, and SQL.
theme: navy_blue
Instructor: Assoc. Prof. Ahmet Arif AYDIN
Author: Ceyhun TUFAN
Date: 2026
---

# SECTION 1: CORE CONCEPTS & ER MODELING

## Question 1.1: What is Data Independence?
Data independence is the capacity to change the schema at one level of a database system without having to change the schema at the next higher level.

> [!IMPORTANT] Referential Integrity Rule
> Dependent child records must be deleted or updated before removing a parent primary key record unless ON DELETE CASCADE is specified.

- **Logical Data Independence:** Protects external views from conceptual schema changes.
- **Physical Data Independence:** Protects conceptual schema from storage and indexing changes.

```sql
SELECT s.student_name, COUNT(e.course_code) AS total_courses
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_name;
```

| Course Code | Course Title | Enrolled Students |
| :--- | :--- | :--- |
| BM335 | Database Management Systems | 2 |
| BM315 | Programming Languages | 3 |

![University ER Diagram](raporlar/ermodel.drawio.png)
````

#### Invoke via MCP Tool (`pdf_from_markdown`):
```json
{
  "output_path": "C:/path/to/Output_Report.pdf",
  "markdown_file": "C:/path/to/draft.md"
}
```

### Markdown-to-PDF Syntax Mapping

| Markdown Syntax | Rendered PDF Component |
| :--- | :--- |
| `--- ... ---` (YAML Frontmatter) | Cover page title, subtitle, abstract box, color theme, and bottom metadata key-values |
| `# SECTION 1: ...` | Full-width colored Section Header banner (`add_section_header`) |
| `## Question 1: ...` or `## Soru 1: ...` | Left-accented shaded Q&A Card (`add_qa`) + subsequent paragraph as answer |
| ` ```sql ... ``` ` | Shaded monospace Code Block (`add_code_block`) |
| `\| Col 1 \| Col 2 \|` | Zebra-striped Table with primary-colored header (`add_table`) |
| `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]` | Styled Callout / Alert Box (`add_callout`) |
| `![Caption](path/to/img.png)` | Centered auto-scaled Image with italic caption (`add_image`) |
| `- **Title:** Description` | Bold-prefixed Bullet Point (`add_bullet`) |

---

## 💻 CLI Usage (EN)

```bash
# 1. Compile a Markdown file into a styled PDF (with emerald theme)
python pdf_mcp/cli.py from-md "notes.md" "Output.pdf" --theme emerald

# 2. Generate a PDF from a structured JSON file
python pdf_mcp/cli.py generate "payload.json" "Report.pdf"

# 3. Extract text from specific pages (pages 1 to 3)
python pdf_mcp/cli.py read "slides.pdf" --start 1 --end 3

# 4. Batch-search across all PDFs in a folder
python pdf_mcp/cli.py search "./slides" --pattern "L*.pdf" -q "ACID"

# 5. Inspect PDF metadata
python pdf_mcp/cli.py meta "document.pdf"

# 6. Compare two PDF files page by page
python pdf_mcp/cli.py diff "v1.pdf" "v2.pdf"
```

---

## 🐍 Python API Usage (EN)

```python
from pdf_mcp import build_pdf_from_markdown, PDFReportBuilder

# Option 1: One-Line Markdown Compilation
build_pdf_from_markdown(
    output_path="Quick_Report.pdf",
    markdown_file="draft.md",
    theme="navy_blue"
)

# Option 2: Programmatic Builder API
builder = PDFReportBuilder(header_title="Architecture Report", theme_name="slate")
builder.draw_cover(
    title="SYSTEM ARCHITECTURE REPORT",
    subtitle="Indexing & Query Optimization Analysis",
    category="ENGINEERING",
    description="Comparative analysis of B+ Tree and Hash indexing structures.",
    metadata={"Author": "Ceyhun TUFAN", "Version": "1.1.0"}
)

builder.add_page()
builder.add_section_header("1. INDEX COMPARISON", "Time Complexity Breakdown")
builder.add_table(
    headers=["Index Type", "Point Lookup", "Range Scan"],
    rows=[
        ["B+ Tree", "O(log N)", "Supported (Linked Leaves)"],
        ["Hash Index", "O(1)", "Not Supported"]
    ]
)
builder.add_callout("Use B+ Tree indexes by default for general-purpose workloads.", kind="tip")
builder.add_image("diagram.png", caption="Figure 1: PostgreSQL 8KB Page Layout")
builder.output("Architecture_Report.pdf")
```

---
---

<a name="-türkçe-dokümantasyon"></a>

# 🇹🇷 Türkçe Dokümantasyon

<div align="right">
  <a href="#-english-documentation">⬆️ Go to English Documentation</a>
</div>

**PDF-MCP**, yapay zeka kodlama asistanları (**Google Antigravity**, **Claude Desktop**, **Cursor**) ve geliştiriciler için tasarlanmış hafif, yüksek performanslı bir **Model Context Protocol (MCP)** sunucusu ve komut satırı (CLI) araç setidir.

Ajanların PDF belgelerini okumasına, onlarca slayt/doküman içinde toplu arama yapmasına, iki PDF'i karşılaştırmasına ve **hiçbir ara JSON dönüştürücü script yazmaya gerek kalmadan doğrudan Markdown (`.md`) veya JSON üzerinden yayın kalitesinde A4 PDF raporlar** üretmesine olanak tanır.

---

## 🆕 v1.1.0 ile Gelen Yenilikler

- **📝 Markdown-First PDF Derleyici (`pdf_from_markdown`)**: Ajan veya kullanıcı standart bir Markdown metni/dosyası verir; sistem otomatik olarak kapak sayfası, bölüm başlıkları, soru-cevap kartları, kod blokları, tablolar, uyarı kutuları ve görseller içeren şık bir PDF üretir.
- **📊 Yerleşik Stilize Tablo Motoru (`table`)**: Tema renkli başlık satırı, zebra desenli (alternatif satır dolgulu) ve otomatik metin kaydırmalı tablolar.
- **💡 Renkli Uyarı / Bilgi Panelleri (`callout`)**: `NOTE`, `TIP`, `WARNING`, `IMPORTANT`, `CAUTION` tiplerinde sol kenarı renk şeritli vurgu kutuları.
- **🖼️ Akıllı Görsel ve Diyagram Gömme (`image`)**: En-boy oranını (aspect ratio) koruyarak ortalanmış resim/diyagram ekleme, alt yazı (`caption`) desteği ve eksik görsellerde çökmeyi önleyen hata toleranslı yer tutucu (fallback).
- **📂 Dosya Yolu Desteği (`input_file`)**: Büyük raporlarda 100 KB+ veriyi sohbet bağlamına (context) basmak yerine doğrudan diskteki `.md` veya `.json` dosya yolunu vererek tek adımda derleme.

---

## ✨ Temel Özellikler

| Özellik / Araç | Açıklama |
| :--- | :--- |
| **`pdf_from_markdown`** | ***(Yeni)*** `.md` dosyasını veya ham Markdown metnini doğrudan yayın kalitesinde PDF raporuna derler. |
| **`pdf_generate_report`** | Yapılandırılmış JSON verisinden veya harici `input_file` dosyasından (`qa`, `table`, `callout`, `image`, `code`, `bullet`) PDF üretir. |
| **`pdf_read_text`** | Tam belgeyi veya belirli sayfa aralıklarını (`start_page` - `end_page`) temiz metin olarak çıkarır. |
| **`pdf_search_batch`** | Bir klasördeki onlarca PDF içinde (`*.pdf`, `L*.pdf`) anahtar kelime veya Regex araması yapar. |
| **`pdf_get_metadata`** | Sayfa sayısı, dosya boyutu, başlık, yazar ve şifreleme durumunu döndürür. |
| **`pdf_compare_files`** | İki PDF dosyasını sayfa sayfa karşılaştırarak metin farklarını tespit eder. |
| **Tam Türkçe / UTF-8** | `Arial`, `Calibri`, `Segoe UI`, `Consolas` ve `DejaVu` TrueType fontlarıyla `ç, ğ, ı, ö, ş, ü, İ, Ğ, Ş` karakterlerini kusursuz işler. |

---

## 🚀 Hızlı Kurulum (TR)

### 1. Gereksinimlerin Kurulması

Proje yalnızca iki hafif kütüphaneye (`pypdf` ve `fpdf2`) ihtiyaç duyar:

```bash
git clone https://github.com/your-username/pdf-mcp.git
cd pdf-mcp
pip install -r requirements.txt
```

*(İsteğe Bağlı) Terminalden her yerden `pdf-mcp` komutuyla erişmek için düzenlenebilir modda kurun:*

```bash
pip install -e .
```

### 2. MCP Sunucu Kurulumu

#### Google Antigravity (`C:\Users\<KullanıcıAdı>\.gemini\config\mcp_config.json`)
```json
{
  "mcpServers": {
    "pdf-toolkit": {
      "command": "python",
      "args": [
        "C:/path/to/pdf-mcp/pdf_mcp/server.py"
      ],
      "disabled": false
    }
  }
}
```

#### Claude Desktop / Cursor (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "pdf-toolkit": {
      "command": "python",
      "args": [
        "C:/path/to/pdf-mcp/pdf_mcp/server.py"
      ]
    }
  }
}
```

---

## ⚡ Anlık Kullanım Rehberi (Markdown $\rightarrow$ PDF)

### Senaryo: Markdown Dosyasından Tek Adımda PDF Üretimi (Tavsiye Edilen)

Herhangi bir `.md` dosyası oluşturun. YAML başlığı (frontmatter) ile kapak bilgilerini ve temayı (`navy_blue`, `emerald`, `slate`) belirleyebilirsiniz:

````markdown
---
title: VERİTABANI YÖNETİM SİSTEMLERİ
subtitle: Çıkmış Sınav Soruları ve Çözüm Rehberi
category: DERS NOTLARI
description: Bu doküman L01-L12 vize ve final sorularının detaylı çözümlerini içerir.
theme: navy_blue
Ders Sorumlusu: Doç. Dr. Ahmet Arif AYDIN
Hazırlayan: Ceyhun TUFAN
Tarih: 2026
---

# BÖLÜM 1: TEMEL KAVRAMLAR VE ER MODELİ

## Soru 1.1: Veri Bağımsızlığı (Data Independence) nedir?
Veritabanının fiziksel veya mantıksal şemasında yapılan değişikliklerin üst katmandaki uygulama programlarını etkilememesidir.

> [!IMPORTANT] Kritik Kural
> Başvuru bütünlüğü (Referential Integrity) gereği yabancı anahtar ile bağlı bir kayıt silinmeden önce bağımlı satırlar temizlenmelidir.

- **Mantıksal Veri Bağımsızlığı:** Kavramsal şema değişikliklerinden dış şemaları korur.
- **Fiziksel Veri Bağımsızlığı:** Disk ve indeks değişikliklerinden kavramsal şemayı korur.

```sql
SELECT o.ogrenciadi, COUNT(k.derskodu) AS ders_sayisi
FROM ogrenci o
JOIN kayit k ON o.ogrencino = k.ogrencino
GROUP BY o.ogrenciadi;
```

| Ders Kodu | Ders Adı | Öğrenci Sayısı |
| :--- | :--- | :--- |
| BM335 | Veritabanı Yönetim Sistemleri | 2 |
| BM315 | Programlama Dilleri | 3 |

![Üniversite ER Modeli](raporlar/ermodel.drawio.png)
````

#### MCP Aracı İle Çağrımı (`pdf_from_markdown`):
```json
{
  "output_path": "C:/path/to/Cikti_Raporu.pdf",
  "markdown_file": "C:/path/to/rapor_taslagi.md"
}
```

### Markdown Sözdizimi Eşleme Tablosu

| Markdown İfadesi | PDF Çıktısındaki Karşılığı |
| :--- | :--- |
| `--- ... ---` (YAML Frontmatter) | Kapak sayfası başlığı, alt başlığı, özet kutusu, tema ve alt bilgi metaverileri |
| `# BÖLÜM 1: ...` | Tam genişlikte renkli Bölüm Başlığı (`add_section_header`) |
| `## Soru 1: ...` veya `### ...` | Sol şeritli, gölgeli Soru-Cevap Kartı (`add_qa`) ve takip eden cevap metni |
| ` ```sql ... ``` ` | Monospace fontlu, çerçeveli Kod Bloğu (`add_code_block`) |
| `\| Sütun 1 \| Sütun 2 \|` | Zebra desenli, renkli başlıklı Tablo (`add_table`) |
| `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]` | Renkli Uyarı / Bilgi Paneli (`add_callout`) |
| `![Alt Yazı](resim/yolu.png)` | Ortalanmış, ölçeklenmiş Görsel ve İtalik Alt Yazı (`add_image`) |
| `- **Başlık:** Açıklama` | Kalın başlıklı Madde İmi (`add_bullet`) |

---

## 💻 Komut Satırı (CLI) Kullanımı (TR)

```bash
# 1. Markdown dosyasını PDF'e derle (Zümrüt Yeşili tema ile)
python pdf_mcp/cli.py from-md "notlar.md" "Cikti.pdf" --theme emerald

# 2. JSON payload dosyasından PDF üret
python pdf_mcp/cli.py generate "payload.json" "Rapor.pdf"

# 3. PDF'ten belirli sayfa aralığını oku (1-3. sayfalar)
python pdf_mcp/cli.py read "slayt.pdf" --start 1 --end 3

# 4. Klasördeki tüm PDF slaytlarında kelime ara
python pdf_mcp/cli.py search "./DersNotlari" --pattern "L*.pdf" -q "ACID"

# 5. PDF teknik bilgilerini görüntüle
python pdf_mcp/cli.py meta "dokuman.pdf"

# 6. İki PDF dosyasını karşılaştır
python pdf_mcp/cli.py diff "eski.pdf" "yeni.pdf"
```

---

## 🐍 Python API Kullanımı (TR)

```python
from pdf_mcp import build_pdf_from_markdown, PDFReportBuilder

# Yöntem 1: Doğrudan Markdown'dan PDF Üretimi
build_pdf_from_markdown(
    output_path="Hizli_Rapor.pdf",
    markdown_file="taslak.md",
    theme="navy_blue"
)

# Yöntem 2: Programatik Builder API
builder = PDFReportBuilder(header_title="Teknik Rapor", theme_name="slate")
builder.draw_cover(
    title="SİSTEM MİMARİSİ RAPORU",
    subtitle="Performans ve İndeksleme Analizi",
    category="MÜHENDİSLİK",
    description="B+ Ağacı ve Hash İndeks karşılaştırması.",
    metadata={"Yazar": "Ceyhun TUFAN", "Sürüm": "1.1.0"}
)

builder.add_page()
builder.add_section_header("1. İNDEKS KARŞILAŞTIRMASI", "Zaman Karmaşıklığı Analizi")
builder.add_table(
    headers=["İndeks Türü", "Eşitlik Arama", "Aralık Sorgusu"],
    rows=[
        ["B+ Ağacı", "O(log N)", "Destekler (Sıralı Yapraklar)"],
        ["Hash İndeks", "O(1)", "Desteklemez"]
    ]
)
builder.add_callout("Genel amaçlı sorgularda varsayılan olarak B+ Ağacı tercih edilmelidir.", kind="tip")
builder.add_image("diyagram.png", caption="Şekil 1: Sayfa İçi Yerleşim")
builder.output("Mimari_Rapor.pdf")
```

---

## 🧪 Testing / Testler

Run the unit and MCP server integration test suite / Birim ve entegrasyon testlerini çalıştırın:

```bash
python -m unittest discover -s tests -v
```

---

## 📄 License / Lisans

MIT License — see [LICENSE](LICENSE) for details.
