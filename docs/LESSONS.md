# ClipSort Learning Guide

A structured curriculum for building ClipSort from scratch. Each lesson teaches computer science concepts through hands-on coding exercises that contribute to the real, working tool. By the end, you'll have both the tool **and** the skills to build others like it.

**How to use this guide:** Work through the lessons in order. Each one builds on the previous. For any exercise, you can paste the exercise prompt into an LLM (like Claude) and ask it to coach you through the solution step by step — don't ask it to write the code for you; ask it to *guide* you.

**Prerequisites:** Basic Python familiarity (variables, `print()`, `if/else`). If you're coming from Java (AP CS A), Python will feel familiar — the concepts are the same, the syntax is simpler.

---

## Checkpoints: Pick Up Where You Need To

Each module has a **checkpoint branch** — a snapshot of the working code at that module boundary. If you get stuck on a module or want to skip ahead, you can start fresh from any checkpoint:

```bash
git checkout checkpoint/module-N
```

| Checkpoint | What It Contains | Use It When... |
|---|---|---|
| `checkpoint/module-0` | Scaffolding only (pyproject.toml, Makefile, .gitignore, empty src/ and tests/ dirs, Dockerfile skeleton) | You finished Module 0 and want to start coding application logic |
| `checkpoint/module-1` | Scaffolding + scanner + parser + ClipInfo with tests | You want to skip to building the organizer |
| `checkpoint/module-2` | Full Phase 1 (scanner, parser, organizer, reporter, CLI, Docker) with all tests | You want to start QR code work |
| `checkpoint/module-3` | Phase 1 + QR generator + QR detector + detection chain + video fixture infra | You want to start clapper board work |
| `checkpoint/module-4` | Phase 1 + Phase 2 + Phase 3 (clapper detection, OCR, splitter, audio clap detection) | You want to start engineering practices |

**How checkpoints work:** Each branch contains the full, working code for everything up to that point. All tests pass on every checkpoint. You can compare your code against a checkpoint with `git diff checkpoint/module-N` to see what's different.

**Important:** Checkpoints are a safety net, not a shortcut. You'll learn the most by writing the code yourself. But if you're stuck for more than 30 minutes on something mechanical (not conceptual), grab the checkpoint and move on to the interesting stuff.

---

## Module 0: Project Setup and the Software Development Lifecycle

> **Checkpoint:** Starting fresh? Run `git checkout checkpoint/module-0` for a working scaffold to build on.

*Skills: version control, project scaffolding, dependency management, development environments, professional workflow*

This module is arguably the most important one. Knowing how to set up a project from scratch — and how professional developers manage code over time — is a skill you'll use on every project for the rest of your career. Most CS classes skip this entirely, but it's what separates "I can write a function" from "I can build and ship software."

### Lesson 0.1: Version Control with Git

**Concepts:** Repositories, commits, branches, diffs, history, collaboration

**Background reading:** Git tracks every change you make to your code, creating a timeline you can navigate. If you break something, you can go back. If you want to try an experiment, you can create a branch. Every professional software project uses version control — it's not optional.

Think of it like "undo" on steroids: not just one level of undo, but a complete history of every change, who made it, when, and why.

**Exercises:**

**Exercise 0.1a — Your first repository**
```
Create a new directory for ClipSort and initialize it as a git repo:

  mkdir clipsort
  cd clipsort
  git init

Now create a simple file — say, a one-line README.txt that says
"ClipSort - video clip organizer". Then:

  git status          # Shows untracked files
  git add README.txt  # Stage the file (tell git you want to include it)
  git commit -m "Initial commit: add README"

Run `git log` to see your commit. You now have a permanent record of
this change. Even if you delete the file later, git remembers it.

Key commands to understand:
  - git status: "What's changed since my last commit?"
  - git add: "I want to include this change in my next commit"
  - git commit: "Save a snapshot of all staged changes"
  - git log: "Show me the history"
  - git diff: "Show me what changed"
```

**Exercise 0.1b — Making and tracking changes**
```
Edit your README.txt — add a second line describing what ClipSort does.
Now explore the workflow:

  git status          # Shows README.txt is "modified"
  git diff            # Shows exactly what changed (lines added/removed)
  git add README.txt
  git commit -m "Add project description to README"

Now make a change you don't want to keep. Edit the file, then:
  git diff            # See the unwanted change
  git restore README.txt  # Undo the change, go back to last commit

This is why git matters: you can experiment freely because you can
always get back to a known good state.

Practice: make 3-4 more commits, adding content each time. Run
`git log --oneline` to see your history grow.
```

**Exercise 0.1c — .gitignore: what NOT to track**
```
Some files should never be committed to git:
  - .env files (contain secrets like API keys)
  - __pycache__/ (Python's compiled cache — regenerated automatically)
  - .venv/ (your virtual environment — too large, machine-specific)
  - .DS_Store (macOS junk files)

Create a .gitignore file:

  # Python
  __pycache__/
  *.py[cod]
  *.egg-info/
  dist/
  build/
  .venv/

  # Environment
  .env

  # OS
  .DS_Store

  # IDE
  .idea/
  .vscode/

Commit it: git add .gitignore && git commit -m "Add .gitignore"

Test it: create a file called "test.pyc". Run `git status`. Notice
git ignores it completely. Delete the test file.

Why this matters: without .gitignore, you'd accidentally commit
secrets, junk files, or huge directories. On a team, this causes
real problems.
```

**Exercise 0.1d — Branching: safe experimentation**
```
Branches let you work on a feature without affecting the main code:

  git branch                  # List branches (* marks current)
  git checkout -b add-parser  # Create and switch to a new branch

Now make some changes and commit them. These commits exist only on
the "add-parser" branch. The "main" branch is untouched.

  git log --oneline           # See commits on this branch
  git checkout main           # Switch back to main
  git log --oneline           # Those commits aren't here!
  git checkout add-parser     # Switch back — they're still here

When your feature is ready, you merge it:
  git checkout main
  git merge add-parser

This workflow — branch, develop, merge — is how every team develops
software. It prevents half-finished work from breaking the main code.
```

