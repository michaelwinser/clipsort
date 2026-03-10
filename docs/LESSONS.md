# ClipSort Learning Guide

A structured curriculum for building ClipSort from scratch. Each lesson teaches computer science concepts through hands-on coding exercises that contribute to the real, working tool. By the end, you'll have both the tool **and** the skills to build others like it.

**How to use this guide:** Work through the lessons in order. Each one builds on the previous. For any exercise, you can paste the exercise prompt into an LLM (like Claude) and ask it to coach you through the solution step by step — don't ask it to write the code for you; ask it to *guide* you.

**Prerequisites:** Basic Python familiarity (variables, `print()`, `if/else`). If you're coming from Java (AP CS A), Python will feel familiar — the concepts are the same, the syntax is simpler.

---

## Module 1: Foundations — Files, Strings, and Patterns

*AP CS alignment: strings, conditionals, loops, methods, data types*

### Lesson 1.1: Working with Files and Paths

**Concepts:** File systems, paths, file extensions, the `pathlib` module

**Background reading:** In Python, `pathlib.Path` is the modern way to work with files and directories. It replaces messy string concatenation (`"/Users/" + name + "/videos"`) with clean, object-oriented code.

**Exercises:**

**Exercise 1.1a — Explore pathlib**
```
Write a Python script that:
1. Creates a Path object for the current directory
2. Prints every file in the directory
3. For each file, prints its name, its extension, and its size in bytes

Hint: Look at Path.iterdir(), Path.name, Path.suffix, and Path.stat()
```

**Exercise 1.1b — Filter by extension**
```
Write a function called `find_video_files` that:
- Takes a directory path (string or Path) as input
- Returns a list of Path objects for files with video extensions
  (.mp4, .mov, .mkv, .avi)
- Handles extensions case-insensitively (so .MP4 works too)
- Skips directories and non-video files

Test it: create a temporary folder with some .txt and .mp4 files and verify
your function finds only the videos.
```

**Exercise 1.1c — Recursive scanning**
```
Extend `find_video_files` to accept an optional `recursive` parameter
(default False). When True, it should find video files in all
subdirectories too.

Hint: Path has both .iterdir() and .rglob() methods. Which one helps here?
```

**Key concept — why this matters for ClipSort:** The very first thing our tool does is find all the video files in a directory. This function becomes `FileScanner.scan()` in the real codebase.

---

### Lesson 1.2: Parsing Filenames with String Methods

**Concepts:** String methods, splitting, slicing, type conversion

**Background reading:** Parsing means extracting structured information from unstructured text. Your video files are named `1a.mp4`, `1b.mp4`, `2a.mp4` — the scene number and take letter are *encoded* in the filename. Parsing is how we decode them.

**Exercises:**

**Exercise 1.2a — Manual parsing**
```
Write a function `parse_simple` that takes a filename like "1a.mp4" and
returns a tuple (scene_number, take_letter). Examples:

  parse_simple("1a.mp4")   -> (1, "a")
  parse_simple("12c.mov")  -> (12, "c")
  parse_simple("3b.mkv")   -> (3, "b")

Use only basic string methods — no regex yet.
Hint: First strip the extension. Then the last character is the take letter,
and everything before it is the scene number.

What should your function do if the filename doesn't match this pattern?
(e.g., "notes.txt" or "behind_the_scenes.mp4")
```

**Exercise 1.2b — Multiple formats**
```
Extend your parser to handle these additional formats:
  "Scene1_Take2.mp4"  -> (1, 2)
  "S01T03.mp4"        -> (1, 3)
  "1_2.mp4"           -> (1, 2)

Write a function `parse_filename` that tries each format and returns the
first match, or None if no format matches.

Think about: how do you structure code that tries multiple approaches
in sequence? (This is the "chain of responsibility" pattern.)
```

**Key concept — data extraction:** Turning a filename string into structured data (scene number + take) is a core programming skill. It shows up everywhere: parsing URLs, reading CSV files, processing user input.

---

### Lesson 1.3: Regular Expressions

**Concepts:** Pattern matching, regex syntax, capture groups

**Background reading:** Regular expressions (regex) are a mini-language for describing text patterns. Instead of writing custom string-slicing code for each filename format, one regex pattern can do it all. They're powerful but can be cryptic — start simple.

