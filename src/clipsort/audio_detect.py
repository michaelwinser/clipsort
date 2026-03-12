"""Audio clap detection — detect audible clap sounds in video audio tracks."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


class AudioClapDetector:
    """Detect audible clap sounds in video audio tracks.

    Extracts audio via FFmpeg, computes a short-time energy envelope,
    and finds peaks using scipy.signal.find_peaks with prominence filtering.
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        window_ms: float = 20.0,
        min_gap: float = 2.0,
        threshold: float = 0.6,
    ) -> None:
        """Configure the detector.

        Args:
            sample_rate: Audio sample rate for analysis (Hz).
            window_ms: RMS window size in milliseconds.
            min_gap: Minimum seconds between claps to avoid double-triggering.
            threshold: Prominence threshold as fraction of max energy.
        """
        self.sample_rate = sample_rate
        self.window_ms = window_ms
        self.min_gap = min_gap
        self.threshold = threshold

    def detect_timestamps(self, video_path: Path) -> list[float]:
        """Extract audio and return timestamps of detected claps.

        Args:
            video_path: Path to the video file.

        Returns:
            List of timestamps (seconds) where claps were detected, sorted ascending.
        """
        audio = self._extract_audio(video_path)
        if audio.size == 0:
            return []

        envelope = self._compute_envelope(audio)
        if envelope.size == 0:
            return []

        return self._find_claps(envelope)

    def _extract_audio(self, video_path: Path) -> np.ndarray:
        """Extract mono audio as float32 array via FFmpeg pipe.

        Args:
            video_path: Path to the video file.

        Returns:
            Audio samples normalized to [-1, 1] as float32.
        """
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-ac", "1",
            "-ar", str(self.sample_rate),
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "pipe:1",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            logger.warning("Failed to extract audio from %s", video_path)
            return np.array([], dtype=np.float32)

        if not result.stdout:
            logger.debug("No audio data in %s", video_path)
            return np.array([], dtype=np.float32)

        # Parse raw 16-bit PCM and normalize to [-1, 1]
        raw = np.frombuffer(result.stdout, dtype=np.int16)
        return raw.astype(np.float32) / 32768.0

    def _compute_envelope(self, audio: np.ndarray) -> np.ndarray:
        """Compute RMS energy envelope over sliding windows.

        Args:
            audio: Audio samples as float32 in [-1, 1].

        Returns:
            RMS energy envelope (one value per window).
        """
        window_samples = max(1, int(self.sample_rate * self.window_ms / 1000.0))

        # Trim audio to exact multiple of window size
        n_windows = len(audio) // window_samples
        if n_windows == 0:
            return np.array([], dtype=np.float32)

        trimmed = audio[: n_windows * window_samples]
        frames = trimmed.reshape(n_windows, window_samples)
        return np.sqrt(np.mean(frames**2, axis=1))

    def _find_claps(self, envelope: np.ndarray) -> list[float]:
        """Find peaks in the envelope using scipy.signal.find_peaks.

        Args:
            envelope: RMS energy envelope from _compute_envelope.

        Returns:
            List of timestamps (seconds) of detected claps.
        """
        from scipy.signal import find_peaks

        # Convert min_gap to envelope sample distance
        window_seconds = self.window_ms / 1000.0
        min_distance = max(1, int(self.min_gap / window_seconds))

        # Prominence threshold: fraction of max energy
        max_energy = np.max(envelope)
        if max_energy == 0:
            return []

        prominence = self.threshold * max_energy

        peaks, _ = find_peaks(
            envelope,
            distance=min_distance,
            prominence=prominence,
        )

        # Convert peak indices to timestamps
        timestamps = [int(p) * window_seconds for p in peaks]
        return timestamps