**Key concept — why version control matters:** Without git, you'd be saving copies like `parser_v2.py`, `parser_v2_fixed.py`, `parser_v2_final_FINAL.py`. Sound familiar? Git solves this properly. It's the single most important tool in a professional developer's toolkit.

---

### Lesson 0.2: GitHub — Collaboration and Code Hosting

**Concepts:** Remote repositories, pushing, pulling, pull requests, code review, issues

**Background reading:** Git works locally on your machine. GitHub is a website that hosts your repository online, enabling collaboration, backup, and project management. Even on a solo project, GitHub gives you issue tracking, a backup of your code, and a portfolio to show others.

**Exercises:**

**Exercise 0.2a — Create a GitHub repository**
```
1. Go to github.com and create a new repository called "clipsort"
2. Follow GitHub's instructions to connect your local repo:

  git remote add origin https://github.com/YOUR_USERNAME/clipsort.git
  git push -u origin main

Now your code is backed up online. If your laptop dies, your code
survives. Run `git log --oneline` on GitHub's web interface to verify.

Vocabulary:
  - "remote": a copy of your repo hosted somewhere else (GitHub)
  - "origin": the default name for your remote
  - "push": upload your commits to the remote
  - "pull": download new commits from the remote
```

**Exercise 0.2b — Issues: tracking what needs to be done**
```
GitHub Issues are how teams track bugs, features, and tasks. Create
your first issues using the GitHub web interface or the CLI:

  gh issue create --title "Implement filename parser" \
    --body "Parse filenames like 1a.mp4, Scene1_Take2.mp4 to extract scene/take info"

  gh issue create --title "Implement file scanner" \
    --body "Find all video files in a directory, with optional recursive scanning"

  gh issue create --title "Implement organizer" \
    --body "Copy/move files into scene folders based on parsed info"

Create issues for the first 5-6 things you need to build.
Each issue should describe WHAT needs to be done, not HOW.

Look at your issue list: `gh issue list`
This is your to-do list for the project.
```

**Exercise 0.2c — Pull requests: proposing changes**
```
A pull request (PR) says "I've made changes on a branch — please
review them before merging into main." Even on a solo project, PRs
create a record of what changed and why.

  git checkout -b feature/file-scanner
  # ... write code, make commits ...
  git push -u origin feature/file-scanner

  gh pr create --title "Add file scanner" \
    --body "Implements FileScanner class. Closes #2."

Notice "Closes #2" — this links the PR to the issue you created.
When the PR is merged, the issue is automatically closed.

Open the PR on GitHub's website. You can see:
  - The diff (what changed)
  - A place for review comments
  - Status checks (tests passing/failing)

Merge the PR: `gh pr merge --merge`

This workflow — issue -> branch -> PR -> merge — is how professional
teams work. It creates an audit trail of every decision.
```

**Key concept — the development loop:** Professional development follows a cycle: **Plan** (create an issue) -> **Branch** (isolate your work) -> **Build** (write code and tests) -> **Review** (pull request) -> **Merge** (integrate). Even solo developers benefit from this discipline.

---

### Lesson 0.3: Project Scaffolding

**Concepts:** Directory structure conventions, configuration files, the "blank project" problem

**Background reading:** Starting a new project is one of the hardest moments. You stare at an empty folder and think "where do I even begin?" Scaffolding is the answer: a standard set of files and directories that every Python project needs. Once you know the pattern, you can start any project in 10 minutes.

**Exercises:**

**Exercise 0.3a — Create the project structure**
```
Every well-structured Python project looks roughly like this:

  clipsort/
    src/
      clipsort/
        __init__.py
        cli.py
    tests/
      __init__.py
      conftest.py
    pyproject.toml
    Makefile
    Dockerfile
    .gitignore
    README.txt

Create this structure now. Most files can be empty placeholders —
you'll fill them in during later modules. The point is that the
structure exists from day one.

Why this structure?
  - src/clipsort/: your application code (a Python package)
  - tests/: your test code (kept separate from application code)
  - pyproject.toml: project metadata and dependencies
  - Makefile: shortcuts for common commands
  - Dockerfile: container packaging
  - .gitignore: files git should ignore

This is a convention, not a requirement. But following conventions
means any Python developer can look at your project and instantly
understand where things are.

Commit this: git add -A && git commit -m "Add project scaffolding"
```

**Exercise 0.3b — pyproject.toml: your project's identity card**
```
pyproject.toml is the modern way to configure a Python project. It
replaces the older setup.py, setup.cfg, and requirements.txt.

Create pyproject.toml:

  [project]
  name = "clipsort"
  version = "0.1.0"
  description = "Organize video clips into scene folders"
  requires-python = ">=3.12"
  dependencies = [
      "click>=8.0",
  ]

  [project.scripts]
  clipsort = "clipsort.cli:main"

  [project.optional-dependencies]
  dev = [
      "pytest>=7.0",
      "pytest-cov",
      "ruff",
  ]

  [tool.ruff]
  target-version = "py312"
  line-length = 100

  [tool.pytest.ini_options]
  testpaths = ["tests"]

Sections explained:
  - [project]: name, version, what Python version you need
  - dependencies: packages your code needs to run
  - [project.scripts]: "when someone types 'clipsort', run this function"
  - [project.optional-dependencies]: packages only needed for development
  - [tool.ruff]: linter configuration
  - [tool.pytest]: test runner configuration

Commit this change.
```

