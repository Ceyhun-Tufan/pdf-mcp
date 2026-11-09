# -*- coding: utf-8 -*-
"""Self-contained unit tests for pdf_mcp reader and writer modules."""

import os
import sys
import json
import unittest

cur_dir = os.path.dirname(os.path.abspath(__file__))
pkg_dir = os.path.abspath(os.path.join(cur_dir, ".."))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

from pdf_mcp.reader import extract_pdf_text, get_pdf_metadata, search_pdfs, compare_pdfs
from pdf_mcp.writer import (
    build_pdf_document,
    build_pdf_from_markdown,
    parse_markdown_to_doc_data,
)


class TestPDFReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_pdf = os.path.join(cur_dir, "fixture_sample.pdf")
        md_fixture = """---
title: Sistem Mimarisi Test Dokümanı
subtitle: Otomatik Test Verisi
category: TEST
---

# BÖLÜM 1: MİMARİ TEMELLER

## Soru 1: Mikroservis nedir?
Mikroservis mimarisi, uygulamaların bağımsız dağıtılabilir servisler halinde yapılandırıldığı sistemdir.
"""
        build_pdf_from_markdown(output_path=cls.sample_pdf, markdown_text=md_fixture)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.sample_pdf):
            os.remove(cls.sample_pdf)

    def test_metadata(self):
        meta = get_pdf_metadata(self.sample_pdf)
        self.assertIn("total_pages", meta)
        self.assertGreaterEqual(meta["total_pages"], 2)
        self.assertGreater(meta["file_size_bytes"], 0)

    def test_extract_text(self):
        res = extract_pdf_text(self.sample_pdf, start_page=1, end_page=2)
        self.assertEqual(res["extracted_page_count"], 2)
        self.assertIn("full_text", res)
        self.assertIn("Mikroservis", res["full_text"])

    def test_search(self):
        res = search_pdfs(cur_dir, pattern="fixture_*.pdf", query="Mikroservis")
        self.assertGreater(res["scanned_files_count"], 0)
        self.assertGreater(res["pages_with_matches"], 0)

    def test_compare(self):
        res = compare_pdfs(self.sample_pdf, self.sample_pdf)
        self.assertTrue(res["is_identical"])
        self.assertEqual(res["differing_pages_count"], 0)


