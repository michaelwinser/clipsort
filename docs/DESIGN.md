# Design Document: ClipSort

**Version:** 1.0
**Date:** 2026-03-10

---

## 1. Architecture Overview

ClipSort is a Python CLI application packaged as a Docker container. It follows a pipeline architecture where video files pass through detection stages and are routed to their destination folders.

```
                         +------------------+
                         |   CLI Interface   |
                         |   (click/typer)   |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   File Scanner    |
                         | (find video files)|
                         +--------+---------+
                                  |
                    +-------------+-------------+
                    |             |              |
           +--------v--+  +------v------+  +----v--------+
           |  Filename  |  |  QR Code    |  |  Clapper    |
           |  Parser    |  |  Detector   |  |  OCR        |
           +--------+--+  +------+------+  +----+--------+
                    |             |              |
                    +-------------+-------------+
                                  |
                         +--------v---------+
                         |   Organizer       |
                         | (copy/move files) |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Reporter        |
                         | (summary output)  |
                         +------------------+
```

### Key Design Principles

1. **Detection chain with fallback**: QR -> OCR -> Filename -> Unsorted. Each detector returns a result or `None`, and the next detector in the chain is tried.
2. **Non-destructive by default**: Files are copied, not moved, unless explicitly requested.
3. **Dry-run first**: The organizer builds a plan (list of source->dest mappings) that can be previewed or executed.
4. **Pluggable detectors**: Each detection method implements a common interface, making it easy to add new methods.

## 2. Component Design

### 2.1 CLI Interface