**Exercise 0.3c — Virtual environments: isolating your project**
```
A virtual environment is an isolated Python installation just for your
project. Without it, installing a package for one project might break
another project. Think of it as Docker for Python packages, but lighter.

  python -m venv .venv            # Create the virtual environment
  source .venv/bin/activate       # Activate it (macOS/Linux)
  # On Windows: .venv\Scripts\activate

Your terminal prompt changes to show (.venv). Now:
  pip install -e ".[dev]"         # Install your project + dev dependencies

The -e flag means "editable" — when you change your code, you don't
need to reinstall. The ".[dev]" means "install this project plus the
dev optional dependencies (pytest, ruff)."

Verify: run `clipsort --help`. It should show your CLI (once you've
written cli.py in Module 2).

Important: the .venv/ directory is in your .gitignore. Every developer
creates their own. The pyproject.toml is what you share — it's the
recipe, not the cooked meal.
```

**Key concept — reproducibility:** Between pyproject.toml (which packages), .gitignore (what not to track), and virtual environments (isolated installation), you have everything needed for anyone to clone your repo and get a working development environment in two commands: `python -m venv .venv && pip install -e ".[dev]"`. This is a superpower.

---

### Lesson 0.4: Code Quality Tools

**Concepts:** Linters, formatters, automation, Makefiles

**Background reading:** Professional developers don't manually check for style issues, unused imports, or common mistakes. They use automated tools that catch these instantly. This isn't about being picky — it's about catching bugs before they become bugs.

**Exercises:**

**Exercise 0.4a — Linting with ruff**
```
ruff is a Python linter — it reads your code and warns about problems.
It catches things like:
  - Unused imports
  - Undefined variables
  - Style violations
  - Common mistakes

Write a deliberately bad Python file, bad_example.py:

  import os
  import sys
  import json

  def add(x,y):
      result = x+y
      unused_variable = 42
      return result

  def dead_code():
      pass

Run: ruff check bad_example.py

ruff will flag: unused imports (os, sys, json), unused variable,
unused function. Fix the issues and run ruff again until it's clean.

Now configure ruff to run on your whole project:
  ruff check src/ tests/
```

**Exercise 0.4b — The Makefile: one command to rule them all**
```
A Makefile defines shortcuts for commands you run frequently.
Instead of remembering long commands, you type `make test`.

Create a Makefile:

  .PHONY: test lint format build clean help

  help:             ## Show this help message
  	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | \
  	  awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

  test:             ## Run tests
  	pytest tests/ -v

  test-cov:         ## Run tests with coverage report
  	pytest tests/ -v --cov=clipsort --cov-report=term-missing

  lint:             ## Check code quality
  	ruff check src/ tests/

  format:           ## Auto-format code
  	ruff format src/ tests/

  build:            ## Build Docker image
  	docker build -t clipsort .

  clean:            ## Remove build artifacts
  	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage
  	find . -type d -name __pycache__ -exec rm -rf {} +

Now:
  make help    # See all available commands
  make lint    # Run the linter
  make test    # Run the tests

Why not just type the commands directly? Three reasons:
  1. You don't have to remember them
  2. New developers can run `make help` to see what's available
  3. CI/CD pipelines can use the same commands

Commit the Makefile.
```

**Exercise 0.4c — Pre-commit: automated quality gates**
```
What if you could automatically run linting before every commit,
so bad code never makes it into your git history?

  pip install pre-commit

Create .pre-commit-config.yaml:

  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.9.0
      hooks:
        - id: ruff
          args: [--fix]
        - id: ruff-format

  pip install pre-commit
  pre-commit install

Now try committing code with a lint error. pre-commit will block the
commit and show you what's wrong. Fix it, stage again, commit again.

This is a "quality gate" — an automated check that prevents mistakes
from reaching your codebase. Professional teams use these extensively.
```

**Key concept — automation over discipline:** Don't rely on remembering to run the linter. Automate it. Don't rely on remembering the right flags for pytest. Put them in the Makefile. The best engineering practices are the ones that happen automatically.

---

### Lesson 0.5: The Software Development Lifecycle (SDLC)

**Concepts:** Planning, requirements, design, implementation, testing, deployment, maintenance

**Background reading:** Building software isn't just writing code. Professional software goes through a lifecycle of phases. Understanding this lifecycle helps you work methodically instead of hacking things together and hoping they work.

**Exercises:**

**Exercise 0.5a — Reading the planning documents**
```
Read through the three planning documents in the docs/ directory:

  1. PRD.md (Product Requirements Document)
     - What problem are we solving?
     - Who is the user?
     - What are the use cases?

  2. DESIGN.md (Design Document)
     - What components do we need?
     - How do they connect?
     - What technologies will we use?

  3. ROADMAP.md (Implementation Roadmap)
     - What do we build first?
     - What can we defer?
     - How do we know each phase is done?

For each document, write down answers to:
  - What's the purpose of this document?
  - Who is the audience?
  - When in the project lifecycle is it created?
  - What would go wrong if we skipped it?
```

**Exercise 0.5b — Tracing a feature through the lifecycle**
```
Pick UC-1001 (organize clips by scene number from filename) and
trace it through every phase of the lifecycle:

  1. REQUIREMENT:  What does the PRD say this feature should do?
  2. DESIGN:       What components in DESIGN.md handle it?
  3. PLAN:         What roadmap tasks implement it?
  4. IMPLEMENT:    What code files will you create/modify?
  5. TEST:         What tests verify it works?
  6. DEPLOY:       How does the user access it? (Docker container)

Do the same for UC-2001 (QR code detection). Notice how a more complex
feature touches more components and requires more planning.

This is called "traceability" — the ability to trace any feature from
its requirement all the way through to its tests. If a test fails,
you can trace back to understand what requirement it validates.
```

**Exercise 0.5c — Writing your own use case**
```
Think of a feature that isn't in the PRD. Maybe:
  - Renaming files based on scene/take (not just moving them)
  - Generating a shot list from organized clips
  - Creating a video montage of first frames from each scene

Write a use case for it using the same format as the PRD:
  - Give it a UC number (e.g., UC-6001)
  - Define the Actor, Precondition, Trigger, Flow, Postcondition
  - Write 3-4 Acceptance Criteria

Then sketch which components from DESIGN.md would need to change,
and where in the ROADMAP.md it would fit.

This exercise practices the full cycle: requirement -> design -> plan.
```

