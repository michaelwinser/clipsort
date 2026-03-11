# Test Fixtures

## Strategy

ClipSort uses **generated fixtures** wherever possible, to keep the repo small and tests deterministic.

### Phase 1 — Empty files
Phase 1 tests only need files with the right names (the content doesn't matter for filename-based organization). Fixtures are created in `conftest.py` using `Path.touch()`.

### Phase 2 — Tiny generated videos
Phase 2 tests need actual video files (for QR code detection). The `make_test_video` factory in `conftest.py` generates 1-second, 320x240 videos using OpenCV. These are created once per test session and cached in a temp dir. Total size per video is ~10-50KB.

This is gated behind `pytest.importorskip("cv2")` so Phase 1 tests run without OpenCV installed.

### Phase 3 — Curated reference images
Phase 3 tests (clapper board OCR) use curated reference images in `clapper_boards/`. These are the one case where static fixtures are better than generated ones — realistic handwriting, lighting conditions, and camera angles can't be programmatically reproduced.

Each image is a small JPEG (<100KB). The `manifest.json` file describes the expected OCR results for each image.

## Adding fixtures

- **Prefer generated over static.** If you can create a fixture programmatically, do so in `conftest.py`.
- **Keep static fixtures small.** Compress images, use low resolution, crop to the region of interest.
- **Document expectations.** For static fixtures, add entries to the relevant manifest file.