**Exercises:**

**Exercise 1.3a — First regex**
```
Import Python's `re` module. Write a regex pattern that matches filenames
like "1a", "2b", "12c" and captures the scene number and take letter
separately.

Use re.match() and .group() to extract the pieces.

Hint: \d+ matches one or more digits. [a-z] matches a single lowercase letter.
Parentheses () create "capture groups" that let you extract pieces.
```

**Exercise 1.3b — Pattern library**
```
Create a list of (name, pattern) pairs for all four filename formats:
  1. "1a" style:        r'^(\d+)([a-z])'
  2. "1_2" style:       r'^(\d+)[_-](\d+)'
  3. "Scene1_Take2":    r'^[Ss]cene[_\s]?(\d+)[_\s]?[Tt]ake[_\s]?(\d+)'
  4. "S01T03":          r'^[Ss](\d+)[Tt](\d+)'

Write a function that tries each pattern against a filename and returns
the first match. Test it with at least 2 examples per pattern.

Challenge: What does [_\s]? mean? Break it down character by character.
```

**Exercise 1.3c — Edge cases**
```
What happens with these inputs? Write tests to verify:
  - "1A.mp4"  (uppercase take letter)
  - "01a.mp4" (leading zero)
  - "1.mp4"   (no take letter)
  - ""         (empty string)
  - "scene1_take2.MP4" (lowercase "scene", uppercase extension)

Fix your parser to handle these gracefully.
```

**Key concept — regex vs. manual parsing:** You've now done both. Regex is more concise for complex patterns, but manual parsing can be clearer for simple cases. Good engineers choose the right tool for the job.

---

### Lesson 1.4: Data Classes and Structured Data

**Concepts:** Classes, data classes, type hints, `None` as a sentinel value

**Background reading:** In Java (AP CS A), you'd create a class with instance variables, a constructor, and getters. Python's `@dataclass` gives you all of that in just a few lines. It's how we represent structured data cleanly.

**Exercises:**

**Exercise 1.4a — Your first dataclass**
```
from dataclasses import dataclass

Create a ClipInfo dataclass with these fields:
  - scene: int          (required)
  - take: int or str    (optional, default None)
  - confidence: float   (default 1.0)
  - method: str         (default "filename")

Create a few instances and print them. Notice how Python auto-generates
__repr__ and __eq__ for you.

Java comparison: this replaces a class with a constructor, toString(),
equals(), and getters — all in about 5 lines.
```

**Exercise 1.4b — Refactor the parser**
```
Update your parse_filename function to return a ClipInfo object instead
of a tuple. Return None when no pattern matches.

Before: parse_filename("1a.mp4") -> (1, "a")
After:  parse_filename("1a.mp4") -> ClipInfo(scene=1, take="a", method="filename")

Why is this better than returning a tuple? Think about what happens when
you add more fields later.
```

**Key concept — AP CS connection:** This is the same OOP you're learning in AP CS A, but Python makes it lighter. The idea is identical: bundle related data together into a meaningful type.

---

## Module 2: Building the Organizer

*AP CS alignment: lists, dictionaries, file I/O, algorithm design, testing*

### Lesson 2.1: Planning Before Executing

**Concepts:** Separation of concerns, two-phase operations (plan then execute), defensive programming

**Background reading:** A well-designed program separates *deciding what to do* from *doing it*. ClipSort first builds a plan (a list of "move file X to folder Y" instructions), then executes it. This makes dry-run mode trivial and testing easy.

**Exercises:**

**Exercise 2.1a — The OrganizePlan**
```
Create a dataclass called OrganizePlan with:
  - mappings: list of (source_path, destination_path) tuples
  - unsorted: list of paths that couldn't be categorized

Write a function `build_plan` that:
  1. Takes a list of video file paths and an output directory path
  2. Parses each filename using your parser from Module 1
  3. For files with a detected scene: maps them to output_dir/scene_XX/filename
  4. For files without a match: adds them to the unsorted list
  5. Returns an OrganizePlan

Do NOT copy or move any files — just build the plan.
```

