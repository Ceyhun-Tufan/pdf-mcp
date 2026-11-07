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


if __name__ == "__main__":
    unittest.main()
