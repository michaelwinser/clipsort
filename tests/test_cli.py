"""Integration tests for the CLI."""

import pytest
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

    def test_help_shows_all_commands(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "organize" in result.output
        assert "detect" in result.output
        assert "qr-generate" in result.output

    def test_organize_multiple_patterns(self, tmp_path):
        """UC-1002: All four filename conventions are recognized."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # scene_letter, scene_take, Scene_Take, short_form
        for name in ["1a.mp4", "2_1.mp4", "Scene3_Take1.mp4", "S04T01.mp4"]:
            (input_dir / name).touch()

        result = self.runner.invoke(
            main,
            ["organize", str(input_dir), str(output_dir)],
        )
        assert result.exit_code == 0
        assert "4 video file(s)" in result.output
        assert (output_dir / "scene_01").exists()
        assert (output_dir / "scene_02").exists()
        assert (output_dir / "scene_03").exists()
        assert (output_dir / "scene_04").exists()
        # No unsorted
        assert "Unsorted" not in result.output

    def test_organize_report_content(self, sample_video_dir, tmp_path):
        """UC-1004: Report file contains scene count, clips-per-scene, unsorted count."""
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
        content = report.read_text()
        assert "Scenes detected:" in content
        assert "clip(s)" in content
        assert "Files processed:" in content

    def test_organize_conflict_resolution(self, tmp_path):
        """UC-1005: Identically-named files from different subdirs get deduped."""
        input_dir = tmp_path / "input"
        sub_a = input_dir / "CARD_A"
        sub_b = input_dir / "CARD_B"
        sub_a.mkdir(parents=True)
        sub_b.mkdir(parents=True)
        output_dir = tmp_path / "output"

        # Same filename in both subdirectories
        (sub_a / "1a.mp4").touch()
        (sub_b / "1a.mp4").touch()

        result = self.runner.invoke(
            main,
            ["organize", str(input_dir), str(output_dir), "-r"],
        )
        assert result.exit_code == 0
        # Both files should end up in scene_01
        scene_dir = output_dir / "scene_01"
        assert scene_dir.exists()
        files = list(scene_dir.iterdir())
        assert len(files) == 2
        names = sorted(f.name for f in files)
        assert "1a.mp4" in names
        assert "1a_2.mp4" in names
        # Report mentions conflict
        assert "Conflicts resolved" in result.output

    def test_organize_missing_input_dir(self, tmp_path):
        """UC-4002: Nonexistent input dir produces clear error."""
        result = self.runner.invoke(
            main,
            ["organize", str(tmp_path / "nonexistent"), str(tmp_path / "out")],
        )
        assert result.exit_code != 0

    def test_organize_subcommand_help(self):
        result = self.runner.invoke(main, ["organize", "--help"])
        assert result.exit_code == 0
        assert "INPUT_DIR" in result.output


class TestQRGenerateCLI:
    def setup_method(self):
        self.runner = CliRunner()

    @pytest.fixture(autouse=True)
    def _skip_without_qrcode(self):
        pytest.importorskip("qrcode")

    def test_qr_generate_single(self, tmp_path):
        out = tmp_path / "test.png"
        result = self.runner.invoke(
            main,
            ["qr-generate", "--scene", "1", "--take", "2", "--output", str(out)],
        )
        assert result.exit_code == 0
        assert "QR code saved" in result.output
        assert out.exists()

    def test_qr_generate_batch(self, tmp_path):
        out = tmp_path / "sheet.pdf"
        result = self.runner.invoke(
            main,
            ["qr-generate", "--scenes", "3", "--takes", "2", "--output", str(out)],
        )
        assert result.exit_code == 0
        assert "QR sheet saved" in result.output
        assert out.exists()

    def test_qr_generate_mixed_errors(self):
        result = self.runner.invoke(
            main,
            ["qr-generate", "--scene", "1", "--take", "1", "--scenes", "3", "--takes", "2"],
        )
        assert result.exit_code != 0

    def test_qr_generate_no_args_errors(self):
        result = self.runner.invoke(main, ["qr-generate"])
        assert result.exit_code != 0

    def test_qr_generate_single_with_project(self, tmp_path):
        """UC-2002: --project flag is accepted and output is created."""
        out = tmp_path / "proj_test.png"
        result = self.runner.invoke(
            main,
            [
                "qr-generate",
                "--scene", "1",
                "--take", "1",
                "--project", "MyFilm",
                "--output", str(out),
            ],
        )
        assert result.exit_code == 0
        assert "QR code saved" in result.output
        assert out.exists()

    def test_qr_generate_incomplete_single_args(self):
        """UC-4002: --scene without --take produces clear error."""
        result = self.runner.invoke(
            main,
            ["qr-generate", "--scene", "1"],
        )
        assert result.exit_code != 0


class TestDetectCLI:
    def setup_method(self):
        self.runner = CliRunner()

    @pytest.fixture(autouse=True)
    def _skip_without_cv2(self):
        pytest.importorskip("cv2")

    def test_detect_with_qr_videos(self, make_test_video, tmp_path):
        import json

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create a video with QR code
        data = json.dumps({"v": 1, "scene": 1, "take": 1})
        video = make_test_video("qr_clip.mp4", qr_data=data)
        import shutil

        shutil.copy2(video, input_dir / "qr_clip.mp4")

        result = self.runner.invoke(
            main,
            ["detect", str(input_dir), str(output_dir)],
        )
        assert result.exit_code == 0
        assert "1 video file(s)" in result.output

    def test_detect_fallback_to_filename(self, tmp_path):
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create empty video files (will fail QR detection, fall back to filename)
        (input_dir / "1a.mp4").write_bytes(b"\x00" * 100)
        (input_dir / "2b.mp4").write_bytes(b"\x00" * 100)

        result = self.runner.invoke(
            main,
            ["detect", str(input_dir), str(output_dir), "--dry-run"],
        )
        assert result.exit_code == 0
        assert "2 video file(s)" in result.output
        assert "scene_01" in result.output
        assert "scene_02" in result.output

    def test_detect_qr_organizes_correctly(self, make_test_video, tmp_path):
        """UC-2001: QR-detected scene/take places file in correct folder."""
        import json
        import shutil

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        data = json.dumps({"v": 1, "scene": 3, "take": 1})
        video = make_test_video("scene3_qr.mp4", qr_data=data)
        shutil.copy2(video, input_dir / "scene3_qr.mp4")

        result = self.runner.invoke(
            main,
            ["detect", str(input_dir), str(output_dir)],
        )
        assert result.exit_code == 0
        assert (output_dir / "scene_03").exists()

    def test_detect_mixed_input(self, make_test_video, tmp_path):
        """UC-2004: Mixed QR + filename + unsorted with method reporting."""
        import json
        import shutil

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        report = tmp_path / "report.txt"

        # QR video
        data = json.dumps({"v": 1, "scene": 1, "take": 1})
        video = make_test_video("qr_mixed.mp4", qr_data=data)
        shutil.copy2(video, input_dir / "qr_mixed.mp4")

        # Filename-parseable (will fail QR, fall back to filename)
        (input_dir / "2a.mp4").write_bytes(b"\x00" * 100)

        # Unrecognizable
        (input_dir / "random_clip.mp4").write_bytes(b"\x00" * 100)

        result = self.runner.invoke(
            main,
            [
                "detect",
                str(input_dir),
                str(output_dir),
                "--report-file",
                str(report),
            ],
        )
        assert result.exit_code == 0
        content = report.read_text()
        assert "Detection methods:" in content
        assert "Unsorted:" in content or "Unsorted: 1" in content

    def test_detect_missing_input_dir(self, tmp_path):
        """UC-4002: Nonexistent input dir for detect command."""
        result = self.runner.invoke(
            main,
            ["detect", str(tmp_path / "nonexistent"), str(tmp_path / "out")],
        )
        assert result.exit_code != 0

    def test_detect_no_files(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        output_dir = tmp_path / "output"
        result = self.runner.invoke(
            main,
            ["detect", str(empty), str(output_dir)],
        )
        assert result.exit_code != 0
        assert "No video files found" in result.output

    def test_detect_with_mode_qr(self, tmp_path):
        """--mode qr uses only QR detection + filename fallback."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        (input_dir / "1a.mp4").write_bytes(b"\x00" * 100)

        result = self.runner.invoke(
            main,
            ["detect", str(input_dir), str(output_dir), "--mode", "qr", "--dry-run"],
        )
        assert result.exit_code == 0
        assert "scene_01" in result.output

    def test_detect_with_mode_ocr(self, tmp_path):
        """--mode ocr uses only OCR detection + filename fallback."""
        pytesseract = pytest.importorskip("pytesseract")  # noqa: F841

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        (input_dir / "2b.mp4").write_bytes(b"\x00" * 100)

        result = self.runner.invoke(
            main,
            ["detect", str(input_dir), str(output_dir), "--mode", "ocr", "--dry-run"],
        )
        assert result.exit_code == 0
        # Falls back to filename parsing
        assert "scene_02" in result.output

    def test_detect_auto_mode_chain(self, make_test_video, tmp_path):
        """Auto mode tries QR → OCR → filename in order."""
        pytesseract = pytest.importorskip("pytesseract")  # noqa: F841
        import json
        import shutil

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # QR video
        data = json.dumps({"v": 1, "scene": 1, "take": 1})
        video = make_test_video("auto_qr.mp4", qr_data=data)
        shutil.copy2(video, input_dir / "auto_qr.mp4")

        # Filename-only video
        (input_dir / "3a.mp4").write_bytes(b"\x00" * 100)

        result = self.runner.invoke(
            main,
            [
                "detect",
                str(input_dir),
                str(output_dir),
                "--mode", "auto",
            ],
        )
        assert result.exit_code == 0
        assert "2 video file(s)" in result.output

    def test_detect_help_shows_mode_option(self):
        result = self.runner.invoke(main, ["detect", "--help"])
        assert result.exit_code == 0
        assert "--mode" in result.output
        assert "auto" in result.output


class TestSplitCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_split_help(self):
        result = self.runner.invoke(main, ["split", "--help"])
        assert result.exit_code == 0
        assert "INPUT_FILE" in result.output
        assert "OUTPUT_DIR" in result.output
        assert "--mode" in result.output
        assert "--sample-rate" in result.output
        assert "--precise" in result.output
        assert "--skip-preamble" in result.output
        assert "--slate-buffer" in result.output
        assert "--dry-run" in result.output

    def test_split_missing_input(self):
        result = self.runner.invoke(main, ["split", "/nonexistent/video.mp4", "/tmp/out"])
        assert result.exit_code != 0

    def test_split_with_mode(self):
        """--mode qr is accepted in help output."""
        result = self.runner.invoke(main, ["split", "--help"])
        assert "auto" in result.output
        assert "qr" in result.output
        assert "ocr" in result.output

    def test_help_shows_split_command(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "split" in result.output

    @pytest.fixture(autouse=True)
    def _skip_without_cv2(self):
        pytest.importorskip("cv2")

    def test_split_dry_run(self, make_multi_scene_video, tmp_path):
        """Dry run shows the split plan without creating files."""
        import shutil

        pytest.importorskip("qrcode")
        pytest.importorskip("pyzbar")

        if shutil.which("ffmpeg") is None:
            pytest.skip("ffmpeg not available")

        video_path, _ = make_multi_scene_video("cli_dry_run.mp4")
        output_dir = tmp_path / "output"

        result = self.runner.invoke(
            main,
            ["split", str(video_path), str(output_dir), "--dry-run", "--mode", "qr"],
        )
        assert result.exit_code == 0
        assert "dry run" in result.output
        assert not output_dir.exists()