**Exercise 2.1b — Conflict detection**
```
What if two files would end up with the same destination path?
(e.g., two different files both named "1a.mp4" from different subdirectories)

Add conflict detection to build_plan. When a conflict is found, modify
the destination filename by appending _2, _3, etc. before the extension.

"1a.mp4" -> "scene_01/1a.mp4"       (first file, no conflict)
"1a.mp4" -> "scene_01/1a_2.mp4"     (second file with same name)
```

**Exercise 2.1c — Execute the plan**
```
Write a function `execute_plan` that:
  1. Takes an OrganizePlan and a `move` boolean (default False)
  2. Creates any needed directories
  3. Copies (or moves if move=True) each file to its destination
  4. Returns the number of files processed

Use shutil.copy2 (preserves metadata) and shutil.move.
Create needed directories with Path.mkdir(parents=True, exist_ok=True).
```

**Key concept — plan/execute separation:** This pattern appears everywhere in software. Database migrations, deployment scripts, even video games (compute the frame, then render it). It makes code testable and predictable.

---

### Lesson 2.2: Writing Tests with pytest

**Concepts:** Unit testing, test fixtures, assertions, test-driven development

**Background reading:** Tests are code that verifies other code works correctly. Every professional software project has tests. Writing tests *before* or *alongside* your code (not after) catches bugs early and gives you confidence to make changes.

**Exercises:**

**Exercise 2.2a — Your first test**
```
Create a file called test_parser.py. Write tests for your filename parser:

  import pytest
  from clipsort.parser import parse_filename, ClipInfo

  def test_simple_scene_letter():
      result = parse_filename("1a.mp4")
      assert result is not None
      assert result.scene == 1
      assert result.take == "a"

  def test_no_match_returns_none():
      result = parse_filename("random_file.txt")
      assert result is None

Run with: python -m pytest test_parser.py -v

The -v flag shows each test name and whether it passed or failed.
```

**Exercise 2.2b — Parameterized tests**
```
pytest lets you run the same test with different inputs using
@pytest.mark.parametrize:

  @pytest.mark.parametrize("filename,expected_scene,expected_take", [
      ("1a.mp4", 1, "a"),
      ("2b.mov", 2, "b"),
      ("12c.mkv", 12, "c"),
      ("Scene1_Take2.mp4", 1, 2),
      ("S01T03.mp4", 1, 3),
  ])
  def test_parse_filename(filename, expected_scene, expected_take):
      result = parse_filename(filename)
      assert result.scene == expected_scene
      assert result.take == expected_take

Add at least 10 test cases covering all four filename patterns,
edge cases, and invalid inputs.
```

**Exercise 2.2c — Testing the organizer with temporary directories**
```
pytest provides a `tmp_path` fixture that gives you a clean temporary
directory for each test:

  def test_build_plan_groups_by_scene(tmp_path):
      # Create test files
      input_dir = tmp_path / "input"
      input_dir.mkdir()
      (input_dir / "1a.mp4").touch()
      (input_dir / "1b.mp4").touch()
      (input_dir / "2a.mp4").touch()

      output_dir = tmp_path / "output"

      plan = build_plan(list(input_dir.iterdir()), output_dir)

      # Verify scene 1 has 2 files, scene 2 has 1
      scene_1_files = [s for s, d in plan.mappings if "scene_01" in str(d)]
      assert len(scene_1_files) == 2

Write tests for:
  - Files are correctly grouped by scene
  - Unsorted files are captured
  - Conflicts are resolved
  - execute_plan actually creates the files
```

**Key concept — the test pyramid:** Unit tests (fast, test one function) form the base. Integration tests (test multiple components together) are in the middle. End-to-end tests (test the whole app) are at the top. Write many unit tests, fewer integration tests.

---

### Lesson 2.3: Building the CLI with Click

**Concepts:** Command-line interfaces, argument parsing, decorators, user experience

**Background reading:** A CLI (command-line interface) is how users interact with our tool. Python's `click` library makes it easy to define commands, arguments, and options using decorators — special annotations that modify a function's behavior.

**Exercises:**

**Exercise 2.3a — Hello Click**
```
Install click: pip install click

Write a simple CLI:

  import click

  @click.command()
  @click.argument("name")
  def hello(name):
      click.echo(f"Hello, {name}!")

  if __name__ == "__main__":
      hello()

Run it: python hello.py World
Run it: python hello.py --help

Notice how --help is automatically generated. This is why we use a
framework instead of parsing sys.argv manually.
```

