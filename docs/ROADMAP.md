# Implementation Roadmap: ClipSort

**Date:** 2026-03-10

---

## Phase Overview

| Phase | Name | Deliverables | Use Cases |
|-------|------|-------------|-----------|
| 1 | Filename Organizer | CLI that organizes clips by filename patterns | UC-1001 through UC-1006, UC-4001 through UC-4003 |
| 2 | QR Code Detection | QR code generation + video QR detection | UC-2001 through UC-2004 |
| 3a | Clapper Board Detection + OCR | Visual slate detection, OCR text extraction | UC-3001, UC-3002 |
| 3b | Video Splitting | Split continuous video at clapper boundaries | UC-3003 |
| 3c | Audio Clap Detection | Audio transient detection as supplementary signal | UC-3004 |
| 4 | Polish & Extensibility | Custom patterns, folder formats, UX improvements | UC-5001, UC-5002 |

Each phase produces a working Docker image that can be used independently. Later phases build on earlier ones without breaking existing functionality.

---

## Phase 1: Filename Organizer

**Goal:** A working CLI tool in Docker that organizes video files into scene folders based on filename patterns.

**This is the immediate need** — the student can use this right away to organize his existing footage named `1a`, `1b`, `1c`, etc.

### Tasks

#### 1.1 Project scaffolding
- Initialize Python project with `pyproject.toml` (using hatchling or setuptools)
- Set up `ruff` for linting
- Set up `pytest` with `conftest.py`
- Create project directory structure
- Create `Makefile` with targets: `test`, `lint`, `build`, `run`

#### 1.2 File Scanner (`scanner.py`)
- Implement `FileScanner` class
- Support flat and recursive directory scanning
- Filter by video file extensions (case-insensitive)
- **Tests:** Empty directory, directory with mixed files, nested directories, case variations in extensions

#### 1.3 Filename Parser (`parser.py`)
- Implement `ClipInfo` dataclass
- Implement `FilenameParser` with built-in patterns:
  - `1a`, `1b`, `12c` (scene + letter take)
  - `1_1`, `2_3` (scene_take numeric)
  - `Scene1_Take2`, `scene_01_take_03` (verbose)
  - `S01T03` (short form)
- Auto-detect which pattern a batch of files uses
- **Tests:** Parameterized tests covering all patterns, edge cases (leading zeros, uppercase/lowercase, non-matching filenames)

#### 1.4 Organizer (`organizer.py`)
- Implement `OrganizePlan` dataclass
- Implement `Organizer.plan()` — builds mapping from source to destination
- Implement `Organizer.execute()` — copies or moves files
- Handle filename conflicts with numeric suffixes
- Folder naming with zero-padded scene numbers
- **Tests:** Plan generation, conflict resolution, copy vs move, dry-run behavior

#### 1.5 Reporter (`reporter.py`)
- Implement summary report (scene count, clips per scene, unsorted count)
- Print to stdout; optionally save to file
- **Tests:** Report content matches expected output for known inputs

#### 1.6 CLI (`cli.py`)
- Implement `organize` command with all flags:
  - `--dry-run`, `--move`, `--recursive`, `--verbose`, `--report-file`
- Help text for all commands and options
- Progress display (file X of Y)
- Proper exit codes
- **Tests:** CLI integration tests using Click's `CliRunner`

#### 1.7 Docker packaging
- Create `Dockerfile` (multi-stage build)
- Create `docker-compose.yml` for convenience
- Test that `docker run` works with mounted volumes
- **Tests:** Docker build succeeds; smoke test with fixture files

#### 1.8 Wrapper and build scripts
- Create `clipsort` (bash) and `clipsort.bat` wrapper scripts that translate local paths to Docker volume mounts and pass all arguments through
- Create `build` (bash) and `build.bat` scripts that build the Docker image
- Wrapper script checks for the Docker image and prints a helpful message if it's missing
- No dependency on `make` for end-user workflows
- **Tests:** Wrapper invocation with `--dry-run` produces correct output; missing-image warning is shown

### Phase 1 Acceptance Criteria
- [ ] `clipsort organize ./raw ./organized` correctly sorts files named `1a.mp4`, `1b.mp4`, `2a.mp4` into `scene_01/` and `scene_02/`
- [ ] `--dry-run` shows the plan without moving files
- [ ] `--move` moves instead of copying
- [ ] `--recursive` finds files in subdirectories
- [ ] Unrecognized filenames go to `unsorted/`
- [ ] Summary report is printed after organization
- [ ] Docker container runs and produces correct output
- [ ] `./clipsort` wrapper works on macOS/Linux; `clipsort.bat` works on Windows
- [ ] `./build` and `build.bat` build the Docker image without requiring `make`
- [ ] All unit and integration tests pass
- [ ] `ruff` reports no linting issues

