"""Shared test fixtures for ClipSort.

Fixture strategy:
- Phase 1 tests use empty files (just need names and directory structure).
- Phase 2+ tests use tiny programmatically-generated videos via OpenCV.
- Phase 3 clapper board tests use curated reference images in tests/fixtures/.
"""

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Phase 1 fixtures: empty files for filename-based tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_video_dir(tmp_path: Path) -> Path:
    """A temp dir with empty video files using simple scene-letter naming."""
    d = tmp_path / "videos"
    d.mkdir()
    for name in ["1a.mp4", "1b.mp4", "2a.mp4", "2b.mp4", "2c.mp4", "3a.mov"]:
        (d / name).touch()
    return d


@pytest.fixture()
def scene_letter_files(tmp_path: Path) -> Path:
    """Files using the 1a/1b/1c naming pattern."""
    d = tmp_path / "letters"
    d.mkdir()
    for name in ["1a.mp4", "1b.mp4", "1c.mp4", "2a.mp4", "2b.mp4"]:
        (d / name).touch()
    return d


@pytest.fixture()
def mixed_pattern_files(tmp_path: Path) -> Path:
    """Files using different naming conventions in the same directory."""
    d = tmp_path / "mixed"
    d.mkdir()
    for name in [
        "1a.mp4",
        "Scene2_Take1.mp4",
        "S03T01.mp4",
        "3_2.mkv",
        "random_notes.txt",
        "behind_the_scenes.mp4",
    ]:
        (d / name).touch()
    return d


@pytest.fixture()
def nested_video_dir(tmp_path: Path) -> Path:
    """Files in subdirectories simulating multiple memory cards."""
    root = tmp_path / "cards"
    root.mkdir()
    card_a = root / "CARD_A"
    card_a.mkdir()
    card_b = root / "CARD_B"
    card_b.mkdir()
    for name in ["1a.mp4", "1b.mp4"]:
        (card_a / name).touch()
    for name in ["2a.mp4", "2b.mp4"]:
        (card_b / name).touch()
    return root