class TestPDFWriter(unittest.TestCase):
    def test_build_report_with_rich_components(self):
        test_out = os.path.join(cur_dir, "test_output.pdf")
        data = {
            "title": "Birim Test Dokümanı",
            "subtitle": "Tablo, Callout ve Görsel Bileşen Testi",
            "category": "TEST RAPORU",
            "description": "Bu doküman test_reader_writer.py tarafından üretilmiştir.",
            "metadata": {
                "Yazar": "Test Runner",
                "Durum": "Başarılı",
                "Türkçe Test": "çğıöşü ÇĞİÖŞÜ"
            },
            "sections": [
                {
                    "title": "Bölüm 1: Zengin Bileşenler",
                    "subtitle": "Tablo, Uyarı Kutusu ve Kod Testi",
                    "items": [
                        {
                            "type": "qa",
                            "q_num": "1",
                            "question": "Test sorusu nedir?",
                            "answer": "Test sorusu birim testi için hazırlanmış örnek cevaptır."
                        },
                        {
                            "type": "bullet",
                            "title": "Madde 1",
                            "text": "Madde açıklaması metni"
                        },
                        {
                            "type": "code",
                            "code": "SELECT * FROM services WHERE active = true;"
                        },
                        {
                            "type": "table",
                            "headers": ["Sütun A", "Sütun B", "Açıklama"],
                            "rows": [
                                ["1", "SVC-01", "Kimlik Doğrulama Servisi"],
                                ["2", "SVC-02", "Ödeme Ağ Geçidi"]
                            ]
                        },
                        {
                            "type": "callout",
                            "kind": "tip",
                            "title": "PERFORMANS İPUCU",
                            "text": "Önbellek kullanımı sorgu süresini milisaniye seviyesine indirir."
                        },
                        {
                            "type": "image",
                            "image_path": "non_existent_image_for_fallback.png",
                            "caption": "Eksik görsel hata toleransı testi"
                        }
                    ]
                }
            ]
        }
        out = build_pdf_document(data, test_out)
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 1000)

        if os.path.exists(test_out):
            os.remove(test_out)

    def test_markdown_to_pdf(self):
        test_md_pdf = os.path.join(cur_dir, "test_md_output.pdf")
        md_content = """---
title: Markdown Derleyici Testi
subtitle: Otomatik AST ve PDF Üretimi
category: MÜHENDİSLİK RAPORU
theme: emerald
Yazar: Test Engineer
---

# BÖLÜM 1: TEMEL SÖZDİZİMİ

## Soru 1.1: Yük Dengeleme nedir?
Yük dengeleme, gelen ağ trafiğini birden fazla sunucuya dağıtan mekanizmadır.

> [!NOTE] Önemli Not
> Sağlık kontrolleri (health checks) başarısız olan düğümler havuzdan çıkarılır.

- **Katman 4:** Taşıma katmanı yük dengeleme.
- **Katman 7:** Uygulama katmanı yük dengeleme.

```sql
SELECT service_name, status FROM nodes WHERE healthy = true;
```

| Servis Kodu | Servis Adı | Durum |
| :--- | :--- | :--- |
| SRV-01 | API Gateway | Aktif |
| SRV-02 | Auth Service | Aktif |
"""
        parsed = parse_markdown_to_doc_data(md_content)
        self.assertEqual(parsed["title"], "Markdown Derleyici Testi")
        self.assertEqual(parsed["theme"], "emerald")
        self.assertEqual(len(parsed["sections"]), 1)

        out = build_pdf_from_markdown(output_path=test_md_pdf, markdown_text=md_content)
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 1000)

        if os.path.exists(test_md_pdf):
            os.remove(test_md_pdf)

    def test_input_file_json(self):
        temp_json = os.path.join(cur_dir, "temp_payload.json")
        test_out = os.path.join(cur_dir, "test_from_json.pdf")
        payload = {
            "title": "JSON Dosya Testi",
            "sections": [
                {
                    "title": "Bölüm 1",
                    "items": [{"type": "paragraph", "text": "Dosyadan okunan içerik."}]
                }
            ]
        }
        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        out = build_pdf_document({"input_file": temp_json}, test_out)
        self.assertTrue(os.path.exists(out))

        for p in (temp_json, test_out):
            if os.path.exists(p):
                os.remove(p)

    def test_latex_math_blocks_and_inline(self):
        test_math_pdf = os.path.join(cur_dir, "test_math_output.pdf")
        md_content = """---
title: LaTeX Matematik ve Denklem Testi
subtitle: Blok ve Satır İçi Matematik Derleme
category: MATEMATİK RAPORU
theme: navy_blue
---

# BÖLÜM 1: FORMÜLLER VE DENKLEMLER

## Soru 1: Gauss İntegrali nedir?
Gauss integrali matematikte $I = \\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$ olarak ifade edilen temel integraldir.
Ayrıca kinetik enerji formülü $E = \\frac{1}{2}mv^2$ ve kütle-enerji eşitliği $E = mc^2$ biçimindedir.

$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

```math
x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
```

> [!NOTE] Önemli Denklem Bilgisi
> Formüldeki $\\Delta = b^2 - 4ac$ değeri diskriminant olarak adlandırılır. $\\alpha \\le \\beta$ ve $\\lambda \\to 0$.
"""
        parsed = parse_markdown_to_doc_data(md_content)
        items = parsed["sections"][0]["items"]
        math_items = [it for it in items if it.get("type") == "math"]
        self.assertGreaterEqual(len(math_items), 2)
        self.assertIn(r"\int", math_items[0]["equation"])

        out = build_pdf_from_markdown(output_path=test_math_pdf, markdown_text=md_content)
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 5000)

        if os.path.exists(test_math_pdf):
            os.remove(test_math_pdf)

    def test_callout_and_qa_overflow_resilience(self):
        test_overflow_pdf = os.path.join(cur_dir, "test_overflow_output.pdf")
        long_callout = (
            "Bu çağrı kutusu özellikle metin kaydırma sınırlarını test etmek amacıyla hazırlanmıştır. "
            "Eski kaba formülde satır sayısı tahmin edilirken kelime sınırları hesaba katılmadığından "
            "metin kutunun alt sınırından dışarı taşıyor ve bir sonraki paragrafın üstüne biniyordu. "
            "Artık fpdf2 dry_run=True ile tam piksel yüksekliği ölçüldüğü için kutu tam boyutta açılmakta "
            "ve altındaki içerikle hiçbir şekilde çakışmamaktadır.\n\n"
            "İkinci paragraf: Ayrıca çoklu satırlar ve boşluklar da güvenle işlenir."
        )
        long_q = (
            "Bu çok uzun bir soru metnidir ve birden fazla satıra sarılması gerekmektedir. "
            "Soru kutularında da eski formül satır sayısını eksik tahmin ediyor ve soru kartının "
            "çerçevesi metinden daha kısa kalıyordu. Şimdi ise dinamik ölçümle tam oturmaktadır?"
        )

        data = {
            "title": "Kutu Taşma Dayanıklılık Testi",
            "description": "Uzun açıklamaların kapak kutusundan taşmadığını ve alttaki meta verilerle çakışmadığını doğrulayan açıklama metni. " * 3,
            "sections": [
                {
                    "title": "Bölüm 1: Taşma ve Sınır Kontrolleri",
                    "items": [
                        {"type": "qa", "q_num": "1", "question": long_q, "answer": "Kusursuz cevap metni."},
                        {"type": "callout", "kind": "warning", "title": "UZUN METİN TESTİ", "text": long_callout},
                        {"type": "paragraph", "text": "Bu paragraf kutunun tam altına basılmalı, kutuyla çakışmamalıdır."}
                    ]
                }
            ]
        }
        out = build_pdf_document(data, test_overflow_pdf)
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 3000)

        if os.path.exists(test_overflow_pdf):
            os.remove(test_overflow_pdf)

    def test_code_block_long_lines_and_wrapping(self):
        test_code_pdf = os.path.join(cur_dir, "test_code_output.pdf")
        long_code = (
            "SELECT id, service_name, deployment_region, cluster_ip, health_status, latency_ms, last_heartbeat "
            "FROM microservices_registry_production_eu_central_1 WHERE environment = 'production' AND status = 'healthy' "
            "ORDER BY latency_ms ASC LIMIT 100;"
        )
        data = {
            "title": "Kod Bloğu Sarma Testi",
            "sections": [
                {
                    "title": "Bölüm 1: Uzun Kod Satırları",
                    "items": [
                        {"type": "code", "code": long_code}
                    ]
                }
            ]
        }
        out = build_pdf_document(data, test_code_pdf)
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 2000)

        if os.path.exists(test_code_pdf):
            os.remove(test_code_pdf)

    def test_malformed_math_graceful_fallback(self):
        test_fallback_pdf = os.path.join(cur_dir, "test_fallback_output.pdf")
        # An equation with deliberately broken TeX that mathtext cannot parse
        broken_eq = r"\unsupportedcommand{broken}{syntax"
        data = {
            "title": "Geçersiz Matematik Hata Toleransı Testi",
            "sections": [
                {
                    "title": "Bölüm 1: Fallback Testi",
                    "items": [
                        {"type": "math", "equation": broken_eq, "caption": "Hatalı TeX Toleransı"}
                    ]
                }
            ]
        }
        out = build_pdf_document(data, test_fallback_pdf)
        self.assertTrue(os.path.exists(out))
        self.assertGreater(os.path.getsize(out), 2000)

        if os.path.exists(test_fallback_pdf):
            os.remove(test_fallback_pdf)

    def test_multipage_header_and_subheading_no_collision(self):
        from pypdf import PdfReader
        test_multi_pdf = os.path.join(cur_dir, "test_multi_collision.pdf")
        md_text = """---
title: Sayfalama ve Baslik Cakisma Testi
subtitle: Header ve Margin Guvencesi
category: TEST
---

# BOLUM 1: GIRIS

### Alt Baslik 1.1
Bu bir alt baslik ornegidir. QA karti olmamali, baslik olarak basilmalidir.

```sql
SELECT
    id, name, region, status, cpu, memory, latency, timestamp
FROM microservices_cluster_database_nodes
WHERE env = 'prod'
ORDER BY latency DESC;
```

### Alt Baslik 1.2
```sql
SELECT node_id, count(*) FROM pods GROUP BY node_id;
SELECT service_name, endpoint, port, health FROM microservices_production_registry;
```
"""
        parsed = parse_markdown_to_doc_data(md_text)
        subheads = [it for it in parsed["sections"][0]["items"] if it.get("type") == "subheading"]
        self.assertEqual(len(subheads), 2)
        self.assertEqual(subheads[0]["title"], "Alt Baslik 1.1")

        out = build_pdf_from_markdown(output_path=test_multi_pdf, markdown_text=md_text)
        self.assertTrue(os.path.exists(out))

        reader = PdfReader(test_multi_pdf)
        for p_idx, page in enumerate(reader.pages):
            p_num = p_idx + 1
            if p_num == 1:
                continue
            elements = []
            def visitor(text, cm, tm, font_dict, font_size):
                clean = text.strip()
                if clean:
                    y_mm = (841.89 - tm[5]) * 25.4 / 72.0
                    elements.append((y_mm, clean))
            page.extract_text(visitor_text=visitor)

            for y_mm, text in elements:
                # Running header must stay inside top margin (y < 20mm)
                # Body content must never overlap divider line (19mm) or invade margin (must be y >= 28mm)
                is_header = "Sayfalama" in text or "Sayfa" in text or y_mm < 20.0
                if not is_header:
                    self.assertGreaterEqual(
                        y_mm,
                        28.0,
                        f"Element '{text}' on page {p_num} placed at y={y_mm:.2f}mm which overlaps header zone!"
                    )

        if os.path.exists(test_multi_pdf):
            os.remove(test_multi_pdf)


if __name__ == "__main__":
    unittest.main()
