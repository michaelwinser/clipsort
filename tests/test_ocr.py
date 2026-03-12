"""Tests for the OCR abstraction layer."""

import numpy as np
import pytest

pytesseract = pytest.importorskip("pytesseract")


class TestTesseractEngine:
    def test_recognize_text_in_synthetic_image(self):
        """TesseractEngine reads text drawn with cv2.putText."""
        import cv2

        from clipsort.ocr import TesseractEngine

        # Create a white image with black text
        img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        cv2.putText(img, "SCENE 5", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
        cv2.putText(img, "TAKE 3", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

        engine = TesseractEngine()
        results = engine.recognize(img)

        assert len(results) > 0
        full_text = " ".join(r.text for r in results).upper()
        assert "SCENE" in full_text or "5" in full_text

    def test_recognize_returns_confidence(self):
        """Each result has a non-negative confidence score."""
        import cv2

        from clipsort.ocr import TesseractEngine

        img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img, "HELLO", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 3)

        engine = TesseractEngine()
        results = engine.recognize(img)

        assert len(results) > 0
        for r in results:
            assert r.confidence >= 0

    def test_recognize_returns_bbox(self):
        """Each result has a bounding box."""
        import cv2

        from clipsort.ocr import TesseractEngine

        img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img, "TEST", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 3)

        engine = TesseractEngine()
        results = engine.recognize(img)

        assert len(results) > 0
        for r in results:
            assert r.bbox is not None
            _x, _y, w, h = r.bbox
            assert w > 0
            assert h > 0

    def test_recognize_blank_image_returns_empty(self):
        """A blank white image produces no text results."""
        from clipsort.ocr import TesseractEngine

        img = np.ones((100, 300, 3), dtype=np.uint8) * 255

        engine = TesseractEngine()
        results = engine.recognize(img)

        assert results == []

    def test_recognize_grayscale_input(self):
        """Engine handles grayscale images."""
        import cv2

        from clipsort.ocr import TesseractEngine

        img = np.ones((100, 300), dtype=np.uint8) * 255
        cv2.putText(img, "GRAY", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, 0, 3)

        engine = TesseractEngine()
        results = engine.recognize(img)

        assert len(results) > 0