### Use Cases Covered
UC-1001, UC-1002, UC-1003, UC-1004, UC-1005, UC-1006, UC-4001, UC-4002, UC-4003, UC-4004, UC-4005

---

## Phase 2: QR Code Detection

**Goal:** Generate QR codes for clapper boards and detect them in video files to auto-organize clips.

**Prerequisite:** Phase 1 complete.

### Tasks

#### 2.1 QR Code Generator (`qr_generate.py`)
- Generate QR code images with structured scene/take data
- Single QR code generation (PNG output)
- Batch generation with printable PDF output
- QR codes are large enough for on-camera readability
- **Tests:** Generated QR codes decode back to correct data; PDF is valid

#### 2.2 QR Code Detector (`qr_detect.py`)
- Frame extraction from video using OpenCV
- QR code scanning using pyzbar
- Configurable scan window (first N seconds) and sample rate
- Parse decoded QR data and validate schema
- **Tests:** Detection on test videos with embedded QR frames; no false positives on videos without QR codes

#### 2.3 Detection chain integration
- Wire QR detector into the organize pipeline
- Implement fallback: QR detection -> filename parsing -> unsorted
- Report which detection method was used for each file
- Add `detect` CLI command
- **Tests:** Mixed input with some QR-coded videos and some filename-only videos

#### 2.4 Test fixture generation
- Script to create small test videos with QR codes baked into first frames
- Add to `conftest.py` as session-scoped fixtures
- **Tests:** Fixture generation is deterministic and reproducible

#### 2.5 Docker update
- Add `pyzbar` and `libzbar0` to Docker image
- Add `qrcode`, `fpdf2` to dependencies
- Verify image size stays under 2 GB
- **Tests:** Docker smoke test with QR detection

### Phase 2 Acceptance Criteria
- [ ] `clipsort qr-generate --scene 1 --take 1` produces a valid QR code PNG
- [ ] `clipsort qr-generate --scenes 5 --takes 3` produces a printable PDF
- [ ] `clipsort detect ./raw ./organized` detects QR codes in test videos
- [ ] Fallback to filename-based organization works when no QR is found
- [ ] Report shows detection method used per file
- [ ] All Phase 1 tests still pass (no regressions)

### Use Cases Covered
UC-2001, UC-2002, UC-2003, UC-2004

---

## Phase 3a: Clapper Board Detection + OCR

**Goal:** Detect physical clapper boards in video frames and read scene/take info via OCR, adding OCR as a detection method in the existing chain: QR → OCR → Filename → Unsorted.

**Prerequisite:** Phase 2 complete.

### Tasks

#### 3a.1 OCR abstraction layer (`ocr.py`)
- `OCREngine` protocol with `recognize(image) -> list[OCRResult]`
- `OCRResult` dataclass: text, confidence, bounding box
- `TesseractEngine` implementation wrapping pytesseract
- **Tests:** OCR on synthetic images with drawn text

#### 3a.2 Clapper board visual detection (`clapper_detect.py`)
- Detect high-contrast rectangular regions in sampled frames (Canny + contours)
- Score candidates by aspect ratio, area, and contrast
- Preprocess best candidate with CLAHE contrast enhancement
- Parse OCR output for scene/take patterns ("SCENE 3", "SC 3 TK 2", "S3T2", etc.)
- **Tests:** Slate detection on synthetic frames, OCR text parsing with known patterns

#### 3a.3 Detection chain update
- Add clapper OCR to detect command chain: QR → OCR → Filename → Unsorted
- `--mode` flag: `auto` (default), `qr`, `ocr`
- Add Tesseract system packages to Docker image
- **Tests:** CLI integration tests with --mode flag, full chain with mixed methods

### Phase 3a Acceptance Criteria
- [x] `OCREngine` protocol with swappable backends (Tesseract implemented)
- [x] Clapper board regions detected in high-contrast frames
- [x] OCR text parsed for scene/take patterns (SCENE N, SC N, S3T2, etc.)
- [x] `--mode auto|qr|ocr` flag on `detect` command
- [x] Fallback chain (QR → OCR → Filename) works correctly
- [x] Tesseract added to Docker image (~50MB)
- [x] All Phase 1 and Phase 2 tests still pass

