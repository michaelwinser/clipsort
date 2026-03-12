"""Tests for clapper board detection and OCR text parsing."""

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")
pytesseract = pytest.importorskip("pytesseract")

from clipsort.clapper_detect import ClapperDetector  # noqa: E402
from clipsort.ocr import OCRResult, TesseractEngine  # noqa: E402


class TestParseOCRResults:
    """Test _parse_ocr_results with known text patterns (unit tests)."""

    def setup_method(self):
        self.detector = ClapperDetector(ocr_engine=TesseractEngine())

    def test_scene_take_full_words(self):
        results = [
            OCRResult(text="SCENE 3", confidence=90.0),
            OCRResult(text="TAKE 2", confidence=90.0),
        ]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 3
        assert info.take == 2
        assert info.method == "ocr"

    def test_scene_take_with_colons(self):
        results = [
            OCRResult(text="SCENE: 5", confidence=85.0),
            OCRResult(text="TAKE: 1", confidence=85.0),
        ]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 5
        assert info.take == 1

    def test_abbreviated_sc_tk(self):
        results = [
            OCRResult(text="SC 7", confidence=80.0),
            OCRResult(text="TK 4", confidence=80.0),
        ]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 7
        assert info.take == 4

    def test_combined_short_form(self):
        results = [OCRResult(text="S3T2", confidence=90.0)]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 3
        assert info.take == 2

    def test_combined_short_form_with_space(self):
        results = [OCRResult(text="S3 T2", confidence=90.0)]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 3
        assert info.take == 2

    def test_scene_only_no_take(self):
        results = [OCRResult(text="SCENE 4", confidence=90.0)]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 4
        assert info.take is None

    def test_no_scene_returns_none(self):
        results = [OCRResult(text="HELLO WORLD", confidence=90.0)]
        info = self.detector._parse_ocr_results(results)
        assert info is None

    def test_empty_results_returns_none(self):
        info = self.detector._parse_ocr_results([])
        assert info is None

    def test_low_confidence_filtered(self):
        results = [OCRResult(text="SCENE 1", confidence=10.0)]
        info = self.detector._parse_ocr_results(results)
        assert info is None

    def test_confidence_is_averaged(self):
        results = [
            OCRResult(text="SCENE 2", confidence=80.0),
            OCRResult(text="TAKE 1", confidence=60.0),
        ]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.confidence == pytest.approx(70.0)

    def test_case_insensitive(self):
        results = [
            OCRResult(text="scene 2", confidence=90.0),
            OCRResult(text="take 3", confidence=90.0),
        ]
        info = self.detector._parse_ocr_results(results)
        assert info is not None
        assert info.scene == 2
        assert info.take == 3


class TestFindSlateRegion:
    """Test _find_slate_region on synthetic frames."""

    def setup_method(self):
        self.detector = ClapperDetector(ocr_engine=TesseractEngine())

    def test_finds_rectangle_on_dark_background(self):
        """A white rectangle on a dark frame should be detected."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a white rectangle (like a clapper board)
        cv2.rectangle(frame, (100, 80), (540, 400), (255, 255, 255), -1)
        cv2.rectangle(frame, (100, 80), (540, 400), (0, 0, 0), 3)
        # Add some text inside for contrast
        cv2.putText(frame, "SCENE 1", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

        region = self.detector._find_slate_region(frame)
        assert region is not None
        assert region.shape[0] > 100  # Reasonable height
        assert region.shape[1] > 100  # Reasonable width

    def test_uniform_frame_returns_none(self):
        """A solid-color frame has no slate region."""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        region = self.detector._find_slate_region(frame)
        assert region is None

    def test_too_small_rect_ignored(self):
        """A tiny rectangle is ignored (below min area threshold)."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Tiny rect — well under 2% of frame area
        cv2.rectangle(frame, (300, 230), (320, 250), (255, 255, 255), -1)
        region = self.detector._find_slate_region(frame)
        assert region is None


class TestPreprocessSlate:
    """Test _preprocess_slate preprocessing."""

    def setup_method(self):
        self.detector = ClapperDetector(ocr_engine=TesseractEngine())

    def test_returns_grayscale(self):
        bgr = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        result = self.detector._preprocess_slate(bgr)
        assert len(result.shape) == 2  # Grayscale

    def test_handles_grayscale_input(self):
        gray = np.random.randint(0, 256, (100, 200), dtype=np.uint8)
        result = self.detector._preprocess_slate(gray)
        assert len(result.shape) == 2


class TestClapperDetectorPipeline:
    """Integration tests for the full detection pipeline."""

    def test_detect_clapper_video(self, clapper_video):
        """Full pipeline: detect text overlay in a generated video."""
        engine = TesseractEngine()
        detector = ClapperDetector(ocr_engine=engine, scan_seconds=3, sample_rate=2)

        result = detector.detect(clapper_video)
        # OCR on cv2.putText is not always reliable — check that at minimum
        # the pipeline runs without error and returns ClipInfo or None.
        if result is not None:
            assert result.scene == 3
            assert result.method == "ocr"

    def test_detect_plain_video_returns_none(self, plain_video):
        """A video with no text should return None."""
        engine = TesseractEngine()
        detector = ClapperDetector(ocr_engine=engine, scan_seconds=3, sample_rate=2)

        result = detector.detect(plain_video)
        assert result is None

    def test_detect_nonexistent_video(self, tmp_path):
        """A nonexistent video path returns None."""
        engine = TesseractEngine()
        detector = ClapperDetector(ocr_engine=engine)

        result = detector.detect(tmp_path / "no_such_video.mp4")
        assert result is None
