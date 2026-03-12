"""Tests for QR code detection."""

import json
from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")

from clipsort.parser import ClipInfo  # noqa: E402
from clipsort.qr_detect import DetectionChain, QRDetector  # noqa: E402


class TestQRDetector:
    def setup_method(self):
        self.detector = QRDetector(scan_seconds=5, sample_rate=2)

    def test_detect_qr_in_video(self, qr_video):
        result = self.detector.detect(qr_video)
        assert result is not None
        assert result.scene == 1
        assert result.take == 1
        assert result.method == "qr"

    def test_detect_no_qr_returns_none(self, plain_video):
        result = self.detector.detect(plain_video)
        assert result is None

    def test_detect_nonexistent_file(self, tmp_path):
        result = self.detector.detect(tmp_path / "nope.mp4")
        assert result is None

    def test_parse_valid_data(self):
        raw = json.dumps({"v": 1, "scene": 5, "take": 2})
        result = QRDetector._parse_qr_data(raw)
        assert result is not None
        assert result.scene == 5
        assert result.take == 2
        assert result.method == "qr"

    def test_parse_invalid_json(self):
        assert QRDetector._parse_qr_data("not json") is None

    def test_parse_wrong_version(self):
        raw = json.dumps({"v": 99, "scene": 1, "take": 1})
        assert QRDetector._parse_qr_data(raw) is None

    def test_parse_missing_fields(self):
        raw = json.dumps({"v": 1, "scene": 1})
        assert QRDetector._parse_qr_data(raw) is None

    def test_parse_not_a_dict(self):
        raw = json.dumps([1, 2, 3])
        assert QRDetector._parse_qr_data(raw) is None


class TestDetectionChain:
    def test_first_detector_wins(self):
        def d1(path):
            return ClipInfo(scene=1, take=1, method="d1")

        def d2(path):
            return ClipInfo(scene=2, take=2, method="d2")

        chain = DetectionChain([d1, d2])
        result = chain.detect(Path("test.mp4"))
        assert result is not None
        assert result.method == "d1"

    def test_fallback_to_second(self):
        def d1(path):
            return None

        def d2(path):
            return ClipInfo(scene=3, take=1, method="d2")

        chain = DetectionChain([d1, d2])
        result = chain.detect(Path("test.mp4"))
        assert result is not None
        assert result.method == "d2"

    def test_all_fail_returns_none(self):
        def d1(path):
            return None

        def d2(path):
            return None

        chain = DetectionChain([d1, d2])
        result = chain.detect(Path("test.mp4"))
        assert result is None