**Key concept — the SDLC isn't waterfall:** You don't finish all planning before writing any code. In practice, you plan a phase, build it, learn from it, and adjust the plan for the next phase. The roadmap has 4 phases precisely because we don't try to design everything upfront. But having *some* plan before coding prevents wasted effort and missed requirements.

---

## Module 1: Foundations — Files, Strings, and Patterns

> **Checkpoint:** Need a fresh start? Run `git checkout checkpoint/module-1` for working scanner + parser code.

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

> **Checkpoint:** Need a fresh start? Run `git checkout checkpoint/module-2` for the full Phase 1 codebase (scanner, parser, organizer, reporter, CLI, Docker).

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

### Lesson 2.2.5: Building Test Fixtures

**Concepts:** Test fixtures, conftest.py, generated vs. static test data, factory patterns

**Background reading:** A test fixture is the "stuff" your tests need — test files, directories, sample data. The question is: do you commit test data to the repo, or generate it on the fly? The answer depends on what you're testing.

**Exercises:**

**Exercise 2.2.5a — conftest.py and shared fixtures**
```
pytest has a special file called conftest.py. Any fixture defined there
is automatically available to all test files in the same directory.

Create tests/conftest.py with a fixture that builds a temporary
directory of test video files:

  import pytest
  from pathlib import Path

  @pytest.fixture()
  def sample_video_dir(tmp_path):
      d = tmp_path / "videos"
      d.mkdir()
      for name in ["1a.mp4", "1b.mp4", "2a.mp4", "2b.mp4"]:
          (d / name).touch()  # creates empty files
      return d

Use this fixture in a test:

  def test_scanner_finds_videos(sample_video_dir):
      scanner = FileScanner()
      files = scanner.scan(sample_video_dir)
      assert len(files) == 4

Key ideas:
  - tmp_path is a built-in pytest fixture that gives you a fresh temp dir
  - Your fixture builds on tmp_path to create specific test scenarios
  - Each test gets its own tmp_path, so tests can't interfere with each other
  - Fixtures are functions, so you can parameterize them
```

**Exercise 2.2.5b — Generated vs. static fixtures**
```
For ClipSort, we need three kinds of test data:

  1. EMPTY FILES (Phase 1): We only care about filenames, not content.
     -> Generate in conftest.py using Path.touch()
     -> Zero bytes, instant to create

  2. TINY VIDEOS (Phase 2): We need real video data for QR detection.
     -> Generate in conftest.py using OpenCV
     -> 320x240, 5fps, 1 second = ~30KB per video
     -> Created once per test session (scope="session")

  3. CLAPPER BOARD PHOTOS (Phase 3): We need realistic images.
     -> Commit static files to tests/fixtures/clapper_boards/
     -> Realistic handwriting and lighting can't be generated

The rule of thumb: generate what you can, commit what you can't.

Why not commit everything? Binary files bloat the git repo, are hard
to diff, and someone has to maintain them. Why not generate everything?
Some test data (handwritten text, real-world photos) can't be
programmatically reproduced with enough fidelity.

Write fixtures for at least three test scenarios:
  - A directory with files using the scene-letter pattern (1a, 1b...)
  - A directory with mixed naming patterns
  - A nested directory simulating multiple memory cards
```

**Exercise 2.2.5c — Video fixture factory (Phase 2 preview)**
```
When you reach Phase 2, you'll need test videos with QR codes baked in.
Here's the pattern — a session-scoped factory fixture:

  @pytest.fixture(scope="session")
  def make_test_video(tmp_path_factory):
      cv2 = pytest.importorskip("cv2")  # skip if OpenCV not installed
      import numpy as np

      video_dir = tmp_path_factory.mktemp("videos")

      def _make(filename, *, qr_data=None):
          path = video_dir / filename
          writer = cv2.VideoWriter(
              str(path),
              cv2.VideoWriter_fourcc(*"mp4v"),
              5, (320, 240)
          )
          for i in range(5):  # 1 second at 5fps
              frame = np.zeros((240, 320, 3), dtype=np.uint8)
              frame[:,:] = (i * 50, 128, 200)
              writer.write(frame)
          writer.release()
          return path

      return _make

Key patterns:
  - scope="session": created once, shared across all tests (fast)
  - pytest.importorskip: gracefully skip if dependency not installed
  - Factory function: each call creates a different test video
  - tmp_path_factory: session-scoped version of tmp_path

Don't worry about implementing this now — you'll build it in Module 3.
The point is to understand the pattern: factories that generate minimal
test data on demand.
```

**Key concept — good tests are self-contained:** Tests that depend on files committed to the repo are fragile — someone might delete or modify the file, and the test breaks for a non-obvious reason. Tests that generate their own data are self-documenting: the fixture *is* the specification of what the test needs.

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

> **Checkpoint:** Need a fresh start? Run `git checkout checkpoint/module-3` for Phase 1 + QR code support.

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

> **Checkpoint:** Need a fresh start? Run `git checkout checkpoint/module-4` for Phase 1 + Phase 2 + Phase 3 code.

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
Install: pip install pytesseract
(Also requires Tesseract system package: brew install tesseract on Mac,
or apt-get install tesseract-ocr on Linux/Docker)

  import pytesseract
  from PIL import Image

  data = pytesseract.image_to_data(
      Image.open("your_image.jpg"),
      output_type=pytesseract.Output.DICT
  )

  for i, text in enumerate(data["text"]):
      text = text.strip()
      if not text:
          continue
      conf = float(data["conf"][i])
      if conf < 0:
          continue
      print(f"{text} (confidence: {conf:.1f}%)")

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

### Lesson 4.4: Audio Analysis and Signal Processing

**Concepts:** PCM audio, sample rates, RMS energy, peak detection, data fusion