**Exercise 2.3b — The organize command**
```
Build the real `organize` command:

  @click.command()
  @click.argument("input_dir", type=click.Path(exists=True))
  @click.argument("output_dir", type=click.Path())
  @click.option("--dry-run", is_flag=True, help="Preview without moving files")
  @click.option("--move", is_flag=True, help="Move files instead of copying")
  @click.option("--recursive", "-r", is_flag=True, help="Scan subdirectories")
  def organize(input_dir, output_dir, dry_run, move, recursive):
      ...

Wire it up to your FileScanner, FilenameParser, and Organizer.
In dry-run mode, print the plan but don't execute it.

Test with real video files (or just .txt files renamed to .mp4 for now).
```

**Exercise 2.3c — Testing the CLI**
```
Click provides CliRunner for testing CLIs without actually running them
in a subprocess:

  from click.testing import CliRunner

  def test_organize_dry_run(tmp_path):
      runner = CliRunner()
      input_dir = tmp_path / "input"
      input_dir.mkdir()
      (input_dir / "1a.mp4").touch()

      output_dir = tmp_path / "output"

      result = runner.invoke(organize, [
          str(input_dir), str(output_dir), "--dry-run"
      ])

      assert result.exit_code == 0
      assert "scene_01" in result.output

Write tests for each CLI flag combination.
```

**Key concept — decorators:** In Python, `@click.command()` is a decorator. It wraps your function with extra behavior (argument parsing, help generation). In AP CS terms, it's like implementing an interface — your function provides the logic, the framework provides the plumbing.

---

### Lesson 2.4: Docker Packaging

**Concepts:** Containers, Dockerfiles, images, volumes, reproducible environments

**Background reading:** Docker packages your application with all its dependencies into a container — a lightweight, isolated environment that runs the same on any machine. Instead of telling someone "install Python 3.12, then pip install these 5 things, then make sure ffmpeg is on your PATH..." you give them one command: `docker run clipsort`.

**Exercises:**

**Exercise 2.4a — Your first Dockerfile**
```
Create a file called Dockerfile:

  FROM python:3.12-slim

  WORKDIR /app
  COPY pyproject.toml .
  COPY src/ src/

  RUN pip install --no-cache-dir .

  ENTRYPOINT ["python", "-m", "clipsort"]

Build it: docker build -t clipsort .
Run it:   docker run clipsort --help

Concepts to understand:
  - FROM: base image (someone else's pre-built container with Python)
  - WORKDIR: like `cd` inside the container
  - COPY: bring files from your machine into the container
  - RUN: execute a command during build
  - ENTRYPOINT: what runs when someone does `docker run`
```

**Exercise 2.4b — Volume mounts**
```
The container is isolated — it can't see your files by default.
Volume mounts (-v) bridge your filesystem into the container:

  docker run --rm \
    -v /path/to/your/videos:/input:ro \
    -v /path/to/output:/output \
    clipsort organize /input /output

The :ro means read-only — the container can read but not modify your
source videos. This is a safety measure.

Test this with a directory of test files.
```

**Exercise 2.4c — Docker Compose for convenience**
```
Create a docker-compose.yml that makes the volume mounts easier:

  services:
    clipsort:
      build: .
      volumes:
        - ./test_videos:/input:ro
        - ./output:/output

Run with: docker compose run clipsort organize /input /output

This is easier to remember and share than long docker run commands.
```

**Key concept — reproducibility:** Docker solves "works on my machine." Your tool will work the same on macOS, Windows, or Linux. This matters for collaboration — anyone can use your tool without debugging their Python installation.

---

## Module 3: QR Code Detection

*AP CS alignment: 2D arrays (images), algorithms, binary data, encoding/decoding*

### Lesson 3.1: Generating QR Codes

**Concepts:** Data encoding, image generation, structured data formats (JSON)

**Background reading:** QR codes encode data (text, URLs, JSON) into a visual pattern that cameras can read. For ClipSort, we print QR codes on clapper boards that encode the scene and take number. The camera captures it, and our tool reads it from the video.

**Exercises:**

