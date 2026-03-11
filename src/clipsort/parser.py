"""Filename parser — extracts scene/take info from video filenames."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class ClipInfo:
    """Parsed clip metadata."""

    scene: int
    take: int | str | None = None
    confidence: float = 1.0
    method: str = "filename"


class FilenameParser:
    """Extract scene/take information from video filenames using regex patterns."""

    PATTERNS: ClassVar[list[tuple[str, re.Pattern[str]]]] = [
        ("scene_letter", re.compile(r"^(\d+)([a-z])(?:\.\w+)?$", re.I)),
        ("scene_take", re.compile(r"^(\d+)[_-](\d+)(?:\.\w+)?$")),
        (
            "scene_Take",
            re.compile(r"^[Ss]cene[_\s]?(\d+)[_\s]?[Tt]ake[_\s]?(\d+)(?:\.\w+)?$", re.I),
        ),
        ("short_form", re.compile(r"^[Ss](\d+)[Tt](\d+)(?:\.\w+)?$", re.I)),
    ]

    def parse(self, filename: str) -> ClipInfo | None:
        """Try each pattern against the filename; return the first match or None."""
        stem = Path(filename).stem if "." in filename else filename

        for name, pattern in self.PATTERNS:
            match = pattern.match(filename)
            if match is None and stem != filename:
                match = pattern.match(stem)
            if match:
                scene = int(match.group(1))
                raw_take = match.group(2)
                take = int(raw_take) if raw_take.isdigit() else raw_take.lower()
                return ClipInfo(scene=scene, take=take, method=f"filename:{name}")

        return None