**Technology:** [Click](https://click.palletsprojects.com/)

Click is preferred over argparse for its decorator-based API and built-in help generation. Typer is an alternative but Click has fewer dependencies.

**Commands:**

```
clipsort organize [OPTIONS] INPUT_DIR OUTPUT_DIR
clipsort detect [OPTIONS] INPUT_DIR OUTPUT_DIR
clipsort split [OPTIONS] INPUT_FILE OUTPUT_DIR
clipsort qr-generate [OPTIONS]
```

**Global Options:**
- `--verbose` / `-v`: Enable debug logging
- `--dry-run`: Preview without making changes
- `--move`: Move files instead of copying
- `--recursive` / `-r`: Scan subdirectories
- `--report-file PATH`: Save report to file

### 2.2 File Scanner

Responsible for discovering video files in the input directory.

```python
class FileScanner:
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.mts', '.m4v', '.webm'}

    def scan(self, input_dir: Path, recursive: bool = False) -> list[Path]:
        """Return sorted list of video file paths."""
```

- Uses `pathlib.Path.glob()` or `rglob()` for recursive scanning
- Filters by extension (case-insensitive)
- Returns files sorted by name for deterministic output

### 2.3 Filename Parser

Extracts scene/take information from filenames using regex pattern matching.

```python
@dataclass
class ClipInfo:
    scene: int
    take: int | str | None = None
    confidence: float = 1.0
    method: str = "filename"

class FilenameParser:
    PATTERNS: list[tuple[str, re.Pattern]] = [
        ("scene_letter",  re.compile(r'^(\d+)([a-z])(?:\.\w+)?$', re.I)),
        ("scene_take",    re.compile(r'^(\d+)[_-](\d+)(?:\.\w+)?$')),
        ("scene_Take",    re.compile(r'^[Ss]cene[_\s]?(\d+)[_\s]?[Tt]ake[_\s]?(\d+)', re.I)),
        ("short_form",    re.compile(r'^[Ss](\d+)[Tt](\d+)', re.I)),
    ]

    def parse(self, filename: str) -> ClipInfo | None:
        """Try each pattern; return first match or None."""

    def parse_custom(self, filename: str, pattern: str) -> ClipInfo | None:
        """Parse using a user-provided pattern with {scene}/{take} placeholders."""
```

The custom pattern feature converts user-friendly patterns like `{scene}_{take}` into regex groups.

### 2.4 QR Code Detector

Scans the first N seconds of a video for QR codes.

```python
class QRDetector:
    def __init__(self, scan_seconds: int = 10, sample_rate: int = 2):
        """
        scan_seconds: how far into the video to scan
        sample_rate: frames to sample per second
        """

    def detect(self, video_path: Path) -> ClipInfo | None:
        """Open video, sample frames, scan for QR codes."""
```

**Technology:**
- **OpenCV** (`cv2.VideoCapture`) for frame extraction
- **pyzbar** for QR code decoding (faster and more reliable than OpenCV's built-in detector)

**QR Data Format:**
```json
{
  "v": 1,
  "scene": 3,
  "take": 2,
  "project": "short-film"
}
```

The `v` field is a schema version for forward compatibility. The decoder validates the schema and rejects unrecognized versions.

**Frame Sampling Strategy:**
- Extract `scan_seconds * sample_rate` frames from the start of the video
- For a 10-second scan at 2 fps, that's 20 frames per video
- Processing time: ~200ms per video (20 frames x ~10ms per frame with pyzbar)

### 2.5 QR Code Generator

Generates printable QR codes for clapper boards.

```python
class QRGenerator:
    def generate_single(self, scene: int, take: int, project: str = "") -> Image:
        """Generate a single QR code image."""

    def generate_sheet(self, scenes: int, takes: int, project: str = "",
                       output_path: Path) -> None:
        """Generate a printable PDF with all scene/take QR codes."""
```

**Technology:**
- **qrcode** library for QR generation
- **Pillow** for image composition
- **reportlab** or **fpdf2** for PDF generation

### 2.6 Clapper Board Detector (Phase 3)

Detects the visual presence of a clapper board and extracts text via OCR.

```python
class ClapperDetector:
    def detect(self, video_path: Path) -> ClipInfo | None:
        """Detect clapper board and read scene/take via OCR."""

    def _find_slate_frame(self, video_path: Path) -> np.ndarray | None:
        """Find the frame most likely to contain a readable slate."""

    def _preprocess_slate(self, frame: np.ndarray) -> np.ndarray:
        """Enhance contrast, deskew, crop to slate region."""

    def _ocr_slate(self, slate_image: np.ndarray) -> ClipInfo | None:
        """Run OCR and extract scene/take fields."""
```

**Slate Detection Strategy:**
1. Sample frames from the first 10 seconds
2. For each frame, detect high-contrast rectangular regions (potential slates)
3. Score candidates by: aspect ratio close to 4:3, high internal contrast, presence of horizontal stripes at top
4. Select the highest-scoring frame

**OCR Pipeline:**
1. Crop to detected slate region
2. Apply CLAHE contrast enhancement
3. Deskew using Hough line detection
4. Run OCR (PaddleOCR for accuracy; EasyOCR as fallback)
5. Parse OCR output for patterns like "SCENE: 3" or "SC 3 TK 2"
6. Return result with confidence score

### 2.7 Video Splitter (Phase 3)

Splits a continuous video file at detected clapper board boundaries.

```python
class VideoSplitter:
    def split(self, video_path: Path, output_dir: Path,
              timestamps: list[SplitPoint]) -> list[Path]:
        """Split video at given timestamps using FFmpeg."""
```

**FFmpeg Strategy:**
- Use stream copy (`-c copy`) for speed — no re-encoding
- Add 0.5s buffer after each clapper detection to skip the slate itself
- For frame-accurate cuts, offer an optional `--precise` flag that re-encodes

### 2.8 Organizer

Builds and executes the file organization plan.

```python
@dataclass
class OrganizePlan:
    mappings: list[tuple[Path, Path]]  # (source, destination)
    unsorted: list[Path]
    conflicts: list[tuple[Path, Path, Path]]  # (source, attempted_dest, actual_dest)

class Organizer:
    def plan(self, files: list[tuple[Path, ClipInfo | None]],
             output_dir: Path, folder_format: str = "scene_{scene:02d}") -> OrganizePlan:
        """Build the organization plan."""

    def execute(self, plan: OrganizePlan, move: bool = False) -> None:
        """Execute the plan (copy or move files)."""
```

**Conflict Resolution:**
When two files map to the same destination, append `_2`, `_3`, etc. before the extension.

### 2.9 Reporter

Generates human-readable summaries of operations.

```python
class Reporter:
    def report(self, plan: OrganizePlan, stream=sys.stdout) -> None:
        """Print organization summary."""

    def save(self, plan: OrganizePlan, path: Path) -> None:
        """Save report to file."""
```

## 3. Project Structure

```
clipsort/
  docs/
    PRD.md
    DESIGN.md
    ROADMAP.md
  src/
    clipsort/
      __init__.py
      cli.py              # Click CLI entry point
      scanner.py           # FileScanner
      parser.py            # FilenameParser, ClipInfo
      qr_detect.py         # QRDetector
      qr_generate.py       # QRGenerator
      clapper_detect.py    # ClapperDetector (Phase 3)
      splitter.py          # VideoSplitter (Phase 3)
      organizer.py         # Organizer, OrganizePlan
      reporter.py          # Reporter
  tests/
    conftest.py            # Shared fixtures
    test_scanner.py
    test_parser.py
    test_qr_detect.py
    test_qr_generate.py
    test_clapper_detect.py
    test_splitter.py
    test_organizer.py
    test_reporter.py
    test_cli.py            # Integration tests
    fixtures/              # Test video/image files
  Dockerfile
  docker-compose.yml
  pyproject.toml
  Makefile                 # Build, test, lint shortcuts
```

## 4. Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.12 | Rich ecosystem for video/image processing |
| CLI Framework | Click | Simple, well-documented, minimal dependencies |
| Video I/O | OpenCV (cv2) | Industry standard, fast frame extraction |
| QR Detection | pyzbar | Fast, reliable, ~10ms per frame |
| QR Generation | qrcode + Pillow | Lightweight, well-maintained |
| PDF Generation | fpdf2 | Lightweight, no system dependencies |
| OCR | PaddleOCR | Best accuracy/size ratio for Docker |
| Video Splitting | FFmpeg (subprocess) | Industry standard, stream copy support |
| Audio Analysis | librosa | Feature extraction for clap detection |
| Testing | pytest | Standard Python test framework |
| Linting | ruff | Fast, replaces flake8 + isort + black |
| Docker Base | python:3.12-slim | Small base image |

## 5. Docker Design

### Dockerfile Strategy

Multi-stage build to keep the final image small:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
# Install build tools, compile wheels

# Stage 2: Runtime
FROM python:3.12-slim
# Copy wheels from builder
# Install FFmpeg and system libs (libzbar, libgl1)
# Install Python packages
# Set entrypoint
```

### Volume Mounts

```
/input   - Read-only mount of source video directory
/output  - Writable mount for organized output
```

### Entry Point

```dockerfile
ENTRYPOINT ["python", "-m", "clipsort"]
```

Usage:
```bash
docker run --rm \
  -v $(pwd)/raw:/input:ro \
  -v $(pwd)/organized:/output \
  clipsort organize /input /output
```

## 6. Error Handling Strategy

| Error Type | Handling |
|-----------|---------|
| Missing input directory | Exit with clear message and usage hint |
| No video files found | Exit with message listing supported extensions |
| Permission denied on output | Exit with message suggesting volume mount fix |
| Corrupt video file | Log warning, skip file, continue processing |
| QR decode failure | Fall back to filename parser |
| OCR low confidence | Log warning, fall back to filename parser |
| FFmpeg not found | Exit with message (shouldn't happen in Docker) |

All errors use structured logging. In normal mode, users see clean messages. With `--verbose`, full tracebacks and debug info are shown.

## 7. Testing Strategy

### Unit Tests
- **FilenameParser**: Parameterized tests with dozens of filename variations
- **QRDetector**: Tests using pre-generated test images with known QR codes
- **Organizer**: Tests using temporary directories with mock files
- **Reporter**: Tests comparing output against expected strings

### Integration Tests
- **CLI tests**: Using Click's `CliRunner` to test full command execution
- **Docker tests**: Build and run container with test fixture files

### Test Fixtures
- Small (1-second) test video files with QR codes baked in
- Generated programmatically in `conftest.py` using OpenCV to keep the repo small
- Fixture videos are ~50KB each (low resolution, short duration)

### CI Considerations
- Tests run without Docker (unit + integration tests use local Python)
- Docker build and smoke test as a separate CI step
- No GPU required for CI