**Exercise 3.1a — Generate a QR code**
```
Install: pip install qrcode[pil]

  import qrcode
  import json

  data = json.dumps({"v": 1, "scene": 1, "take": 1})
  img = qrcode.make(data)
  img.save("scene1_take1.png")

Generate QR codes for scene 1 takes 1-3. Open them in an image viewer.
Scan them with your phone's camera to verify they decode correctly.

Think about: why JSON instead of just "1-1"? What if we add more fields
later (like "project" or "date")?
```

**Exercise 3.1b — Batch generation**
```
Write a function that generates QR codes for all scene/take combinations:

  def generate_qr_codes(scenes: int, takes: int, output_dir: Path):
      for scene in range(1, scenes + 1):
          for take in range(1, takes + 1):
              ...

This is a nested loop — the same concept from AP CS where you traverse
a 2D array. Here, scenes are rows and takes are columns.

Generate codes for 5 scenes x 3 takes = 15 QR codes.
```

**Exercise 3.1c — Printable PDF sheet**
```
Install: pip install fpdf2

Create a PDF that arranges all QR codes on a printable page with labels.
Each QR code should be ~3cm x 3cm (large enough to read on camera)
with "Scene X / Take Y" printed below it.

Hint: fpdf2's FPDF class has .image() and .text() methods.
Lay them out in a grid: 3 across, multiple rows.

Print the PDF and test: can your phone's camera read the QR codes
from the printed page?
```

**Key concept — encoding and decoding:** QR codes are a physical form of data encoding — the same idea as UTF-8 for text or MP4 for video. Data goes in (JSON string), gets encoded (QR pattern), and can be decoded back to the original data. Lossy encoding (like JPEG) loses some data; QR codes are lossless.

---

### Lesson 3.2: Reading Video Frames with OpenCV

**Concepts:** Video as a sequence of images, frame extraction, sampling strategies

**Background reading:** A video file is essentially thousands of images (frames) played in sequence. At 30fps, a 10-second clip has 300 frames. OpenCV lets us open a video and extract individual frames as arrays of pixel values.

**Exercises:**

**Exercise 3.2a — Extract a frame**
```
Install: pip install opencv-python-headless

  import cv2

  cap = cv2.VideoCapture("your_video.mp4")
  success, frame = cap.read()
  if success:
      cv2.imwrite("frame_0.jpg", frame)
      print(f"Frame shape: {frame.shape}")  # (height, width, channels)
  cap.release()

Extract the first frame of a video and save it. Look at the shape —
it's a 3D array (height x width x 3 color channels). This is a
2D array concept from AP CS, extended to 3 dimensions.
```

**Exercise 3.2b — Sample frames from a time range**
```
Write a function that extracts N evenly-spaced frames from the first
S seconds of a video:

  def sample_frames(video_path: Path, seconds: int = 10,
                    samples_per_second: int = 2) -> list[np.ndarray]:
      cap = cv2.VideoCapture(str(video_path))
      fps = cap.get(cv2.CAP_PROP_FPS)
      total_frames = int(seconds * fps)
      step = int(fps / samples_per_second)
      ...

Return a list of frames. Test by saving them as numbered JPEGs.

Think about: why sample instead of checking every frame? If a video is
30fps and we need to check 10 seconds, that's 300 frames. Sampling at
2fps gives us 20 frames — 15x less work for the same result.
```

**Exercise 3.2c — Video metadata**
```
OpenCV can read video properties:

  cap = cv2.VideoCapture("video.mp4")
  fps = cap.get(cv2.CAP_PROP_FPS)
  frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
  width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
  height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
  duration = frame_count / fps

Write a function that returns a dictionary of video properties.
This is useful for reporting and debugging.
```

**Key concept — arrays and images:** An image is a 2D array of pixels. Each pixel has 3 values (blue, green, red in OpenCV). Video processing is fundamentally array manipulation — the same concepts from AP CS applied to visual data.

---

### Lesson 3.3: Detecting QR Codes in Video

**Concepts:** Combining components, detection pipelines, error handling

**Exercises:**

**Exercise 3.3a — QR detection on a single image**
```
Install: pip install pyzbar

  from pyzbar.pyzbar import decode
  from PIL import Image

  img = Image.open("scene1_take1.png")
  results = decode(img)
  for result in results:
      print(result.data.decode("utf-8"))

Test with the QR codes you generated in Lesson 3.1.
What does the result object contain besides .data?
```

