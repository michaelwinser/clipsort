"""Video splitting — scan for scene markers and split with FFmpeg."""

from __future__ import annotations

import logging
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from clipsort.parser import ClipInfo

logger = logging.getLogger(__name__)

FrameDetector = Callable[[np.ndarray], ClipInfo | None]


@dataclass
class SplitPoint:
    """A detected scene marker at a specific timestamp."""

    timestamp: float  # Seconds from video start
    clip_info: ClipInfo | None


@dataclass
class Segment:
    """A contiguous segment of video to extract."""

    start: float
    end: float | None  # None = to end of video
    clip_info: ClipInfo | None  # None for preamble
    index: int


class SplitScanner:
    """Iterate through a video and detect scene markers."""

    def __init__(
        self,
        frame_detectors: list[FrameDetector],
        sample_rate: float = 1.0,
        dedup_window: float = 3.0,
    ) -> None:
        """Configure the scanner.

        Args:
            frame_detectors: Callables that take a frame and return ClipInfo or None.
            sample_rate: Frames per second to sample.
            dedup_window: Seconds within which duplicate detections are merged.
        """
        self.frame_detectors = frame_detectors
        self.sample_rate = sample_rate
        self.dedup_window = dedup_window

    def scan(self, video_path: Path) -> list[SplitPoint]:
        """Scan the full video for scene markers.

        Args:
            video_path: Path to the video file.

        Returns:
            List of SplitPoints sorted by timestamp.
        """
        import cv2

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.warning("Cannot open video: %s", video_path)
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, int(fps / self.sample_rate))

        split_points: list[SplitPoint] = []

        for frame_idx in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_idx / fps

            for detector in self.frame_detectors:
                info = detector(frame)
                if info is not None:
                    candidate = SplitPoint(timestamp=timestamp, clip_info=info)
                    if not self._is_duplicate(candidate, split_points):
                        split_points.append(candidate)
                        if info is not None:
                            logger.debug(
                                "Split point at %.1fs: scene=%d in %s",
                                timestamp,
                                info.scene,
                                video_path.name,
                            )
                        else:
                            logger.debug(
                                "Split point at %.1fs in %s",
                                timestamp,
                                video_path.name,
                            )
                    break  # First detector wins for this frame

        cap.release()
        return split_points

    def _is_duplicate(self, candidate: SplitPoint, existing: list[SplitPoint]) -> bool:
        """Check if a candidate is a duplicate of a recent detection.

        A candidate is duplicate if within the dedup window there is:
        - A point with matching scene/take (both have clip_info), or
        - Any point at all, when the candidate has no clip_info (audio).
          Audio-only split points near any existing point are redundant.
        """
        for point in existing:
            time_gap = abs(candidate.timestamp - point.timestamp)
            if time_gap > self.dedup_window:
                continue
            # Audio candidate (no clip_info) is duplicate if near any existing point
            if candidate.clip_info is None:
                return True
            # Visual candidate: check if scene/take match
            if (
                point.clip_info is not None
                and candidate.clip_info.scene == point.clip_info.scene
                and candidate.clip_info.take == point.clip_info.take
            ):
                return True
        return False


class VideoSplitter:
    """Split a video into segments using FFmpeg."""

    def __init__(self, precise: bool = False) -> None:
        """Configure splitting mode.

        Args:
            precise: If True, re-encode for frame-accurate cuts.
                     If False, use stream copy (fast but may have keyframe imprecision).
        """
        self.precise = precise

    @staticmethod
    def check_ffmpeg() -> None:
        """Raise RuntimeError if ffmpeg is not available."""
        if shutil.which("ffmpeg") is None:
            raise RuntimeError(
                "ffmpeg not found. Install FFmpeg or use the Docker image."
            )
        if shutil.which("ffprobe") is None:
            raise RuntimeError(
                "ffprobe not found. Install FFmpeg or use the Docker image."
            )

    @staticmethod
    def get_video_duration(path: Path) -> float:
        """Get video duration in seconds using ffprobe."""
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())

    def compute_segments(
        self,
        split_points: list[SplitPoint],
        duration: float,
        slate_buffer: float = 0.5,
        skip_preamble: bool = False,
    ) -> list[Segment]:
        """Compute output segments from split points.

        Args:
            split_points: Detected scene markers (must be sorted by timestamp).
            duration: Total video duration in seconds.
            slate_buffer: Seconds to skip past the slate after each detection.
            skip_preamble: If True, discard content before the first detection.

        Returns:
            List of Segments to extract.
        """
        if not split_points:
            return []

        segments: list[Segment] = []
        idx = 0

        # Preamble: content before the first detection
        first_ts = split_points[0].timestamp
        if first_ts > 0 and not skip_preamble:
            segments.append(Segment(start=0, end=first_ts, clip_info=None, index=idx))
            idx += 1

        # Each split point starts a new segment
        for i, point in enumerate(split_points):
            start = point.timestamp + slate_buffer
            # Clamp start to not exceed duration
            start = min(start, duration)

            end = split_points[i + 1].timestamp if i + 1 < len(split_points) else None

            # Skip zero-length segments
            if end is not None and start >= end:
                continue

            segments.append(
                Segment(start=start, end=end, clip_info=point.clip_info, index=idx)
            )
            idx += 1

        return segments

    def split(
        self, video_path: Path, output_dir: Path, segments: list[Segment]
    ) -> list[Path]:
        """Split video into segments using FFmpeg.

        Args:
            video_path: Source video file.
            output_dir: Directory to write output clips.
            segments: Segments to extract.

        Returns:
            List of paths to created files.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        extension = video_path.suffix
        output_paths = []

        for segment in segments:
            filename = self._segment_filename(segment, extension)
            output_path = output_dir / filename
            self._run_ffmpeg(video_path, output_path, segment.start, segment.end)
            output_paths.append(output_path)
            logger.debug("Created %s", output_path.name)

        return output_paths

    def _run_ffmpeg(
        self,
        video_path: Path,
        output_path: Path,
        start: float,
        end: float | None,
    ) -> None:
        """Run a single FFmpeg extraction."""
        cmd = ["ffmpeg", "-y", "-i", str(video_path)]

        cmd.extend(["-ss", f"{start:.3f}"])
        if end is not None:
            cmd.extend(["-to", f"{end:.3f}"])

        if self.precise:
            # Re-encode for frame-accurate cuts
            cmd.extend(["-c:v", "libx264", "-c:a", "aac"])
        else:
            # Stream copy for speed
            cmd.extend(["-c", "copy"])

        cmd.append(str(output_path))

        logger.debug("Running: %s", " ".join(cmd))
        subprocess.run(cmd, capture_output=True, check=True)

    @staticmethod
    def _segment_filename(segment: Segment, extension: str) -> str:
        """Generate a filename for a segment.

        Naming convention:
        - scene_01_take_01.mp4 (scene + numeric take)
        - scene_01_take_a.mp4 (scene + letter take)
        - scene_02.mp4 (scene, no take)
        - preamble.mp4 (content before first detection)
        - segment_001.mp4 (fallback when no clip_info)
        """
        if segment.clip_info is None:
            if segment.index == 0:
                return f"preamble{extension}"
            return f"segment_{segment.index:03d}{extension}"

        info = segment.clip_info
        name = f"scene_{info.scene:02d}"
        if info.take is not None:
            if isinstance(info.take, int):
                name += f"_take_{info.take:02d}"
            else:
                name += f"_take_{info.take}"
        return f"{name}{extension}"