# ---------------------------------------------------------------------------
# Phase 2+ fixtures: tiny generated videos (requires OpenCV)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def make_test_video(tmp_path_factory):
    """Factory that creates tiny test videos using OpenCV.

    Returns a callable: make(filename, *, width, height, fps, seconds, qr_data)
    Gated behind pytest.importorskip so Phase 1 tests run without OpenCV.
    """
    cv2 = pytest.importorskip("cv2")
    import numpy as np

    video_dir = tmp_path_factory.mktemp("test_videos")

    def _make(
        filename: str = "test.mp4",
        *,
        width: int = 320,
        height: int = 240,
        fps: int = 5,
        seconds: int = 1,
        qr_data: str | None = None,
        text_overlay: dict | None = None,
    ) -> Path:
        path = video_dir / filename
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))

        total_frames = fps * seconds
        for i in range(total_frames):
            # Gradient frame so each frame is visually distinct
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            shade = int(255 * i / max(total_frames - 1, 1))
            frame[:, :] = (shade, 128, 255 - shade)

            if qr_data and i == 0:
                # Embed a QR code in the first frame
                try:
                    import qrcode

                    qr_img = qrcode.make(qr_data).resize((100, 100))
                    qr_np = np.array(qr_img.convert("RGB"))
                    frame[10:110, 10:110] = qr_np
                except ImportError:
                    pass

            if text_overlay and i < fps * 2:
                # Draw clapper-board-like text on first 2 seconds of frames.
                # Draw a white rectangle as slate background, then black text.
                slate_x, slate_y = 20, 20
                slate_w, slate_h = width - 40, height - 40
                cv2.rectangle(
                    frame,
                    (slate_x, slate_y),
                    (slate_x + slate_w, slate_y + slate_h),
                    (255, 255, 255),
                    -1,
                )
                # Draw border
                cv2.rectangle(
                    frame,
                    (slate_x, slate_y),
                    (slate_x + slate_w, slate_y + slate_h),
                    (0, 0, 0),
                    2,
                )
                scene_num = text_overlay.get("scene", 1)
                take_num = text_overlay.get("take", 1)
                cv2.putText(
                    frame,
                    f"SCENE {scene_num}",
                    (slate_x + 10, slate_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"TAKE {take_num}",
                    (slate_x + 10, slate_y + 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 0),
                    2,
                )

            writer.write(frame)

        writer.release()
        return path

    return _make


@pytest.fixture(scope="session")
def qr_video(make_test_video):
    """A tiny video with a QR code in the first frame."""
    import json

    data = json.dumps({"v": 1, "scene": 1, "take": 1})
    return make_test_video("qr_test.mp4", qr_data=data)


@pytest.fixture(scope="session")
def plain_video(make_test_video):
    """A tiny video with no QR code."""
    return make_test_video("plain_test.mp4")


@pytest.fixture(scope="session")
def clapper_video(make_test_video):
    """A tiny video with clapper board text overlay (Scene 3, Take 2)."""
    return make_test_video(
        "clapper_test.mp4",
        width=640,
        height=480,
        seconds=2,
        text_overlay={"scene": 3, "take": 2},
    )


# ---------------------------------------------------------------------------
# Phase 3b fixtures: multi-scene videos for splitting tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def make_multi_scene_video(tmp_path_factory):
    """Factory that creates test videos with multiple scene markers at known timestamps.

    Returns a callable: make(filename, scenes, *, width, height, fps, marker_type)

    Each scene entry is a dict with:
      - "time": timestamp in seconds where the marker appears
      - "scene": scene number
      - "take": take number (optional)

    Default: 3 scenes at 0s, 7s, 14s in a 20s video.
    """
    cv2 = pytest.importorskip("cv2")
    import json

    import numpy as np

    video_dir = tmp_path_factory.mktemp("multi_scene_videos")

    def _make(
        filename: str = "multi_scene.mp4",
        scenes: list[dict] | None = None,
        *,
        total_seconds: int = 20,
        width: int = 320,
        height: int = 240,
        fps: int = 5,
        marker_type: str = "qr",
    ) -> tuple[Path, list[dict]]:
        if scenes is None:
            scenes = [
                {"time": 0, "scene": 1, "take": 1},
                {"time": 7, "scene": 2, "take": 1},
                {"time": 14, "scene": 3, "take": 1},
            ]

        path = video_dir / filename
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))

        total_frames = fps * total_seconds
        # How many frames each marker is visible (2 seconds for text/OCR,
        # 1 frame for QR since a single frame is enough for decoding)
        marker_duration_frames = fps * 2 if marker_type == "text" else 1

        # Build a list of (start_frame, end_frame, scene_info) ranges
        marker_ranges = []
        for s in scenes:
            start = int(s["time"] * fps)
            end = min(start + marker_duration_frames, total_frames)
            marker_ranges.append((start, end, s))

        for i in range(total_frames):
            # Different color per "segment" so they're visually distinguishable
            segment_idx = 0
            for s in scenes:
                if i >= int(s["time"] * fps):
                    segment_idx = s["scene"]
            hue = (segment_idx * 60) % 180
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :] = (hue, 128, 200)

            # Check if this frame falls within any marker range
            for start, end, scene_info in marker_ranges:
                if start <= i < end:
                    if marker_type == "qr":
                        try:
                            import qrcode

                            data = json.dumps({
                                "v": 1,
                                "scene": scene_info["scene"],
                                "take": scene_info.get("take", 1),
                            })
                            qr_img = qrcode.make(data).resize((100, 100))
                            qr_np = np.array(qr_img.convert("RGB"))
                            frame[10:110, 10:110] = qr_np
                        except ImportError:
                            pass
                    elif marker_type == "text":
                        # Draw text overlay like clapper board
                        scene_num = scene_info["scene"]
                        take_num = scene_info.get("take", 1)
                        sx, sy = 20, 20
                        ex, ey = width - 20, height - 20
                        cv2.rectangle(frame, (sx, sy), (ex, ey), (255, 255, 255), -1)
                        cv2.rectangle(frame, (sx, sy), (ex, ey), (0, 0, 0), 2)
                        cv2.putText(
                            frame, f"SCENE {scene_num}",
                            (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2,
                        )
                        cv2.putText(
                            frame, f"TAKE {take_num}",
                            (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2,
                        )
                    break  # Only draw one marker per frame

            writer.write(frame)

        writer.release()
        return path, scenes

    return _make
