# PDF-MCP (v1.2.0): Model Context Protocol (MCP) Server & CLI Toolkit

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![Version 1.2.0](https://img.shields.io/badge/version-1.2.0-emerald.svg)]()

### 🌐 [**🇬🇧 English Documentation**](#english-documentation) &nbsp;|&nbsp; [**🇹🇷 Türkçe Dokümantasyon**](#turkce-dokumantasyon)

</div>

---

<a id="english-documentation"></a>

# 🇬🇧 English Documentation

**PDF-MCP** is a lightweight, high-performance **Model Context Protocol (MCP)** server and command-line (CLI) toolkit designed for AI coding assistants (**Google Antigravity**, **Claude Desktop**, **Cursor**) and developers.

It empowers AI agents to natively inspect, batch-search, and diff PDF documents, as well as compile **publication-grade A4 PDF reports directly from Markdown (`.md`) or structured JSON**—complete with cover pages, Q&A cards, LaTeX mathematical equations, code blocks, zebra-striped tables, callout alerts, embedded diagrams, and full UTF-8/Unicode typography support—without writing intermediate dump scripts.

---

## 🆕 What's New in v1.2.0

- **📐 Native LaTeX Math & Equation Rendering (`math`)**: High-resolution 300 DPI mathematical typography rendered via `matplotlib.mathtext` without requiring external TeX distributions (TeX Live/MiKTeX). Supports block formulas (`$$...$$`, `\[...\]`, ```` ```math ````) into styled cards with labels/captions, plus automatic inline math conversion (`$E=mc^2$`, `\alpha`, `\sum`, `\int`, `\frac{a}{b}`) into clean Unicode typography.
- **🛡️ Bulletproof Box Overflow & Overlap Prevention**: Replaced naive line estimation with exact dynamic measurement (`multi_cell(..., dry_run=True, output=MethodReturnValue.HEIGHT)`). Callouts, Q&A cards, and cover descriptions dynamically expand to fit text perfectly, eliminating content truncation and text collisions.
- **📜 Smart Code Block Wrapping & Pagination**: Long code lines soft-wrap cleanly with indentation without clipping margins; multi-page code blocks gracefully split across page boundaries with individual boxed containers.
- **📝 Markdown-First PDF Compiler (`pdf_from_markdown`)**: Pass a standard Markdown file or string; the engine automatically compiles YAML frontmatter, `#` sections, `##` Q&A cards, LaTeX equations, fenced code blocks, Markdown tables, `> [!NOTE]` callouts, and `![caption](img)` figures into a styled PDF.
- **📊 Native Styled Table Engine (`table`)**: Automatic column sizing, primary-colored headers, and alternating row backgrounds (zebra striping).
- **💡 Rich Alert / Callout Boxes (`callout`)**: Left-accented callout panels for `NOTE`, `TIP`, `WARNING`, `IMPORTANT`, and `CAUTION`.
- **🖼️ Smart Image & Diagram Embedding (`image`)**: Aspect-ratio preserving centered image rendering with italic captions and graceful fallback placeholders if an image path is missing.
- **📂 Direct File Input (`input_file`)**: Pass a disk path (`.md` or `.json`) to `pdf_generate_report` instead of serializing 100KB+ payloads into the LLM context window.

---

## ✨ Core Tools & Capabilities

| Tool Name | Description |
| :--- | :--- |
| **`pdf_from_markdown`** | Compiles a `.md` file or raw Markdown string directly into a publication-grade styled PDF report with LaTeX math support. |
| **`pdf_generate_report`** | Builds a styled PDF from structured JSON data or an external `input_file` (`qa`, `math`, `table`, `callout`, `image`, `code`, `bullet`). |
| **`pdf_read_text`** | Extracts clean text from an entire PDF or specific page ranges (`start_page` - `end_page`, 1-based). |
| **`pdf_search_batch`** | Rapidly searches across dozens of PDFs in a directory (`*.pdf`, `report_*.pdf`) using keywords or regular expressions. |
| **`pdf_get_metadata`** | Retrieves total page count, file size, title, author, and encryption status. |
| **`pdf_compare_files`** | Compares two PDF files page-by-page to pinpoint textual differences. |
| **Full Unicode & Math** | Native TrueType font support (`Arial`, `Calibri`, `Segoe UI`, `Consolas`, `DejaVu`) for international characters, Turkish (`ç, ğ, ı, ö, ş, ü, İ, Ğ, Ş`), and mathematical symbols. |

---

## 🚀 Quick Start & Installation (EN)

### 1. Install Dependencies

PDF-MCP requires lightweight, zero-system-overhead Python packages (`pypdf`, `fpdf2`, `matplotlib`):

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

## ⚡ Instant Usage Guide (Markdown → PDF)

### Scenario: Compile Markdown to PDF in One Step (Recommended)

Create a `.md` file with optional YAML frontmatter to configure the cover page and theme (`navy_blue`, `emerald`, `slate`):

````markdown
---
title: CLOUD INFRASTRUCTURE AUDIT REPORT
subtitle: Q4 Security, Latency & Scalability Review
category: TECHNICAL REPORT
description: Comprehensive architectural evaluation of distributed API services and storage layers.
theme: navy_blue
Prepared By: Platform Engineering Team
Author: Alex Rivera
Date: 2026
---

# SECTION 1: SERVICE ARCHITECTURE & LATENCY

## Question 1.1: How does edge caching impact P99 response times?
Deploying regional edge caches reduces round-trip latency by serving static and pre-computed payloads directly from points of presence closest to the client.

> [!IMPORTANT] Rate Limiting Policy
> All public endpoints must enforce token-bucket rate limiting at the API Gateway layer prior to production rollout.

- **Edge Gateway:** Handles TLS termination and request routing.
- **Worker Pool:** Processes asynchronous background jobs with automatic retry policies.

```sql
SELECT service_name, AVG(latency_ms) AS avg_latency
FROM telemetry_logs
WHERE status_code = 200
GROUP BY service_name;
```

| Service ID | Component Name | Uptime SLA |
| :--- | :--- | :--- |
| SVC-101 | Auth Gateway | 99.99% |
| SVC-204 | Billing Engine | 99.95% |

![System Topology Diagram](assets/topology.png)
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
| `### Subheading` | Clean bold Subheading (`add_subheading`) |
| `## Question 1: ...` or `### Question 1: ...` | Left-accented shaded Q&A Card (`add_qa`) + subsequent paragraph as answer |
| `$$ ... $$` or `\[ ... \]` or ```` ```math ```` | Standalone high-res LaTeX Mathematical Equation Card (`add_math`) with optional numbering |
| `$E = mc^2$` or `\(...\)` | In-line smooth Unicode mathematical typography (Greek letters, symbols, roots, fractions) |
| ```` ```sql ... ``` ```` | Shaded monospace Code Block with long-line soft-wrap (`add_code_block`) |
| `&#124; Col 1 &#124; Col 2 &#124;` | Zebra-striped Table with primary-colored header (`add_table`) |
| `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]` | Dynamic-height Styled Callout / Alert Box without overflow (`add_callout`) |
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
python pdf_mcp/cli.py read "manual.pdf" --start 1 --end 3

# 4. Batch-search across all PDFs in a folder
python pdf_mcp/cli.py search "./docs" --pattern "*.pdf" -q "latency"

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
    subtitle="Performance & Throughput Benchmarks",
    category="ENGINEERING",
    description="Comparative analysis of distributed caching and message queue throughput.",
    metadata={"Author": "Alex Rivera", "Version": "1.1.0"}
)

builder.add_page()
builder.add_section_header("1. BENCHMARK SUMMARY", "Throughput Under Load")
builder.add_math(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}", caption="Gaussian Integral", label="1.1")
builder.add_table(
    headers=["Engine", "Read Latency", "Write Throughput"],
    rows=[
        ["In-Memory Cache", "0.4 ms", "120,000 ops/sec"],
        ["Distributed Store", "2.1 ms", "45,000 ops/sec"]
    ]
)
builder.add_callout("Enable connection pooling to prevent socket exhaustion under peak load.", kind="tip")
builder.add_image("diagram.png", caption="Figure 1: Cluster Replication Flow")
builder.output("Architecture_Report.pdf")
```

---

<a id="turkce-dokumantasyon"></a>

# 🇹🇷 Türkçe Dokümantasyon

<div align="right">
  <a href="#english-documentation">⬆️ Go to English Documentation</a>
</div>

**PDF-MCP**, yapay zeka kodlama asistanları (**Google Antigravity**, **Claude Desktop**, **Cursor**) ve geliştiriciler için tasarlanmış hafif, yüksek performanslı bir **Model Context Protocol (MCP)** sunucusu ve komut satırı (CLI) araç setidir.

Ajanların PDF belgelerini okumasına, onlarca doküman içinde toplu arama yapmasına, iki PDF'i karşılaştırmasına ve **hiçbir ara JSON dönüştürücü script yazmaya gerek kalmadan doğrudan Markdown (`.md`) veya JSON üzerinden yayın kalitesinde A4 PDF raporlar** üretmesine olanak tanır.

---

## 🆕 v1.2.0 ile Gelen Yenilikler

- **📐 Yerleşik LaTeX Matematik ve Denklem Motoru (`math`)**: Harici bir TeX dağıtımına (TeX Live/MiKTeX) ihtiyaç duymadan `matplotlib.mathtext` ile 300 DPI çözünürlükte matematiksel formül render desteği. Blok denklemleri (`$$...$$`, `\[...\]`, ```` ```math ````) şık denklem kartlarına çevirir; satır içi matematik ifadelerini (`$E=mc^2$`, `\alpha`, `\sum`, `\int`, `\frac{a}{b}`) pürüzsüz Unicode karakterlere dönüştürür.
- **🛡️ Kutu Taşma ve Üst Üste Binme (Overlap) Çözümü**: Kaba satır tahminleri kaldırılarak `fpdf2`'nin `multi_cell(..., dry_run=True, output=MethodReturnValue.HEIGHT)` özelliğiyle piksel hassasiyetinde dinamik yükseklik ölçümüne geçildi. Çağrı kutuları (callout), soru-cevap kartları ve kapak özetleri metnin gerçek boyutuna göre esner; metin taşması veya bir sonraki paragrafın üstüne binme sorunları tamamen ortadan kaldırıldı.
- **📜 Kod Bloklarında Akıllı Satır Kaydırma ve Sayfalama**: 162 mm'yi aşan uzun kod satırları marjinden taşmayacak şekilde girintili olarak yumuşak sarılır (soft-wrap); sayfaları aşan kod blokları sayfa kırılımlarında parçalı çerçevelerle bölünür.
- **📝 Markdown-First PDF Derleyici (`pdf_from_markdown`)**: Ajan veya kullanıcı standart bir Markdown metni/dosyası verir; sistem otomatik olarak kapak sayfası, bölüm başlıkları, soru-cevap kartları, LaTeX denklemleri, kod blokları, tablolar, uyarı kutuları ve görseller içeren şık bir PDF üretir.
- **📊 Yerleşik Stilize Tablo Motoru (`table`)**: Tema renkli başlık satırı, zebra desenli (alternatif satır dolgulu) ve otomatik metin kaydırmalı tablolar.
- **💡 Renkli Uyarı / Bilgi Panelleri (`callout`)**: `NOTE`, `TIP`, `WARNING`, `IMPORTANT`, `CAUTION` tiplerinde sol kenarı renk şeritli vurgu kutuları.
- **🖼️ Akıllı Görsel ve Diyagram Gömme (`image`)**: En-boy oranını (aspect ratio) koruyarak ortalanmış resim/diyagram ekleme, alt yazı (`caption`) desteği ve eksik görsellerde çökmeyi önleyen hata toleranslı yer tutucu (fallback).
- **📂 Dosya Yolu Desteği (`input_file`)**: Büyük raporlarda 100 KB+ veriyi sohbet bağlamına (context) basmak yerine doğrudan diskteki `.md` veya `.json` dosya yolunu vererek tek adımda derleme.

