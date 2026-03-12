"""Tests for audio clap detection."""

from __future__ import annotations

import shutil

import numpy as np
import pytest

scipy = pytest.importorskip("scipy")

from clipsort.audio_detect import AudioClapDetector  # noqa: E402


class TestComputeEnvelope:
    def test_silence_returns_zeros(self):
        detector = AudioClapDetector(sample_rate=22050, window_ms=20.0)
        silence = np.zeros(22050, dtype=np.float32)  # 1 second of silence
        envelope = detector._compute_envelope(silence)
        assert len(envelope) > 0
        assert np.max(envelope) == 0.0

    def test_steady_tone_returns_constant(self):
        detector = AudioClapDetector(sample_rate=22050, window_ms=20.0)
        # 1 second of constant amplitude
        tone = np.ones(22050, dtype=np.float32) * 0.5
        envelope = detector._compute_envelope(tone)
        assert len(envelope) > 0
        # All RMS values should be ~0.5
        np.testing.assert_allclose(envelope, 0.5, atol=0.01)

    def test_impulse_creates_spike(self):
        detector = AudioClapDetector(sample_rate=22050, window_ms=20.0)
        # Silence with a loud burst in the middle
        audio = np.zeros(22050, dtype=np.float32)
        window_samples = int(22050 * 20.0 / 1000.0)
        mid = len(audio) // 2
        audio[mid : mid + window_samples] = 0.9
        envelope = detector._compute_envelope(audio)
        assert len(envelope) > 0
        # Max should be much higher than the rest
        peak_idx = np.argmax(envelope)
        assert envelope[peak_idx] > 0.5
        # Most values should be near zero
        median_val = np.median(envelope)
        assert median_val < 0.1

    def test_empty_audio_returns_empty(self):
        detector = AudioClapDetector()
        empty = np.array([], dtype=np.float32)
        envelope = detector._compute_envelope(empty)
        assert len(envelope) == 0

    def test_short_audio_returns_empty(self):
        detector = AudioClapDetector(sample_rate=22050, window_ms=20.0)
        # Fewer samples than one window
        short = np.ones(10, dtype=np.float32)
        envelope = detector._compute_envelope(short)
        assert len(envelope) == 0


