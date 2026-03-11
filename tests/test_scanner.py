"""Tests for FileScanner."""

from pathlib import Path

from clipsort.scanner import FileScanner


class TestFileScanner:
    def setup_method(self):
        self.scanner = FileScanner()

    def test_scan_finds_video_files(self, sample_video_dir):
        result = self.scanner.scan(sample_video_dir)
        assert len(result) == 6
        assert all(isinstance(p, Path) for p in result)

    def test_scan_returns_sorted_by_name(self, sample_video_dir):
        result = self.scanner.scan(sample_video_dir)
        names = [p.name for p in result]
        assert names == sorted(names, key=str.lower)

    def test_scan_skips_non_video_files(self, mixed_pattern_files):
        result = self.scanner.scan(mixed_pattern_files)
        names = {p.name for p in result}
        assert "random_notes.txt" not in names

    def test_scan_case_insensitive_extensions(self, tmp_path):
        d = tmp_path / "ext_test"
        d.mkdir()
        (d / "clip.MP4").touch()
        (d / "clip.Mp4").touch()
        (d / "clip.mov").touch()
        result = self.scanner.scan(d)
        assert len(result) == 3

    def test_scan_empty_directory(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        result = self.scanner.scan(d)
        assert result == []

    def test_scan_nonexistent_directory(self, tmp_path):
        result = self.scanner.scan(tmp_path / "nope")
        assert result == []

    def test_scan_not_recursive_by_default(self, nested_video_dir):
        result = self.scanner.scan(nested_video_dir, recursive=False)
        assert result == []

    def test_scan_recursive(self, nested_video_dir):
        result = self.scanner.scan(nested_video_dir, recursive=True)
        assert len(result) == 4

    def test_scan_all_supported_extensions(self, tmp_path):
        d = tmp_path / "all_ext"
        d.mkdir()
        for ext in FileScanner.VIDEO_EXTENSIONS:
            (d / f"clip{ext}").touch()
        (d / "clip.txt").touch()
        (d / "clip.pdf").touch()
        result = self.scanner.scan(d)
        assert len(result) == len(FileScanner.VIDEO_EXTENSIONS)