---

## ✨ Temel Özellikler

| Özellik / Araç | Açıklama |
| :--- | :--- |
| **`pdf_from_markdown`** | `.md` dosyasını veya ham Markdown metnini LaTeX matematik desteğiyle doğrudan yayın kalitesinde PDF raporuna derler. |
| **`pdf_generate_report`** | Yapılandırılmış JSON verisinden veya harici `input_file` dosyasından (`qa`, `math`, `table`, `callout`, `image`, `code`, `bullet`) PDF üretir. |
| **`pdf_read_text`** | Tam belgeyi veya belirli sayfa aralıklarını (`start_page` - `end_page`) temiz metin olarak çıkarır. |
| **`pdf_search_batch`** | Bir klasördeki onlarca PDF içinde (`*.pdf`, `rapor_*.pdf`) anahtar kelime veya Regex araması yapar. |
| **`pdf_get_metadata`** | Sayfa sayısı, dosya boyutu, başlık, yazar ve şifreleme durumunu döndürür. |
| **`pdf_compare_files`** | İki PDF dosyasını sayfa sayfa karşılaştırarak metin farklarını tespit eder. |
| **Tam Türkçe ve Matematik** | `Arial`, `Calibri`, `Segoe UI`, `Consolas` ve `DejaVu` TrueType fontlarıyla `ç, ğ, ı, ö, ş, ü, İ, Ğ, Ş` karakterlerini ve zengin matematik sembollerini kusursuz işler. |

