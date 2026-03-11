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