**Exercise 3.3b — QR detection on video frames**
```
Combine Lessons 3.2 and 3.3a:

  def detect_qr_in_video(video_path: Path) -> ClipInfo | None:
      frames = sample_frames(video_path, seconds=10, samples_per_second=2)
      for frame in frames:
          results = decode(frame)
          if results:
              data = json.loads(results[0].data.decode("utf-8"))
              return ClipInfo(
                  scene=data["scene"],
                  take=data.get("take"),
                  confidence=1.0,
                  method="qr"
              )
      return None

Test: create a short video (even a screen recording showing a QR code)
and verify detection works.
```

**Exercise 3.3c — The detection chain**
```
Build the fallback chain that tries multiple detection methods:

  def detect_clip_info(video_path: Path) -> ClipInfo | None:
      # Try QR detection first
      info = detect_qr_in_video(video_path)
      if info:
          return info

      # Fall back to filename parsing
      info = parse_filename(video_path.name)
      if info:
          return info

      # Nothing worked
      return None

This is the "chain of responsibility" pattern. Each method either
succeeds (short-circuits) or passes to the next one.

Write tests for: QR-only video, filename-only video, video with both,
video with neither.
```

**Key concept — algorithm design:** The detection chain is an algorithm you designed. It has a clear input (video file), a defined process (try methods in order), and a guaranteed output (ClipInfo or None). This kind of systematic thinking is what AP CS teaches.

---

## Module 4: Clapper Board Detection (Advanced)

*AP CS alignment: algorithm design, image processing, working with external libraries*

### Lesson 4.1: Image Processing Basics

**Concepts:** Color spaces, thresholding, contour detection

**Exercises:**

**Exercise 4.1a — Grayscale and thresholding**
```
Convert a frame to grayscale and apply binary thresholding:

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
  cv2.imwrite("binary.jpg", binary)

Try different threshold values (64, 128, 192). What happens?
A clapper board has very high contrast (black and white) — how could
thresholding help us find it?
```

**Exercise 4.1b — Finding rectangles**
```
Use contour detection to find rectangular shapes in a frame:

  contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)

  for contour in contours:
      # Approximate the contour to a polygon
      peri = cv2.arcLength(contour, True)
      approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

      # Rectangles have 4 vertices
      if len(approx) == 4:
          x, y, w, h = cv2.boundingRect(approx)
          print(f"Rectangle at ({x},{y}), size {w}x{h}")

Draw the detected rectangles on the frame and save it.
Which rectangle is the clapper board? How can you filter by size or
aspect ratio?
```

**Exercise 4.1c — Scoring candidates**
```
Write a function that scores how likely a rectangle is to be a clapper
board. Consider:
  - Size: should be a significant portion of the frame (>5% of area)
  - Aspect ratio: clapper boards are roughly 4:3
  - Position: usually held in the upper half of frame
  - Contrast: the region inside should have high contrast

Score each candidate 0-100 and return the best one.
This is an algorithm design exercise — there's no single right answer.
Try different heuristics and see what works.
```

**Key concept — heuristics:** When there's no exact algorithm for a problem (like "is this a clapper board?"), we use heuristics — reasonable rules of thumb that work most of the time. Balancing multiple heuristics is a real-world skill that goes beyond textbook algorithms.

---

### Lesson 4.2: OCR — Reading Text from Images

**Concepts:** OCR (Optical Character Recognition), preprocessing, confidence scores

**Exercises:**

**Exercise 4.2a — Basic OCR**
```
Install: pip install paddleocr

  from paddleocr import PaddleOCR

  ocr = PaddleOCR(use_angle_cls=True, lang='en')
  result = ocr.ocr("your_image.jpg")

  for line in result[0]:
      text = line[1][0]
      confidence = line[1][1]
      print(f"{text} (confidence: {confidence:.2f})")

Try it on:
  - A photo of a clapper board
  - A screenshot of typed text
  - A photo of handwriting

How does accuracy compare across these?
```

