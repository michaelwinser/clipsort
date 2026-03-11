# ClipSort

Organize video clips into scene folders based on filename patterns, QR codes, or clapper board OCR.

Built as a learning project for student filmmakers and AP CS students. See [`docs/LESSONS.md`](docs/LESSONS.md) for the structured curriculum.

## Quick Start

```bash
# With Docker
docker build -t clipsort .
docker run --rm \
  -v /path/to/videos:/input:ro \
  -v /path/to/output:/output \
  clipsort organize /input /output

# Without Docker
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
clipsort organize ./raw ./organized
```

## Usage

```
clipsort organize [OPTIONS] INPUT_DIR OUTPUT_DIR
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview the plan without copying/moving files |
| `--move` | Move files instead of copying (default: copy) |
| `-r`, `--recursive` | Scan subdirectories for video files |
| `-v`, `--verbose` | Enable debug logging |
| `--report-file PATH` | Save the summary report to a file |

### Supported filename patterns

| Pattern | Example | Detected as |
|---------|---------|-------------|
| Scene + letter | `1a.mp4`, `12c.mov` | Scene 1 take a, Scene 12 take c |
| Scene + take | `1_2.mp4`, `3-1.mkv` | Scene 1 take 2, Scene 3 take 1 |
| Verbose | `Scene1_Take2.mp4` | Scene 1 take 2 |
| Short form | `S01T03.mp4` | Scene 1 take 3 |

Files that don't match any pattern go to an `unsorted/` folder.

### Example

```
$ clipsort organize ./raw ./organized --dry-run

Found 5 video file(s).

--- Dry Run ---
  1a.mp4 -> scene_01/1a.mp4
  1b.mp4 -> scene_01/1b.mp4
  2a.mp4 -> scene_02/2a.mp4
  2b.mp4 -> scene_02/2b.mp4
  behind_the_scenes.mp4 -> unsorted
--- End Dry Run ---

Files processed: 5
Scenes detected: 2
  scene_01: 2 clip(s)
  scene_02: 2 clip(s)
Unsorted: 1 file(s)
```

## Development

```bash
make help       # Show available commands
make test       # Run tests (56 tests)
make lint       # Check code quality with ruff
make test-cov   # Tests with coverage report
make build      # Build Docker image
```

Or run everything in Docker (no local Python install needed):

```bash
docker build --target dev -t clipsort-dev .
docker run --rm clipsort-dev pytest tests/ -v
docker run --rm clipsort-dev ruff check src/ tests/
```

## Project Structure

```
src/clipsort/
  scanner.py      # Find video files in directories
  parser.py       # Extract scene/take from filenames
  organizer.py    # Build and execute file organization plans
  reporter.py     # Generate summary reports
  cli.py          # Click CLI entry point
tests/
  conftest.py     # Shared fixtures (generated, not committed binaries)
  test_*.py       # Tests for each component
docs/
  PRD.md          # Product requirements
  DESIGN.md       # Architecture and component design
  ROADMAP.md      # 4-phase implementation plan
  LESSONS.md      # Learning guide with exercises
```

## Checkpoints

If you're working through the [learning guide](docs/LESSONS.md) and get stuck, checkpoint branches let you skip ahead:

```bash
git checkout checkpoint/module-N   # N = 0, 1, 2, 3, or 4
```

See the Checkpoints section in `docs/LESSONS.md` for details on what each contains.

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Filename Organizer | Done | Parse filenames, organize into scene folders |
| 2. QR Code Detection | Planned | Generate QR codes for clappers, detect in video |
| 3. Clapper Board OCR | Planned | Visual slate detection, OCR, video splitting |
| 4. Polish | Planned | Custom patterns, config files, UX improvements |
