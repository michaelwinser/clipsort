"""File scanner — discovers video files in a directory."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar


class FileScanner:
    """Find video files in a directory tree."""

    VIDEO_EXTENSIONS: ClassVar[set[str]] = {".mp4", ".mov", ".mkv", ".avi", ".mts", ".m4v", ".webm"}

    def scan(self, input_dir: Path, recursive: bool = False) -> list[Path]:
        """Return a sorted list of video file paths.

        Args:
            input_dir: Directory to scan.
            recursive: If True, scan subdirectories too.

        Returns:
            List of Path objects for discovered video files, sorted by name.
        """
        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            return []

        if recursive:
            files = (
                p
                for p in input_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in self.VIDEO_EXTENSIONS
            )
        else:
            files = (
                p
                for p in input_dir.iterdir()
                if p.is_file() and p.suffix.lower() in self.VIDEO_EXTENSIONS
            )

        return sorted(files, key=lambda p: p.name.lower())