**Exercise 4.2b — Preprocessing for better OCR**
```
OCR works better on clean, high-contrast images. Apply these
preprocessing steps to a clapper board image:

  1. Convert to grayscale
  2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization):
     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
     enhanced = clahe.apply(gray)
  3. Apply slight blur to reduce noise:
     blurred = cv2.GaussianBlur(enhanced, (3,3), 0)

Compare OCR results before and after preprocessing.
Save intermediate images to see what each step does.
```

**Exercise 4.2c — Extracting scene/take from OCR text**
```
OCR returns raw text. Write a function that searches the text for
scene and take numbers:

  def extract_scene_info(ocr_text: list[str]) -> ClipInfo | None:
      for text in ocr_text:
          # Look for patterns like "SCENE 3", "SC 3", "S3"
          scene_match = re.search(r'(?:scene|sc|s)\s*(\d+)', text, re.I)
          take_match = re.search(r'(?:take|tk|t)\s*(\d+)', text, re.I)
          ...

Handle messy OCR output: extra spaces, misread characters
(0 vs O, 1 vs l), partial text.
```

**Key concept — working with imperfect data:** Real-world data is messy. OCR isn't 100% accurate. Your code needs to handle uncertainty — that's why we have confidence scores and fallback chains. This is very different from textbook problems where input is always clean.

---

### Lesson 4.3: Video Splitting with FFmpeg

**Concepts:** Subprocesses, command-line tools, stream processing

**Exercises:**

**Exercise 4.3a — Running external commands**
```
Python can run other programs using subprocess:

  import subprocess

  result = subprocess.run(
      ["ffmpeg", "-version"],
      capture_output=True, text=True
  )
  print(result.stdout)

FFmpeg is a separate program (not a Python library). We call it as a
subprocess — like calling a function in another language. This is
a common pattern: use the best tool for each job.
```

**Exercise 4.3b — Splitting a video**
```
Write a function that splits a video at given timestamps:

  def split_video(input_path: Path, output_dir: Path,
                  segments: list[tuple[float, float, str]]):
      """
      segments: list of (start_seconds, end_seconds, output_name)
      """
      for start, end, name in segments:
          output_path = output_dir / f"{name}.mp4"
          subprocess.run([
              "ffmpeg", "-i", str(input_path),
              "-ss", str(start), "-to", str(end),
              "-c", "copy",  # no re-encoding = fast
              str(output_path)
          ], check=True)

Test by splitting a video into 3 equal parts.
```

**Exercise 4.3c — End-to-end split pipeline**
```
Combine everything: detect clapper boards in a long video, then split
at those points:

  1. Sample frames throughout the entire video (not just the start)
  2. Detect QR codes or clapper boards at each sample point
  3. Record timestamps where detection occurs
  4. Split the video at those timestamps
  5. Name each segment based on detected scene/take info

This is the most complex exercise — it combines file I/O, image
processing, detection algorithms, and subprocess management.
```

**Key concept — integration:** The hardest part of software isn't writing individual pieces — it's making them work together. This exercise combines everything you've learned across all modules.

---

## Module 5: Software Engineering Practices

*AP CS alignment: program design, documentation, testing, code organization*

### Lesson 5.1: Project Structure and Packaging

**Concepts:** Modules, packages, `pyproject.toml`, entry points

**Exercises:**

**Exercise 5.1a — Python packages**
```
Reorganize your code into a proper package:

  src/
    clipsort/
      __init__.py      (can be empty)
      cli.py           (Click commands)
      scanner.py       (FileScanner)
      parser.py        (FilenameParser, ClipInfo)
      organizer.py     (Organizer, OrganizePlan)
      reporter.py      (Reporter)

In each module, import only what you need from others:
  from clipsort.parser import ClipInfo, parse_filename

Why organize this way? Each file has a single responsibility.
When you fix a bug in the parser, you know exactly where to look.
```

**Exercise 5.1b — pyproject.toml**
```
Create pyproject.toml — the modern way to define a Python project:

  [project]
  name = "clipsort"
  version = "0.1.0"
  requires-python = ">=3.12"
  dependencies = [
      "click>=8.0",
  ]

  [project.scripts]
  clipsort = "clipsort.cli:main"

Install in development mode: pip install -e .
Now you can run `clipsort` from anywhere.
```

### Lesson 5.2: Writing Good Tests

**Concepts:** Test coverage, fixtures, mocking, CI/CD