---

## 🚀 Hızlı Kurulum (TR)

### 1. Gereksinimlerin Kurulması

Proje hafif ve sistem bağımsız kütüphanelere (`pypdf`, `fpdf2`, `matplotlib`) ihtiyaç duyar:

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

## ⚡ Anlık Kullanım Rehberi (Markdown → PDF)

### Senaryo: Markdown Dosyasından Tek Adımda PDF Üretimi (Tavsiye Edilen)

Herhangi bir `.md` dosyası oluşturun. YAML başlığı (frontmatter) ile kapak bilgilerini ve temayı (`navy_blue`, `emerald`, `slate`) belirleyebilirsiniz:

````markdown
---
title: BULUT ALTYAPI VE PERFORMANS RAPORU
subtitle: 4. Çeyrek Güvenlik, Gecikme ve Ölçeklenebilirlik Analizi
category: TEKNİK RAPOR
description: Dağıtık mikroservislerin ve depolama katmanlarının kapsamlı mimari değerlendirmesi.
theme: navy_blue
Birim: Platform Mühendisliği Ekibi
Hazırlayan: Deniz Yılmaz
Tarih: 2026
---

# BÖLÜM 1: SERVİS MİMARİSİ VE GECİKME ANALİZİ

## Soru 1.1: Uç önbellekleme (Edge Caching) yanıt sürelerini nasıl etkiler?
Bölgesel önbellek sunucuları, statik ve sık erişilen verileri istemciye en yakın noktadan sunarak ağ gecikmesini minimuma indirir.

