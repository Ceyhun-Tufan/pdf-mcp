# -*- coding: utf-8 -*-
"""Self-contained unit tests for pdf_mcp server module (MCP JSON-RPC 2.0)."""

import os
import sys
import unittest
import json

cur_dir = os.path.dirname(os.path.abspath(__file__))
pkg_dir = os.path.abspath(os.path.join(cur_dir, ".."))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

from pdf_mcp.server import MCPServer
from pdf_mcp.writer import build_pdf_from_markdown


class TestMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_pdf = os.path.join(cur_dir, "server_fixture.pdf")
        build_pdf_from_markdown(
            output_path=cls.sample_pdf,
            markdown_text="# TEST BÖLÜMÜ\n\nSunucu metadata birim testi."
        )

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.sample_pdf):
            os.remove(cls.sample_pdf)

    def setUp(self):
        self.server = MCPServer()

    def test_initialize(self):
        res = self.server.handle_initialize({})
        self.assertEqual(res["protocolVersion"], "2024-11-05")
        self.assertIn("tools", res["capabilities"])
        self.assertEqual(res["serverInfo"]["name"], "pdf-toolkit-mcp")

    def test_tools_list(self):
        res = self.server.handle_tools_list({})
        self.assertIn("tools", res)
        tool_names = [t["name"] for t in res["tools"]]
        self.assertIn("pdf_read_text", tool_names)
        self.assertIn("pdf_get_metadata", tool_names)
        self.assertIn("pdf_search_batch", tool_names)
        self.assertIn("pdf_compare_files", tool_names)
        self.assertIn("pdf_generate_report", tool_names)
        self.assertIn("pdf_from_markdown", tool_names)

    def test_tools_call_metadata(self):
        call_res = self.server.handle_tools_call({
            "name": "pdf_get_metadata",
            "arguments": {"file_path": self.sample_pdf}
        })
        self.assertFalse(call_res["isError"])
        text_content = call_res["content"][0]["text"]
        data = json.loads(text_content)
        self.assertEqual(data["file_name"], "server_fixture.pdf")
        self.assertGreater(data["total_pages"], 0)

    def test_tools_call_pdf_from_markdown(self):
        out_pdf = os.path.join(cur_dir, "server_md_test.pdf")
        md_text = "# BÖLÜM 1: MCP SERVER TESTİ\n\n## Soru 1: Markdown doğrudan PDF olur mu?\nEvet, tek çağrı ile derlenir.\n\n| Kriter | Durum |\n|---|---|\n| Hız | Yüksek |"
        call_res = self.server.handle_tools_call({
            "name": "pdf_from_markdown",
            "arguments": {
                "output_path": out_pdf,
                "markdown_text": md_text,
                "title": "MCP Markdown Testi"
            }
        })
        self.assertFalse(call_res["isError"])
        data = json.loads(call_res["content"][0]["text"])
        self.assertTrue(data["success"])
        self.assertTrue(os.path.exists(out_pdf))
        if os.path.exists(out_pdf):
            os.remove(out_pdf)


if __name__ == "__main__":
    unittest.main()
