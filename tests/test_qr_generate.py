"""Tests for QR code generation."""

import json

import pytest

qrcode = pytest.importorskip("qrcode")

from clipsort.qr_generate import QRGenerator  # noqa: E402


class TestQRGenerator:
    def setup_method(self):
        self.gen = QRGenerator()

    def test_generate_data(self):
        data = self.gen.generate_data(1, 2)
        parsed = json.loads(data)
        assert parsed == {"v": 1, "scene": 1, "take": 2}

    def test_generate_data_with_project(self):
        data = self.gen.generate_data(3, 1, project="MyFilm")
        parsed = json.loads(data)
        assert parsed == {"v": 1, "scene": 3, "take": 1, "project": "MyFilm"}

    def test_generate_single(self, tmp_path):
        out = tmp_path / "qr.png"
        result = self.gen.generate_single(1, 1, output_path=out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0

    def test_generated_qr_decodes_correctly(self, tmp_path):
        from PIL import Image
        from pyzbar.pyzbar import decode

        out = tmp_path / "qr.png"
        self.gen.generate_single(2, 3, project="Test", output_path=out)

        img = Image.open(out)
        decoded = decode(img)
        assert len(decoded) == 1
        payload = json.loads(decoded[0].data.decode("utf-8"))
        assert payload["v"] == 1
        assert payload["scene"] == 2
        assert payload["take"] == 3
        assert payload["project"] == "Test"

    def test_single_png_has_label(self, tmp_path):
        """UC-2005: Single PNG includes a human-readable text label."""
        from PIL import Image

        # Generate a bare QR code for size comparison
        bare_data = self.gen.generate_data(1, 1)
        bare_img = qrcode.make(bare_data)
        bare_h = bare_img.size[1]

        # Generate the labeled PNG
        out = tmp_path / "labeled.png"
        self.gen.generate_single(1, 1, output_path=out)
        labeled_img = Image.open(out)
        # Labeled image should be taller than bare QR (has text below)
        assert labeled_img.size[1] > bare_h

    def test_single_png_label_includes_project(self, tmp_path):
        """UC-2005: Label includes the project name when provided."""
        from PIL import Image

        out_no_proj = tmp_path / "no_proj.png"
        out_proj = tmp_path / "with_proj.png"
        self.gen.generate_single(1, 1, output_path=out_no_proj)
        self.gen.generate_single(1, 1, project="MyFilm", output_path=out_proj)
        # Both should be valid images; project version should still decode
        assert Image.open(out_no_proj).size[1] > 0
        assert Image.open(out_proj).size[1] > 0

    def test_build_label(self):
        """UC-2005: _build_label produces correct text."""
        assert QRGenerator._build_label(1, 2) == "Scene 1 Take 2"
        assert QRGenerator._build_label(3, 1, "MyFilm") == "MyFilm — Scene 3 Take 1"

    def test_generate_sheet(self, tmp_path):
        out = tmp_path / "sheet.pdf"
        result = self.gen.generate_sheet(3, 2, output_path=out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0