**Background reading:** So far, all our detection has been *visual* — looking at pixels in video frames. But videos have audio too, and a clapper board makes a distinctive *clap* sound. Detecting that sound is a completely different kind of analysis: instead of 2D arrays of pixels, we work with 1D arrays of audio samples. This is **digital signal processing (DSP)** — a field that applies to everything from music apps to medical devices.

The core idea: sound is a wave of air pressure changes over time. A microphone converts those pressure changes into numbers. We analyze those numbers to find the loud, sharp transient that is a clap.

**Exercises:**

**Exercise 4.4a — Audio as data: extracting sound from video**
```
In Lesson 3.2, we learned that images are 2D arrays of numbers.
Audio is simpler: a 1D array of numbers, where each number represents
air pressure at a moment in time.

Key vocabulary:
  - Sample rate: how many numbers per second (22050 Hz = 22050 samples/sec)
  - Bit depth: range of each number (16-bit = -32768 to 32767)
  - Mono vs stereo: 1 channel vs 2 channels

Use FFmpeg to extract audio from a video as raw PCM data and load
it into numpy:

  import subprocess
  import numpy as np

  cmd = [
      "ffmpeg",
      "-i", "your_video.mp4",
      "-ac", "1",             # mono (1 channel)
      "-ar", "22050",         # 22050 samples per second
      "-f", "s16le",          # raw 16-bit signed integers, little-endian
      "-acodec", "pcm_s16le",
      "pipe:1",               # write to stdout instead of a file
  ]

  result = subprocess.run(cmd, capture_output=True, check=True)
  raw = np.frombuffer(result.stdout, dtype=np.int16)
  audio = raw.astype(np.float32) / 32768.0  # normalize to [-1, 1]

  print(f"Samples: {len(audio)}")
  print(f"Duration: {len(audio) / 22050:.1f} seconds")
  print(f"Min: {audio.min():.3f}, Max: {audio.max():.3f}")

Notice "pipe:1" — instead of writing to a file, FFmpeg streams the
raw bytes to stdout. In Lesson 4.3a we used capture_output to get
text; here we capture raw binary data. Same pattern, different data.

Experiment: try different sample rates (8000, 22050, 44100). How does
the array size change? What's the tradeoff between quality and size?
```

**Exercise 4.4b — The sliding window pattern: computing an energy envelope**
```
We have thousands of audio samples per second. To detect a clap, we
don't need to look at every individual sample — we need to know
"how loud is the audio right now?"

This is the SLIDING WINDOW pattern: take a long array, chop it into
fixed-size windows, and compute one summary value per window. It's
one of the most widely-used patterns in computer science.

  import numpy as np

  # Simulate 2 seconds of audio at 22050 Hz
  audio = np.random.randn(44100).astype(np.float32) * 0.1

  # Window parameters
  window_ms = 20          # 20 millisecond windows
  sample_rate = 22050
  window_samples = int(sample_rate * window_ms / 1000)  # = 441

  # Reshape the 1D array into a 2D array of windows
  n_windows = len(audio) // window_samples
  trimmed = audio[:n_windows * window_samples]
  frames = trimmed.reshape(n_windows, window_samples)

  # Compute RMS (Root Mean Square) energy per window
  envelope = np.sqrt(np.mean(frames ** 2, axis=1))

  print(f"Audio samples: {len(audio)}")
  print(f"Window size: {window_samples} samples ({window_ms}ms)")
  print(f"Envelope points: {len(envelope)}")

The reshape trick turns a 1D problem into a 2D one:
  - Before: [s0, s1, s2, ..., s44099]       (44100 values)
  - After:  [[s0..s440], [s441..s881], ...]  (100 rows x 441 cols)

Then np.mean(..., axis=1) collapses each row to one number.

RMS (Root Mean Square) measures the "energy" of a signal. A loud
sound like a clap will have high RMS; silence will be near zero.

Try it with real audio from Exercise 4.4a. Can you spot where a
clap happens by looking at the envelope values?
```

**Exercise 4.4c — Finding peaks: detecting claps with scipy**
```
Now we have an envelope where claps appear as sharp spikes. How do
we automatically find those spikes?

scipy.signal.find_peaks does exactly this:

  from scipy.signal import find_peaks
  import numpy as np

  # Create a synthetic envelope with two "claps"
  envelope = np.zeros(500)
  envelope[100] = 0.9   # loud clap at position 100
  envelope[300] = 0.8   # another clap at position 300
  # Add some background noise
  envelope += np.random.rand(500) * 0.05

  # Find peaks
  peaks, properties = find_peaks(
      envelope,
      distance=50,        # minimum 50 samples apart
      prominence=0.3,     # must stand out by at least 0.3
  )

  print(f"Found {len(peaks)} peaks at positions: {peaks}")

Two critical parameters:
  - distance: minimum gap between peaks (avoids double-triggering)
  - prominence: how much a peak must "stand out" from neighbors

This is a TUNING problem. Like the heuristics in Lesson 4.1c,
there's no single right answer:
  - High prominence = fewer false positives, might miss quiet claps
  - Low prominence = catches everything, including bumps and noise
  - High distance = won't double-trigger, but misses rapid claps
  - Low distance = catches rapid claps, but may double-trigger

Try with real audio from Exercises 4.4a-b:
  1. Compute the envelope of a video with known claps
  2. Run find_peaks with different prominence values (0.3, 0.5, 0.7)
  3. Convert peak positions to timestamps:
     window_seconds = window_ms / 1000.0
     timestamps = [int(p) * window_seconds for p in peaks]
  4. Do the timestamps match where you hear the claps?
```