class TestFindClaps:
    def test_single_peak(self):
        detector = AudioClapDetector(sample_rate=22050, window_ms=20.0, threshold=0.5)
        # Create synthetic envelope with a single spike
        envelope = np.zeros(500, dtype=np.float32)
        envelope[250] = 1.0  # One peak
        claps = detector._find_claps(envelope)
        assert len(claps) == 1

    def test_multiple_peaks(self):
        detector = AudioClapDetector(
            sample_rate=22050, window_ms=20.0, min_gap=0.5, threshold=0.5,
        )
        envelope = np.zeros(1000, dtype=np.float32)
        # Peaks well separated (>0.5s apart at 20ms window = 25 samples)
        envelope[100] = 1.0
        envelope[200] = 0.9
        envelope[300] = 0.8
        claps = detector._find_claps(envelope)
        assert len(claps) == 3

    def test_min_gap_filtering(self):
        detector = AudioClapDetector(
            sample_rate=22050, window_ms=20.0, min_gap=2.0, threshold=0.3,
        )
        # Two peaks very close together — should only get one
        envelope = np.zeros(500, dtype=np.float32)
        envelope[100] = 1.0
        envelope[105] = 0.9  # Only 5 windows apart = 100ms
        claps = detector._find_claps(envelope)
        assert len(claps) == 1

    def test_threshold_sensitivity(self):
        detector_low = AudioClapDetector(threshold=0.2)
        detector_high = AudioClapDetector(threshold=0.8)
        # Envelope with a big peak and a small peak
        envelope = np.zeros(500, dtype=np.float32)
        envelope[100] = 1.0
        envelope[300] = 0.3
        claps_low = detector_low._find_claps(envelope)
        claps_high = detector_high._find_claps(envelope)
        assert len(claps_low) >= len(claps_high)

    def test_silent_envelope_returns_empty(self):
        detector = AudioClapDetector()
        envelope = np.zeros(500, dtype=np.float32)
        claps = detector._find_claps(envelope)
        assert claps == []

    def test_timestamps_are_in_seconds(self):
        detector = AudioClapDetector(sample_rate=22050, window_ms=20.0)
        envelope = np.zeros(1000, dtype=np.float32)
        envelope[500] = 1.0  # At index 500, window_ms=20 -> 500 * 0.02 = 10.0s
        claps = detector._find_claps(envelope)
        assert len(claps) == 1
        assert abs(claps[0] - 10.0) < 0.1


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not available")
class TestExtractAudio:
    def test_extract_from_video(self, make_test_video_with_claps):
        video = make_test_video_with_claps("extract_test.mp4", [2.0], duration=5.0)
        detector = AudioClapDetector()
        audio = detector._extract_audio(video)
        assert len(audio) > 0
        assert audio.dtype == np.float32
        # Should be about 5 seconds of audio at 22050 Hz
        expected_samples = 5.0 * 22050
        assert abs(len(audio) - expected_samples) < 22050  # Within 1 second

    def test_extract_from_silent_video(self, make_test_video_with_claps):
        video = make_test_video_with_claps("silent_test.mp4", [], duration=3.0)
        detector = AudioClapDetector()
        audio = detector._extract_audio(video)
        assert len(audio) > 0
        # Should be mostly silence — RMS should be very low
        rms = np.sqrt(np.mean(audio**2))
        assert rms < 0.01

    def test_extract_nonexistent_file(self, tmp_path):
        detector = AudioClapDetector()
        audio = detector._extract_audio(tmp_path / "nonexistent.mp4")
        assert len(audio) == 0


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not available")
class TestDetectTimestamps:
    def test_detects_claps_at_known_times(self, make_test_video_with_claps):
        clap_times = [2.0, 5.0, 8.0]
        video = make_test_video_with_claps(
            "detect_test.mp4", clap_times, duration=10.0,
        )
        detector = AudioClapDetector(threshold=0.3)
        timestamps = detector.detect_timestamps(video)
        # Should detect roughly the right number of claps
        assert len(timestamps) >= 1
        # Detected timestamps should be in ascending order
        assert timestamps == sorted(timestamps)

    def test_silent_video_returns_empty(self, make_test_video_with_claps):
        video = make_test_video_with_claps("silent_detect.mp4", [], duration=5.0)
        detector = AudioClapDetector()
        timestamps = detector.detect_timestamps(video)
        assert timestamps == []

    def test_nonexistent_file_returns_empty(self, tmp_path):
        detector = AudioClapDetector()
        timestamps = detector.detect_timestamps(tmp_path / "nonexistent.mp4")
        assert timestamps == []


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not available")
class TestAudioSplitIntegration:
    """Test that audio split points integrate with the split pipeline."""

    def test_audio_split_points_have_no_clip_info(self, make_test_video_with_claps):
        from clipsort.splitter import SplitPoint

        video = make_test_video_with_claps(
            "integration_test.mp4", [3.0, 6.0], duration=10.0,
        )
        detector = AudioClapDetector(threshold=0.3)
        timestamps = detector.detect_timestamps(video)

        # Audio-detected timestamps become SplitPoints with clip_info=None
        split_points = [SplitPoint(timestamp=t, clip_info=None) for t in timestamps]
        for sp in split_points:
            assert sp.clip_info is None

    def test_audio_segments_get_generic_names(self, make_test_video_with_claps):
        from clipsort.splitter import SplitPoint, VideoSplitter

        video = make_test_video_with_claps(
            "naming_test.mp4", [3.0], duration=8.0,
        )
        detector = AudioClapDetector(threshold=0.3)
        timestamps = detector.detect_timestamps(video)

        if not timestamps:
            pytest.skip("No claps detected in test video")

        split_points = [SplitPoint(timestamp=t, clip_info=None) for t in timestamps]
        splitter = VideoSplitter()
        duration = splitter.get_video_duration(video)
        segments = splitter.compute_segments(split_points, duration)

        # First segment (preamble) should be named "preamble"
        # Subsequent segments should be named "segment_NNN"
        for seg in segments:
            name = splitter._segment_filename(seg, ".mp4")
            assert name in ("preamble.mp4",) or name.startswith("segment_")

    def test_merge_audio_with_visual_split_points(self):
        from clipsort.parser import ClipInfo
        from clipsort.splitter import SplitPoint, SplitScanner

        # Simulate merging audio and visual split points
        visual_points = [
            SplitPoint(timestamp=2.0, clip_info=ClipInfo(scene=1, take=1, method="qr")),
            SplitPoint(timestamp=10.0, clip_info=ClipInfo(scene=2, take=1, method="qr")),
        ]
        audio_points = [
            SplitPoint(timestamp=2.5, clip_info=None),  # Near visual — duplicate
            SplitPoint(timestamp=6.0, clip_info=None),  # New split point
            SplitPoint(timestamp=10.2, clip_info=None),  # Near visual — duplicate
        ]

        scanner = SplitScanner(frame_detectors=[], dedup_window=3.0)
        merged = list(visual_points)
        for ap in audio_points:
            if not scanner._is_duplicate(ap, merged):
                merged.append(ap)

        merged.sort(key=lambda sp: sp.timestamp)
        # Should have visual(2.0), audio(6.0), visual(10.0) — the two near-dupes are filtered
        assert len(merged) == 3
        assert merged[0].timestamp == 2.0
        assert merged[1].timestamp == 6.0
        assert merged[2].timestamp == 10.0
