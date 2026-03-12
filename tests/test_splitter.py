"""Tests for the video splitter module."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from clipsort.parser import ClipInfo
from clipsort.splitter import Segment, SplitPoint, SplitScanner, VideoSplitter

# ---------------------------------------------------------------------------
# TestSplitScanner
# ---------------------------------------------------------------------------


class TestSplitScanner:
    def test_scan_with_mock_detectors(self, make_test_video):
        """Scanner finds markers via frame detectors."""
        video = make_test_video("scan_test.mp4", seconds=3, fps=5)
        call_count = 0

        def mock_detector(frame):
            nonlocal call_count
            call_count += 1
            # "Detect" on the very first call only
            if call_count == 1:
                return ClipInfo(scene=1, take=1, method="mock")
            return None

        scanner = SplitScanner(frame_detectors=[mock_detector], sample_rate=1.0)
        points = scanner.scan(video)

        assert len(points) == 1
        assert points[0].clip_info.scene == 1

    def test_scan_deduplication(self, make_test_video):
        """Nearby detections of the same scene are deduplicated."""
        video = make_test_video("dedup_test.mp4", seconds=4, fps=5)

        # Always return scene 1 — should be deduplicated within the window
        def always_detect(frame):
            return ClipInfo(scene=1, take=1, method="mock")

        scanner = SplitScanner(
            frame_detectors=[always_detect],
            sample_rate=1.0,
            dedup_window=5.0,
        )
        points = scanner.scan(video)

        assert len(points) == 1

    def test_scan_different_scenes_not_deduped(self, make_test_video):
        """Different scenes within the dedup window are NOT deduplicated."""
        video = make_test_video("multi_scene_dedup.mp4", seconds=4, fps=5)
        call_count = 0

        def alternating_detector(frame):
            nonlocal call_count
            call_count += 1
            # Scene 1 on first call, scene 2 on second
            if call_count == 1:
                return ClipInfo(scene=1, take=1, method="mock")
            if call_count == 2:
                return ClipInfo(scene=2, take=1, method="mock")
            return None

        scanner = SplitScanner(
            frame_detectors=[alternating_detector],
            sample_rate=1.0,
            dedup_window=5.0,
        )
        points = scanner.scan(video)

        assert len(points) == 2
        assert points[0].clip_info.scene == 1
        assert points[1].clip_info.scene == 2

    def test_scan_empty_video(self, make_test_video):
        """Scanner returns empty list when no detections are made."""
        video = make_test_video("empty_scan.mp4", seconds=1, fps=5)

        def no_detect(frame):
            return None

        scanner = SplitScanner(frame_detectors=[no_detect])
        points = scanner.scan(video)
        assert points == []

    def test_scan_unreadable_file(self, tmp_path):
        """Scanner returns empty list for an unreadable file."""
        bad_file = tmp_path / "bad.mp4"
        bad_file.write_bytes(b"\x00" * 100)

        def no_detect(frame):
            return None

        scanner = SplitScanner(frame_detectors=[no_detect])
        points = scanner.scan(bad_file)
        assert points == []

    def test_scan_first_detector_wins(self, make_test_video):
        """First detector that returns a result is used; second is not called."""
        video = make_test_video("priority_test.mp4", seconds=1, fps=5)
        second_called = False

        def first_detector(frame):
            return ClipInfo(scene=1, take=1, method="first")

        def second_detector(frame):
            nonlocal second_called
            second_called = True
            return ClipInfo(scene=2, take=1, method="second")

        scanner = SplitScanner(
            frame_detectors=[first_detector, second_detector],
            sample_rate=1.0,
        )
        points = scanner.scan(video)

        assert len(points) == 1
        assert points[0].clip_info.method == "first"
        assert not second_called


# ---------------------------------------------------------------------------
# TestComputeSegments
# ---------------------------------------------------------------------------


class TestComputeSegments:
    def setup_method(self):
        self.splitter = VideoSplitter()

    def test_single_split_point(self):
        """One split point produces preamble + one scene segment."""
        points = [SplitPoint(timestamp=5.0, clip_info=ClipInfo(scene=1, take=1))]
        segments = self.splitter.compute_segments(points, duration=20.0)

        assert len(segments) == 2
        # Preamble
        assert segments[0].clip_info is None
        assert segments[0].start == 0
        assert segments[0].end == 5.0
        # Scene
        assert segments[1].clip_info.scene == 1
        assert segments[1].start == 5.5  # 5.0 + 0.5 slate buffer
        assert segments[1].end is None

    def test_multiple_split_points(self):
        """Multiple split points produce correct segments."""
        points = [
            SplitPoint(timestamp=0.0, clip_info=ClipInfo(scene=1, take=1)),
            SplitPoint(timestamp=7.0, clip_info=ClipInfo(scene=2, take=1)),
            SplitPoint(timestamp=14.0, clip_info=ClipInfo(scene=3, take=1)),
        ]
        segments = self.splitter.compute_segments(points, duration=20.0)

        # No preamble (first detection at 0.0), 3 scene segments
        assert len(segments) == 3
        assert segments[0].clip_info.scene == 1
        assert segments[0].start == 0.5
        assert segments[0].end == 7.0
        assert segments[1].clip_info.scene == 2
        assert segments[1].start == 7.5
        assert segments[1].end == 14.0
        assert segments[2].clip_info.scene == 3
        assert segments[2].start == 14.5
        assert segments[2].end is None

    def test_skip_preamble(self):
        """Preamble is omitted when skip_preamble=True."""
        points = [SplitPoint(timestamp=5.0, clip_info=ClipInfo(scene=1, take=1))]
        segments = self.splitter.compute_segments(
            points, duration=20.0, skip_preamble=True
        )

        assert len(segments) == 1
        assert segments[0].clip_info.scene == 1

    def test_custom_slate_buffer(self):
        """Custom slate buffer adjusts segment start times."""
        points = [SplitPoint(timestamp=5.0, clip_info=ClipInfo(scene=1, take=1))]
        segments = self.splitter.compute_segments(
            points, duration=20.0, slate_buffer=1.0
        )

        assert segments[1].start == 6.0  # 5.0 + 1.0

    def test_zero_slate_buffer(self):
        """Zero slate buffer means segments start at the detection time."""
        points = [SplitPoint(timestamp=5.0, clip_info=ClipInfo(scene=1, take=1))]
        segments = self.splitter.compute_segments(
            points, duration=20.0, slate_buffer=0.0
        )

        assert segments[1].start == 5.0

    def test_empty_split_points(self):
        """Empty input returns empty output."""
        segments = self.splitter.compute_segments([], duration=20.0)
        assert segments == []

    def test_preamble_at_start(self):
        """No preamble when first detection is at timestamp 0."""
        points = [SplitPoint(timestamp=0.0, clip_info=ClipInfo(scene=1, take=1))]
        segments = self.splitter.compute_segments(points, duration=20.0)

        assert len(segments) == 1
        assert segments[0].clip_info.scene == 1


# ---------------------------------------------------------------------------
# TestSegmentFilename
# ---------------------------------------------------------------------------


class TestSegmentFilename:
    def test_scene_and_take(self):
        seg = Segment(start=0, end=10, clip_info=ClipInfo(scene=1, take=2), index=0)
        assert VideoSplitter._segment_filename(seg, ".mp4") == "scene_01_take_02.mp4"

    def test_scene_only(self):
        seg = Segment(start=0, end=10, clip_info=ClipInfo(scene=5, take=None), index=0)
        assert VideoSplitter._segment_filename(seg, ".mp4") == "scene_05.mp4"

    def test_preamble(self):
        seg = Segment(start=0, end=5, clip_info=None, index=0)
        assert VideoSplitter._segment_filename(seg, ".mp4") == "preamble.mp4"

    def test_no_clip_info_not_preamble(self):
        seg = Segment(start=10, end=20, clip_info=None, index=3)
        assert VideoSplitter._segment_filename(seg, ".mp4") == "segment_003.mp4"

    def test_letter_take(self):
        seg = Segment(start=0, end=10, clip_info=ClipInfo(scene=1, take="a"), index=0)
        assert VideoSplitter._segment_filename(seg, ".mp4") == "scene_01_take_a.mp4"

    def test_mov_extension(self):
        seg = Segment(start=0, end=10, clip_info=ClipInfo(scene=2, take=1), index=0)
        assert VideoSplitter._segment_filename(seg, ".mov") == "scene_02_take_01.mov"


# ---------------------------------------------------------------------------
# TestVideoSplitter
# ---------------------------------------------------------------------------


class TestVideoSplitter:
    def test_check_ffmpeg_available(self):
        """check_ffmpeg passes when ffmpeg and ffprobe are on PATH."""
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            VideoSplitter.check_ffmpeg()  # Should not raise

    def test_check_ffmpeg_missing(self):
        """check_ffmpeg raises RuntimeError when ffmpeg is missing."""
        with (
            patch("shutil.which", return_value=None),
            pytest.raises(RuntimeError, match="ffmpeg not found"),
        ):
            VideoSplitter.check_ffmpeg()

    def test_check_ffprobe_missing(self):
        """check_ffmpeg raises RuntimeError when ffprobe is missing."""
        def side_effect(name):
            return "/usr/bin/ffmpeg" if name == "ffmpeg" else None

        with (
            patch("shutil.which", side_effect=side_effect),
            pytest.raises(RuntimeError, match="ffprobe not found"),
        ):
            VideoSplitter.check_ffmpeg()

    def test_get_video_duration(self, make_test_video):
        """get_video_duration returns a reasonable duration for a test video."""
        pytest.importorskip("cv2")
        import shutil

        if shutil.which("ffprobe") is None:
            pytest.skip("ffprobe not available")

        video = make_test_video("duration_test.mp4", seconds=3, fps=5)
        duration = VideoSplitter.get_video_duration(video)
        # Allow some tolerance for container overhead
        assert 2.0 <= duration <= 4.0


# ---------------------------------------------------------------------------
# TestSplit (end-to-end, requires FFmpeg)
# ---------------------------------------------------------------------------


class TestSplit:
    @pytest.fixture(autouse=True)
    def _require_ffmpeg(self):
        import shutil

        if shutil.which("ffmpeg") is None:
            pytest.skip("ffmpeg not available")

    def test_split_single_segment(self, make_test_video, tmp_path):
        """Splitting a video with one segment produces one output file."""
        pytest.importorskip("cv2")
        video = make_test_video("split_single.mp4", seconds=5, fps=5)
        output_dir = tmp_path / "output"

        segment = Segment(
            start=1.0, end=3.0, clip_info=ClipInfo(scene=1, take=1), index=0
        )
        splitter = VideoSplitter()
        paths = splitter.split(video, output_dir, [segment])

        assert len(paths) == 1
        assert paths[0].exists()
        assert paths[0].name == "scene_01_take_01.mp4"

    def test_split_multiple_segments(self, make_test_video, tmp_path):
        """Splitting with multiple segments produces correct output files."""
        pytest.importorskip("cv2")
        video = make_test_video("split_multi.mp4", seconds=10, fps=5)
        output_dir = tmp_path / "output"

        segments = [
            Segment(start=0, end=3.0, clip_info=None, index=0),  # preamble
            Segment(start=3.5, end=7.0, clip_info=ClipInfo(scene=1, take=1), index=1),
            Segment(start=7.5, end=None, clip_info=ClipInfo(scene=2, take=1), index=2),
        ]
        splitter = VideoSplitter()
        paths = splitter.split(video, output_dir, segments)

        assert len(paths) == 3
        assert paths[0].name == "preamble.mp4"
        assert paths[1].name == "scene_01_take_01.mp4"
        assert paths[2].name == "scene_02_take_01.mp4"
        for p in paths:
            assert p.exists()

    def test_split_precise_mode(self, make_test_video, tmp_path):
        """Precise mode re-encodes and produces output files."""
        pytest.importorskip("cv2")
        video = make_test_video("split_precise.mp4", seconds=5, fps=5)
        output_dir = tmp_path / "output"

        segment = Segment(
            start=1.0, end=3.0, clip_info=ClipInfo(scene=1, take=1), index=0
        )
        splitter = VideoSplitter(precise=True)
        paths = splitter.split(video, output_dir, [segment])

        assert len(paths) == 1
        assert paths[0].exists()

    def test_split_to_end_of_video(self, make_test_video, tmp_path):
        """Segment with end=None extracts to the end of the video."""
        pytest.importorskip("cv2")
        video = make_test_video("split_end.mp4", seconds=5, fps=5)
        output_dir = tmp_path / "output"

        segment = Segment(
            start=2.0, end=None, clip_info=ClipInfo(scene=1, take=1), index=0
        )
        splitter = VideoSplitter()
        paths = splitter.split(video, output_dir, [segment])

        assert len(paths) == 1
        assert paths[0].exists()

    def test_end_to_end_scan_and_split_qr(self, make_multi_scene_video, tmp_path):
        """Full pipeline with QR markers: scan, compute segments, split."""
        pytest.importorskip("cv2")
        pytest.importorskip("qrcode")
        pytest.importorskip("pyzbar")
        from clipsort.qr_detect import QRDetector

        video_path, _scenes = make_multi_scene_video("e2e_split_qr.mp4")

        qr_detector = QRDetector()
        scanner = SplitScanner(
            frame_detectors=[qr_detector.detect_frame],
            sample_rate=1.0,
        )
        points = scanner.scan(video_path)

        # Should find at least some of the scene markers
        assert len(points) >= 1

        duration = VideoSplitter.get_video_duration(video_path)
        splitter = VideoSplitter()
        segments = splitter.compute_segments(points, duration)

        output_dir = tmp_path / "split_output"
        paths = splitter.split(video_path, output_dir, segments)

        assert len(paths) == len(segments)
        for p in paths:
            assert p.exists()
            assert p.stat().st_size > 0

    def test_end_to_end_scan_and_split_ocr(self, make_multi_scene_video, tmp_path):
        """Full pipeline with clapper text markers: scan, compute segments, split."""
        pytest.importorskip("cv2")
        pytest.importorskip("pytesseract")
        from clipsort.clapper_detect import ClapperDetector
        from clipsort.ocr import TesseractEngine

        # Use 640x480 for reliable OCR, and space scenes further apart
        # so the 2-second text overlays don't overlap
        video_path, _scenes = make_multi_scene_video(
            "e2e_split_ocr.mp4",
            scenes=[
                {"time": 0, "scene": 1, "take": 1},
                {"time": 8, "scene": 2, "take": 1},
                {"time": 16, "scene": 3, "take": 1},
            ],
            total_seconds=24,
            width=640,
            height=480,
            marker_type="text",
        )

        ocr_engine = TesseractEngine()
        clapper_detector = ClapperDetector(ocr_engine=ocr_engine)
        scanner = SplitScanner(
            frame_detectors=[clapper_detector.detect_frame],
            sample_rate=1.0,
        )
        points = scanner.scan(video_path)

        # Should find at least some of the text scene markers
        assert len(points) >= 1

        duration = VideoSplitter.get_video_duration(video_path)
        splitter = VideoSplitter()
        segments = splitter.compute_segments(points, duration)

        output_dir = tmp_path / "split_output_ocr"
        paths = splitter.split(video_path, output_dir, segments)

        assert len(paths) == len(segments)
        for p in paths:
            assert p.exists()
            assert p.stat().st_size > 0