**Exercise 4.4d — Data fusion: merging audio and visual detections**
```
Now we have two independent ways to detect scene boundaries:
  - Visual: QR codes, clapper boards, OCR (from Lessons 4.1-4.3)
  - Audio: clap sounds (from Lessons 4.4a-c)

Sometimes both detect the same scene change. Sometimes only one does.
We need to MERGE them without duplicating split points.

This is DATA FUSION: combining results from different detection
sources into a single, better result.

  def merge_timestamps(
      visual: list[float],
      audio: list[float],
      dedup_window: float = 3.0,
  ) -> list[float]:
      """Merge visual and audio timestamps, removing near-duplicates.

      Visual detections take priority because they carry scene/take
      info. An audio timestamp within dedup_window seconds of any
      existing point is considered a duplicate.
      """
      # Start with all visual detections (they have richer data)
      merged = sorted(visual)

      for ts in sorted(audio):
          # Check if this audio detection is near any existing point
          is_duplicate = any(
              abs(ts - existing) <= dedup_window
              for existing in merged
          )
          if not is_duplicate:
              merged.append(ts)

      return sorted(merged)

  # Test it:
  visual = [10.0, 30.5, 55.2]
  audio = [10.3, 29.8, 42.0, 55.0]
  result = merge_timestamps(visual, audio)
  print(result)  # [10.0, 30.5, 42.0, 55.2]
  # 10.3 merged with 10.0, 29.8 merged with 30.5, 55.0 merged with 55.2
  # 42.0 is a NEW detection only audio caught!

Think about:
  - Why do visual detections take priority? (They have scene/take info)
  - What happens if you make dedup_window too small? Too large?
  - This is different from the detection chain (Lesson 3.3c) where
    the first detector to succeed "wins." Here we COMBINE all results.

This pattern appears everywhere: self-driving cars merge camera +
lidar + radar data. Weather apps merge satellite + ground station
readings. Any time you have multiple imperfect sensors, you fuse
their results to get something better than either alone.
```

**Key concept — signal processing as a general skill:** The envelope-and-peaks pattern you just learned isn't specific to audio claps. The same approach works for ECG heart monitors (detecting heartbeats), seismographs (detecting earthquakes), stock price analysis (detecting price spikes), and fitness trackers (detecting footsteps). Learn it once, apply it everywhere. That's the power of studying the underlying computer science rather than just one application.

---

## Module 5: Engineering Practices in Action

> **No checkpoint for Module 5.** This module is about applying practices to whatever code you've built — there's no specific code to skip to.

*Skills: debugging, refactoring, dependency management, CI/CD, releases, documentation*

Module 0 covered project setup. This module covers what happens *during* and *after* development — the ongoing engineering practices that keep a project healthy as it grows.

### Lesson 5.1: Debugging Systematically

**Concepts:** Reading error messages, stack traces, print debugging vs. debuggers, logging

**Background reading:** Everyone's code has bugs. What separates experienced developers from beginners isn't writing bug-free code — it's finding and fixing bugs quickly. The key is being systematic instead of randomly changing things and hoping it works.

**Exercises:**

**Exercise 5.1a — Reading a stack trace**
```
Python stack traces read bottom-to-top. The last line is the error,
and the lines above show how you got there. Consider:

  Traceback (most recent call last):
    File "cli.py", line 42, in organize
      plan = organizer.build_plan(files, output_dir)
    File "organizer.py", line 18, in build_plan
      info = parser.parse(f.name)
    File "parser.py", line 31, in parse
      scene = int(match.group(1))
  ValueError: invalid literal for int() with base 10: 'abc'

Reading this: cli.py called organizer.py which called parser.py, and
on line 31, it tried to convert 'abc' to an integer and failed.

Practice: Deliberately introduce 3 different bugs into your parser
code (e.g., wrong index, missing None check, bad regex). Run the
tests. For each failure, read the stack trace and identify:
  1. What error occurred? (the last line)
  2. Where did it happen? (file and line number)
  3. Why did it happen? (trace the data flow)
```

**Exercise 5.1b — Logging instead of print()**
```
Using print() for debugging works but has problems: you have to
remember to remove them, and they all look the same. Python's
logging module is the professional alternative.

  import logging

  logger = logging.getLogger(__name__)

  def parse(self, filename: str) -> ClipInfo | None:
      logger.debug(f"Parsing filename: {filename}")
      for name, pattern in self.PATTERNS:
          match = pattern.match(filename)
          if match:
              logger.info(f"Matched pattern '{name}' for {filename}")
              return ClipInfo(...)
      logger.warning(f"No pattern matched: {filename}")
      return None

Add logging to your scanner and parser. Then control the output:
  - Normal run: only warnings and errors show
  - With --verbose: debug messages show too

Wire --verbose to logging.basicConfig(level=logging.DEBUG).
Now you have permanent, controllable instrumentation in your code.
```

**Exercise 5.1c — Writing a bug report**
```
When you find a bug, practice writing a proper GitHub issue:

  Title: "Parser crashes on filenames with spaces"

  ## Steps to reproduce
  1. Create a file named "Scene 1 Take 2.mp4"
  2. Run: clipsort organize ./input ./output
  3. Observe crash

  ## Expected behavior
  File should be organized into scene_01/

  ## Actual behavior
  ValueError: invalid literal for int()...

  ## Environment
  - Python 3.12.1
  - ClipSort v0.1.0
  - macOS 15.3

Create a bug report issue on GitHub for a real or hypothetical bug.
Then create a branch, fix it, write a test that covers it, and
submit a PR that references the issue.

This is the professional bug-fix workflow:
  Bug report -> Branch -> Fix + Test -> PR -> Merge
```

**Key concept — bugs are normal:** Professional developers spend as much time debugging as writing new code. The skill isn't avoiding all bugs — it's having a systematic process for finding and fixing them.

---

### Lesson 5.2: Refactoring — Improving Code Without Changing Behavior

**Concepts:** Code smells, refactoring patterns, tests as a safety net

**Background reading:** Refactoring means changing how code is structured without changing what it does. You do it to make code easier to read, maintain, or extend. Tests are your safety net — if they still pass after refactoring, you haven't broken anything.

**Exercises:**