> [!IMPORTANT] Hız Sınırlandırma (Rate Limiting) Kuralı
> Tüm dışa açık API uç noktalarında üretim ortamına geçilmeden önce API Gateway katmanında istek sınırlandırma aktif edilmelidir.

- **API Geçidi:** TLS sonlandırma ve yük dengeleme işlemlerini yürütür.
- **İşçi Havuzu (Worker Pool):** Asenkron arka plan görevlerini otomatik yeniden deneme mekanizmasıyla işler.

```sql
SELECT servis_adi, AVG(gecikme_ms) AS ortalama_gecikme
FROM sistem_kayitlari
WHERE durum_kodu = 200
GROUP BY servis_adi;
```

| Servis Kodu | Bileşen Adı | Çalışma Süresi (SLA) |
| :--- | :--- | :--- |
| SRV-101 | Kimlik Doğrulama Geçidi | 99.99% |
| SRV-204 | Ödeme Motoru | 99.95% |

![Sistem Topoloji Diyagramı](assets/topoloji.png)
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
| `### Alt Başlık` | Vurgulu, temiz Alt Başlık (`add_subheading`) |
| `## Soru 1: ...` veya `### Soru 1: ...` | Sol şeritli, gölgeli Soru-Cevap Kartı (`add_qa`) ve takip eden cevap metni |
| `$$ ... $$` veya `\[ ... \]` veya ```` ```math ```` | Yüksek çözünürlüklü LaTeX Matematik Denklem Kartı (`add_math`) |
| `$E = mc^2$` veya `\(...\)` | Paragraf içi pürüzsüz Unicode matematik tipografisi (Yunan harfleri, semboller, kesirler) |
| ```` ```sql ... ``` ```` | Monospace fontlu, uzun satır kaydırmalı (soft-wrap) Kod Bloğu (`add_code_block`) |
| `&#124; Sütun 1 &#124; Sütun 2 &#124;` | Zebra desenli, renkli başlıklı Tablo (`add_table`) |
| `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]` | Dinamik yükseklikli, taşma korumalı Renkli Uyarı / Bilgi Paneli (`add_callout`) |
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
python pdf_mcp/cli.py read "kilavuz.pdf" --start 1 --end 3

# 4. Klasördeki tüm PDF belgelerinde kelime ara
python pdf_mcp/cli.py search "./Belgeler" --pattern "*.pdf" -q "performans"

# 5. PDF teknik bilgilerini görüntüle
python pdf_mcp/cli.py meta "dokuman.pdf"

# 6. İki PDF dosyasını karşılaştır
python pdf_mcp/cli.py diff "v1.pdf" "v2.pdf"
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
    subtitle="Performans ve Yük Testi Analizi",
    category="MÜHENDİSLİK",
    description="Dağıtık önbellek ve mesaj kuyruğu sistemlerinin karşılaştırmalı analizi.",
    metadata={"Hazırlayan": "Deniz Yılmaz", "Sürüm": "1.1.0"}
)

builder.add_page()
builder.add_section_header("1. PERFORMANS ÖZETİ", "Yük Altında Tepki Süreleri")
builder.add_math(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}", caption="Gauss İntegrali", label="1.1")
builder.add_table(
    headers=["Motor Türü", "Okuma Gecikmesi", "Yazma Kapasitesi"],
    rows=[
        ["Bellek İçi Önbellek", "0.4 ms", "120,000 işlem/sn"],
        ["Dağıtık Depolama", "2.1 ms", "45,000 işlem/sn"]
    ]
)
builder.add_callout("Yoğun trafik altında soket tükenmesini önlemek için bağlantı havuzu (connection pool) kullanılmalıdır.", kind="tip")
builder.add_image("diyagram.png", caption="Şekil 1: Küme Replikasyon Akışı")
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
