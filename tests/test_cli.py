"""Integration tests for the CLI."""

from click.testing import CliRunner

from clipsort.cli import main


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "organize" in result.output

    def test_version(self):
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_organize_dry_run(self, sample_video_dir, tmp_path):
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(sample_video_dir), str(output_dir), "--dry-run"],
        )
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        assert "scene_01" in result.output
        assert not output_dir.exists()

    def test_organize_copy(self, sample_video_dir, tmp_path):
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(sample_video_dir), str(output_dir)],
        )
        assert result.exit_code == 0
        assert "Copied" in result.output
        assert (output_dir / "scene_01").exists()
        assert (output_dir / "scene_02").exists()

    def test_organize_move(self, scene_letter_files, tmp_path):
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(scene_letter_files), str(output_dir), "--move"],
        )
        assert result.exit_code == 0
        assert "Moved" in result.output
        # Source files should be gone
        remaining = list(scene_letter_files.iterdir())
        assert len(remaining) == 0

    def test_organize_recursive(self, nested_video_dir, tmp_path):
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(nested_video_dir), str(output_dir), "-r"],
        )
        assert result.exit_code == 0
        assert "4 video file(s)" in result.output

    def test_organize_no_files(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(empty), str(output_dir)],
        )
        assert result.exit_code != 0
        assert "No video files found" in result.output

    def test_organize_verbose(self, sample_video_dir, tmp_path):
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(sample_video_dir), str(output_dir), "--dry-run", "-v"],
        )
        assert result.exit_code == 0

    def test_organize_report_file(self, sample_video_dir, tmp_path):
        output_dir = tmp_path / "output"
        report = tmp_path / "report.txt"
        result = self.runner.invoke(
            main,
            [
                "organize",
                str(sample_video_dir),
                str(output_dir),
                "--report-file",
                str(report),
            ],
        )
        assert result.exit_code == 0
        assert report.exists()
        assert "Report saved" in result.output

    def test_organize_with_unsorted(self, mixed_pattern_files, tmp_path):
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["organize", str(mixed_pattern_files), str(output_dir)],
        )
        assert result.exit_code == 0
        assert "Unsorted" in result.output or "behind_the_scenes" in result.output