**Exercise 5.2a — Identify code smells**
```
"Code smells" are patterns that suggest code could be improved.
Look through your ClipSort code for these common smells:

  1. LONG FUNCTION: any function longer than ~20 lines
     Fix: break it into smaller functions with clear names

  2. REPEATED CODE: similar logic in multiple places
     Fix: extract a shared helper function

  3. MAGIC VALUES: unexplained numbers or strings in code
     Fix: use named constants
     Bad:  if len(approx) == 4:
     Good: RECTANGLE_VERTICES = 4
           if len(approx) == RECTANGLE_VERTICES:

  4. DEEP NESTING: 3+ levels of indentation
     Fix: return early to flatten the structure
     Bad:  if x:
               if y:
                   if z:
                       do_thing()
     Good: if not x: return
           if not y: return
           if not z: return
           do_thing()

Find at least 3 code smells in your code. For each one, write down
what the smell is and how you'd fix it — but don't fix them yet.
```

**Exercise 5.2b — Refactor with tests as your safety net**
```
Now fix the code smells you identified. After EACH change:

  1. Run `make test` to verify nothing broke
  2. Commit the change with a message like:
     "Refactor: extract _try_pattern() helper from parse()"

If a test fails, you know exactly which change broke it (because
you committed after each one). This is why small, frequent commits
matter.

Rules of refactoring:
  - Change structure, not behavior
  - One change at a time
  - Test after every change
  - If tests fail, undo and try a smaller change
```

**Exercise 5.2c — Adding a feature after refactoring**
```
After refactoring, adding a new feature should be easier. Try this:

Add support for a new filename pattern — say, "Day1_Scene2_Take3.mp4".

Notice how your refactored code (with clean pattern lists and helper
functions) makes this a 2-3 line change instead of a major surgery.
That's the payoff of refactoring.

Write a test FIRST (test-driven development):
  def test_day_scene_take_pattern():
      result = parse_filename("Day1_Scene2_Take3.mp4")
      assert result.scene == 2
      assert result.take == 3

Run it — it fails. Now add the pattern. Run it — it passes.
Commit. This is the TDD cycle: Red (fail) -> Green (pass) -> Refactor.
```

**Key concept — refactoring is not rewriting:** Refactoring is small, safe, incremental improvements. Rewriting is starting over. Refactoring is almost always better. You keep working code working while making it better.

---

### Lesson 5.3: Managing Dependencies

**Concepts:** Dependency versions, lock files, supply chain, updating

**Background reading:** Your project depends on other people's code (Click, OpenCV, pytest). Managing these dependencies well prevents the dreaded "it worked yesterday but today it's broken" problem.

**Exercises:**

**Exercise 5.3a — Understanding version specifiers**
```
In pyproject.toml, dependencies have version constraints:

  "click>=8.0"         # 8.0 or higher (any 8.x, 9.x, etc.)
  "click>=8.0,<9.0"   # 8.0 or higher, but not 9.0+
  "click~=8.1"        # >=8.1, <9.0 (compatible release)
  "click==8.1.7"      # Exactly this version

Why not always pin exact versions? Because then you can't get bug
fixes or security patches. Why not leave them completely open?
Because a breaking change in a dependency could break your tool.

The sweet spot: use >= with a minimum version you've tested against.
For production/Docker, generate a lock file (next exercise) for
exact reproducibility.

Review your pyproject.toml. For each dependency, decide: what's the
minimum version you need, and should you cap the maximum?
```

**Exercise 5.3b — Lock files with pip-compile**
```
A lock file records the exact versions installed, including all
sub-dependencies. This means "pip install" gives identical results
on any machine at any time.

  pip install pip-tools

  # Generate a lock file from your pyproject.toml:
  pip-compile pyproject.toml -o requirements.lock

Look at requirements.lock — it lists every package with exact versions
and hashes. Your Dockerfile should use this:

  COPY requirements.lock .
  RUN pip install --no-cache-dir -r requirements.lock

Now your Docker image installs the exact same versions every time,
even if new versions are released later.

When you want to update dependencies:
  pip-compile --upgrade pyproject.toml -o requirements.lock
```

**Exercise 5.3c — Adding a new dependency**
```
Practice the full workflow of adding a dependency:

1. Identify the need: "I need to generate PDF files"
2. Research options: fpdf2, reportlab, weasyprint
3. Evaluate: size, maintenance status, license, ease of use
4. Add to pyproject.toml: "fpdf2>=2.7"
5. Regenerate the lock file: pip-compile ...
6. Install: pip install -e ".[dev]"
7. Write a minimal test to verify it works
8. Commit all changes (pyproject.toml + lock file)

Go through this process for one of ClipSort's Phase 2 dependencies
(qrcode, pyzbar, or opencv-python-headless).
```

**Key concept — you are responsible for your dependencies:** Every dependency is code you didn't write but ship to your users. Check that dependencies are actively maintained, have compatible licenses, and don't introduce excessive risk. Run `pip audit` periodically to check for known vulnerabilities.

---

### Lesson 5.4: Continuous Integration (CI/CD)

**Concepts:** Automated testing, GitHub Actions, build pipelines, deployment

**Background reading:** CI (Continuous Integration) means automatically running your tests every time you push code. If tests fail, you know immediately — not days later when someone else tries to use your code. CD (Continuous Delivery) extends this to automatically building and publishing releases.

**Exercises:**

**Exercise 5.4a — Your first GitHub Action**
```
Create .github/workflows/ci.yml:

  name: CI

  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]

  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4

        - uses: actions/setup-python@v5
          with:
            python-version: "3.12"

        - name: Install dependencies
          run: pip install -e ".[dev]"

        - name: Lint
          run: ruff check src/ tests/

        - name: Test
          run: pytest tests/ -v

Push this file. Go to your GitHub repo's "Actions" tab and watch it
run. You now have automated CI.

If you push code with a lint error or failing test, the Action fails
and shows a red X. Pull requests will show this status too.
```