### Use Cases Covered
UC-3001, UC-3002

---

## Phase 3b: Video Splitting (Planned)

**Goal:** Split continuous recordings at clapper board boundaries using FFmpeg.

**Prerequisite:** Phase 3a complete.

### Tasks

#### 3b.1 Video splitter (`splitter.py`)
- Accept a list of split timestamps
- Use FFmpeg with stream copy to split video
- Name output clips based on detected scene/take info
- Handle edge cases (split at very beginning/end, single-scene video)
- **Tests:** Splitting a test video at known timestamps produces correct segments

#### 3b.2 `split` CLI command
- Implement `clipsort split <input-file> <output-dir>`
- Options: `--mode qr|ocr|auto`, `--scan-seconds`, `--precise`
- Wire together detection + splitting pipeline
- **Tests:** End-to-end split test with a multi-scene test video

### Use Cases Covered
UC-3003

---

## Phase 3c: Audio Clap Detection (Planned)

**Goal:** Detect audible clapper "clap" sounds as a supplementary detection signal.

**Prerequisite:** Phase 3a complete.

### Tasks

#### 3c.1 Audio clap detection
- Extract audio track using FFmpeg
- Detect sharp transient peaks using librosa
- Correlate audio claps with visual detections
- **Tests:** Clap detection on test audio with known clap positions

#### 3c.2 Docker update
- Add librosa and audio dependencies
- Optimize image size
- **Tests:** Docker smoke test with audio detection

### Use Cases Covered
UC-3004

---

## Phase 4: Polish & Extensibility

**Goal:** Add power-user features, improve UX, and harden the tool for wider use.

**Prerequisite:** Phase 3 complete.

### Tasks

#### 4.1 Custom filename patterns (`UC-5001`)
- Accept `--pattern '{scene}_{take}'` flag
- Convert pattern to regex with named groups
- Validate pattern has `{scene}` placeholder
- **Tests:** Custom patterns match expected filenames; invalid patterns produce errors

#### 4.2 Custom folder naming (`UC-5002`)
- Accept `--folder-format 'Scene {scene}'` flag
- Support zero-padding format specifiers
- **Tests:** Output folders match expected names

#### 4.3 Configuration file support
- Support `.clipsort.yaml` config file in the input directory
- Allows setting defaults for all CLI flags
- CLI flags override config file values
- **Tests:** Config file values are applied; CLI overrides work

#### 4.4 UX improvements
- Colored terminal output (if terminal supports it)
- Progress bar for long-running operations (using `rich` or `tqdm`)
- `--json` flag for machine-readable output
- Improved error messages with suggestions

#### 4.5 Documentation
- `--help` text polished for all commands
- `clipsort --version` shows version
- Usage examples in help text

### Phase 4 Acceptance Criteria
- [ ] Custom patterns work for non-standard naming
- [ ] Custom folder formats produce correct directory names
- [ ] Config file support works
- [ ] All previous phase tests still pass

### Use Cases Covered
UC-5001, UC-5002

---

## Testing Strategy Across Phases

### Test Pyramid

```
         /  E2E (Docker)   \        <- Few, slow, high confidence
        / Integration (CLI)  \      <- Moderate, medium speed
       /   Unit (components)   \    <- Many, fast, focused
```

### Regression Protection

Every phase includes:
1. **New tests** for new functionality
2. **Existing tests** must continue to pass
3. **CI runs all tests** before any merge

### Test Infrastructure

- `conftest.py` creates temporary directories with test files
- Video fixtures are generated programmatically (small, deterministic)
- Markers for slow tests (`@pytest.mark.slow`) to enable fast feedback loops
- Docker tests are separate and marked (`@pytest.mark.docker`)

### Running Tests

```bash
# All tests (fast)
make test

# Including slow tests
make test-all

# Docker tests (requires built image)
make test-docker

# With coverage
make test-coverage
```

---

## Estimated Complexity

| Phase | Relative Effort | Key Risk |
|-------|-----------------|----------|
| Phase 1 | Low | None — straightforward file operations |
| Phase 2 | Medium | QR detection reliability on real-world footage |
| Phase 3 | High | OCR accuracy on handwritten slates; Docker image size |
| Phase 4 | Low | None — incremental features |

Phase 1 is the immediate priority and can be completed quickly. Phase 2 is a natural next step that enables a much better production workflow. Phase 3 is the most ambitious and can be deferred based on the student's needs. Phase 4 is ongoing polish.
