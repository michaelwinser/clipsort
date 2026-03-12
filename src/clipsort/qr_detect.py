"""QR code detection in video files."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path

from clipsort.parser import ClipInfo

logger = logging.getLogger(__name__)


class QRDetector:
    """Detect QR codes in the first few seconds of a video file."""

    def __init__(self, scan_seconds: int = 10, sample_rate: int = 2) -> None:
        """Configure the scan window.

        Args:
            scan_seconds: How many seconds from the start to scan.
            sample_rate: Frames to sample per second.
        """
        self.scan_seconds = scan_seconds
        self.sample_rate = sample_rate

    def detect(self, video_path: Path) -> ClipInfo | None:
        """Scan video frames for a QR code and return parsed metadata.

        Args:
            video_path: Path to the video file.

        Returns:
            ClipInfo if a valid QR code is found, None otherwise.
        """
        import cv2
        from pyzbar.pyzbar import decode as pyzbar_decode

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.warning("Cannot open video: %s", video_path)
            return None

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        max_frame = min(total_frames, int(fps * self.scan_seconds))
        frame_interval = max(1, int(fps / self.sample_rate))

        for frame_idx in range(0, max_frame, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            decoded = pyzbar_decode(frame)
            for obj in decoded:
                raw = obj.data.decode("utf-8", errors="replace")
                info = self._parse_qr_data(raw)
                if info is not None:
                    cap.release()
                    logger.debug("QR found at frame %d in %s", frame_idx, video_path.name)
                    return info

        cap.release()
        return None

    @staticmethod
    def _parse_qr_data(raw: str) -> ClipInfo | None:
        """Parse a QR data string into ClipInfo.

        Expects JSON with schema ``{"v": 1, "scene": N, "take": N}``.

        Returns:
            ClipInfo or None if the data is invalid.
        """
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

        if not isinstance(data, dict):
            return None
        if data.get("v") != 1:
            return None
        if "scene" not in data or "take" not in data:
            return None

        try:
            scene = int(data["scene"])
            take = data["take"]
        except (ValueError, TypeError):
            return None

        return ClipInfo(scene=scene, take=take, method="qr")


class DetectionChain:
    """Try a sequence of detectors, returning the first successful result."""

    def __init__(self, detectors: list[Callable[[Path], ClipInfo | None]]) -> None:
        self.detectors = detectors

    def detect(self, video_path: Path) -> ClipInfo | None:
        """Run each detector in order; return the first non-None result."""
        for detector in self.detectors:
            result = detector(video_path)
            if result is not None:
                return result
        return None