**Exercise 5.4b — Add Docker build to CI**
```
Extend your CI workflow to also build the Docker image:

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t clipsort .
      - name: Smoke test
        run: |
          mkdir -p /tmp/test_input /tmp/test_output
          touch /tmp/test_input/1a.mp4
          docker run --rm \
            -v /tmp/test_input:/input:ro \
            -v /tmp/test_output:/output \
            clipsort organize /input /output

Now every push verifies that the Docker image builds and runs
correctly. You'll never accidentally break the Docker build.
```

**Exercise 5.4c — Status badges and branch protection**
```
Add a CI status badge to your README so anyone can see if tests pass:

  Go to your GitHub Actions workflow -> click "..." -> "Create status badge"
  Copy the markdown and paste it at the top of your README.

Set up branch protection rules (on GitHub):
  1. Go to Settings -> Branches -> Add rule for "main"
  2. Enable "Require status checks to pass before merging"
  3. Select your CI workflow

Now you literally cannot merge a PR that has failing tests. This
protects your main branch from broken code.
```

**Key concept — CI is your automated teammate:** CI catches mistakes within minutes, runs the same checks every time (no forgetting), and gives everyone confidence that main is always working. Setting it up takes 30 minutes; it saves hours over the life of a project.

---

### Lesson 5.5: Releases and Versioning

**Concepts:** Semantic versioning, changelogs, GitHub releases, tagging

**Background reading:** At some point, your tool is ready for others to use. A "release" is a specific, tested, packaged version that you declare as ready. Versioning tells users what changed and whether an update might break their workflow.

**Exercises:**

**Exercise 5.5a — Semantic versioning**
```
Version numbers follow a pattern: MAJOR.MINOR.PATCH (e.g., 1.2.3)

  PATCH (1.2.3 -> 1.2.4): Bug fixes, no new features
  MINOR (1.2.3 -> 1.3.0): New features, backwards compatible
  MAJOR (1.2.3 -> 2.0.0): Breaking changes

For ClipSort, consider these changes. What version bump does each need?

  - Fix: parser crashes on filenames with spaces     -> ?
  - Add: new --json flag for machine-readable output  -> ?
  - Change: rename --recursive flag to --deep          -> ?
  - Add: QR code detection support (Phase 2)           -> ?
  - Change: require Python 3.13 instead of 3.12        -> ?

The answer depends on whether users have to change their behavior.
If they don't, it's minor or patch. If they do, it's major.
```

**Exercise 5.5b — Creating a release**
```
When Phase 1 is complete, create a release:

  1. Update the version in pyproject.toml to "0.1.0"
  2. Create a CHANGELOG.md entry:

     ## [0.1.0] - 2026-XX-XX

     ### Added
     - Filename-based clip organization (scene+letter, Scene_Take, S01T03)
     - Dry-run mode (--dry-run)
     - Move mode (--move) and copy (default)
     - Recursive directory scanning (--recursive)
     - Organization report with scene/clip counts
     - Docker container support

  3. Commit: git commit -m "Release v0.1.0"
  4. Tag: git tag v0.1.0
  5. Push: git push && git push --tags
  6. Create a GitHub release:
     gh release create v0.1.0 --title "v0.1.0: Filename Organizer" \
       --notes-file CHANGELOG.md

Now anyone can download a specific version of your tool.
```

**Exercise 5.5c — Publishing a Docker image**
```
Push your Docker image to GitHub Container Registry so anyone can
pull it without building from source:

  # Log in to GitHub's container registry
  echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

  # Tag and push
  docker tag clipsort ghcr.io/YOUR_USERNAME/clipsort:0.1.0
  docker tag clipsort ghcr.io/YOUR_USERNAME/clipsort:latest
  docker push ghcr.io/YOUR_USERNAME/clipsort:0.1.0
  docker push ghcr.io/YOUR_USERNAME/clipsort:latest

Now anyone can run your tool with:
  docker run ghcr.io/YOUR_USERNAME/clipsort:0.1.0 organize /input /output

Bonus: add this to your CI workflow to automatically publish on
every tagged release.
```

**Key concept — shipping is a skill:** Writing code is only part of software engineering. Packaging, versioning, and releasing it so others can actually use it is equally important. Many great tools die because the developer never learned to ship.

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

## Concept Map: AP CS Topics and Engineering Skills in ClipSort

### Computer Science Concepts

| AP CS Topic | Where It Shows Up in ClipSort |
|---|---|
| Variables & Types | ClipInfo fields, Path objects, strings vs ints |
| Conditionals | Pattern matching fallbacks, error handling |
| Loops | Scanning directories, iterating frames, processing file lists |
| Nested Loops | QR code batch generation (scenes x takes), frame sampling |
| Arrays/Lists | Video frame arrays, file lists, plan mappings |
| 2D Arrays | Image pixel data (height x width x channels) |
| 1D Arrays / Signal Processing | Audio waveforms, energy envelopes, peak detection |
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
| Parameter Tuning | Threshold/sensitivity tradeoffs in clap detection |
| Data Fusion | Merging audio and visual detection results |

### Software Engineering Skills

| Skill | Where It Shows Up in ClipSort |
|---|---|
| Version Control (Git) | Every commit, branch, and merge throughout the project |
| GitHub Workflow | Issues, pull requests, code review, branch protection |
| Project Scaffolding | Directory structure, pyproject.toml, config files |
| Virtual Environments | Isolating project dependencies with .venv |
| Dependency Management | pyproject.toml, lock files, adding/updating packages |
| Code Quality / Linting | ruff checks, pre-commit hooks |
| Debugging | Stack traces, logging, systematic bug investigation |
| Refactoring | Improving code structure without changing behavior |
| CI/CD | GitHub Actions running tests and builds automatically |
| Docker / Containerization | Dockerfile, docker-compose, volume mounts |
| Releases & Versioning | Semantic versioning, tags, changelogs, GitHub releases |
| Documentation | PRD, design docs, CLI help text, code comments |
| SDLC / Planning | Requirements, design, roadmap, traceability |
| Subprocess Piping | Streaming binary data from FFmpeg to numpy |
| Makefiles / Automation | Shortcuts for test, lint, build, clean |