**Exercises:**

**Exercise 5.2a — Fixtures with conftest.py**
```
Create tests/conftest.py with shared test fixtures:

  import pytest
  from pathlib import Path

  @pytest.fixture
  def sample_video_dir(tmp_path):
      """Create a directory with sample video files."""
      for name in ["1a.mp4", "1b.mp4", "2a.mp4", "2b.mp4", "notes.txt"]:
          (tmp_path / name).touch()
      return tmp_path

  @pytest.fixture
  def scene_letter_files(tmp_path):
      """Create files using scene+letter naming."""
      files = ["1a.mp4", "1b.mp4", "1c.mp4", "2a.mp4", "2b.mp4", "3a.mp4"]
      for name in files:
          (tmp_path / name).touch()
      return tmp_path, files

Now any test can use these fixtures by name:
  def test_scanner_finds_videos(sample_video_dir):
      scanner = FileScanner()
      videos = scanner.scan(sample_video_dir)
      assert len(videos) == 4  # excludes notes.txt
```

**Exercise 5.2b — Test coverage**
```
Install: pip install pytest-cov

Run: pytest --cov=clipsort --cov-report=term-missing

This shows which lines of your code are NOT covered by any test.
Aim for >90% coverage on parser.py and organizer.py.

Look at the uncovered lines. Are they error handlers? Edge cases?
Write tests that exercise them.
```

**Exercise 5.2c — Makefile for automation**
```
Create a Makefile that automates common tasks:

  .PHONY: test lint build run

  test:
  	pytest tests/ -v

  lint:
  	ruff check src/ tests/

  build:
  	docker build -t clipsort .

  run:
  	docker run --rm -v $(PWD)/test_videos:/input:ro \
  	  -v $(PWD)/output:/output clipsort organize /input /output

Now `make test` runs all tests. `make build` builds the Docker image.
This is how real projects work — one command to do common things.
```

---

## Tips for Working with an LLM Tutor

When using Claude or another LLM to coach you through these exercises:

1. **Don't ask for the answer.** Ask for hints, explanations, and guidance. Say: *"I'm stuck on Exercise 1.2a. I can strip the extension but I don't know how to separate the number from the letter. Can you give me a hint?"*

2. **Share your code.** Paste what you've written so far and ask: *"Here's my attempt at the parser. What am I doing wrong?"* or *"This works but feels messy — how can I improve it?"*

3. **Ask "why" questions.** *"Why do we use `pathlib` instead of string concatenation for paths?"* Understanding the reasoning makes concepts stick.

4. **Ask for analogies.** *"I'm learning about decorators. Can you explain them in terms of Java concepts I already know?"*

5. **Request smaller steps.** If an exercise feels too big, ask: *"Can you break Exercise 2.1a into smaller steps? I don't know where to start."*

6. **Test understanding.** After completing an exercise, ask: *"Can you quiz me on the concepts from this lesson?"*

7. **Connect to AP CS.** Ask: *"How does this relate to what I'm learning in AP CS about [arrays/sorting/OOP]?"*

---

## Concept Map: AP CS Topics in ClipSort

| AP CS Topic | Where It Shows Up in ClipSort |
|---|---|
| Variables & Types | ClipInfo fields, Path objects, strings vs ints |
| Conditionals | Pattern matching fallbacks, error handling |
| Loops | Scanning directories, iterating frames, processing file lists |
| Nested Loops | QR code batch generation (scenes x takes), frame sampling |
| Arrays/Lists | Video frame arrays, file lists, plan mappings |
| 2D Arrays | Image pixel data (height x width x channels) |
| Strings | Filename parsing, regex patterns, QR data encoding |
| Methods/Functions | Every component: `scan()`, `parse()`, `detect()`, `organize()` |
| Classes/OOP | ClipInfo, FileScanner, FilenameParser, Organizer |
| Encapsulation | Each module hides its implementation details |
| Inheritance | Detection chain (common interface, different implementations) |
| Searching | Finding QR codes in frames, finding patterns in filenames |
| Sorting | Organizing files into ordered scene folders |
| Recursion | Recursive directory scanning |
| Testing | pytest throughout every module |
| Algorithm Design | Detection chain, candidate scoring, sampling strategies |
