"""Tests for Reporter."""

import io
from pathlib import Path

from clipsort.organizer import OrganizePlan
from clipsort.reporter import Reporter


class TestReporter:
    def setup_method(self):
        self.reporter = Reporter()

    def test_report_basic_output(self):
        plan = OrganizePlan(
            mappings=[
                (Path("1a.mp4"), Path("out/scene_01/1a.mp4")),
                (Path("1b.mp4"), Path("out/scene_01/1b.mp4")),
                (Path("2a.mp4"), Path("out/scene_02/2a.mp4")),
            ],
        )
        buf = io.StringIO()
        self.reporter.report(plan, stream=buf)
        output = buf.getvalue()

        assert "Files processed: 3" in output
        assert "Scenes detected: 2" in output
        assert "scene_01: 2 clip(s)" in output
        assert "scene_02: 1 clip(s)" in output

    def test_report_with_unsorted(self):
        plan = OrganizePlan(
            mappings=[
                (Path("1a.mp4"), Path("out/scene_01/1a.mp4")),
            ],
            unsorted=[Path("random.mp4")],
        )
        buf = io.StringIO()
        self.reporter.report(plan, stream=buf)
        output = buf.getvalue()

        assert "Unsorted: 1 file(s)" in output
        assert "random.mp4" in output

    def test_report_with_conflicts(self):
        plan = OrganizePlan(
            mappings=[
                (Path("1a.mp4"), Path("out/scene_01/1a.mp4")),
                (Path("dir2/1a.mp4"), Path("out/scene_01/1a_2.mp4")),
            ],
            conflicts=[
                (
                    Path("dir2/1a.mp4"),
                    Path("out/scene_01/1a.mp4"),
                    Path("out/scene_01/1a_2.mp4"),
                ),
            ],
        )
        buf = io.StringIO()
        self.reporter.report(plan, stream=buf)
        output = buf.getvalue()

        assert "Conflicts resolved: 1" in output

    def test_report_empty_plan(self):
        plan = OrganizePlan()
        buf = io.StringIO()
        self.reporter.report(plan, stream=buf)
        output = buf.getvalue()

        assert "Files processed: 0" in output
        assert "Scenes detected: 0" in output

    def test_report_with_methods(self):
        plan = OrganizePlan(
            mappings=[
                (Path("1a.mp4"), Path("out/scene_01/1a.mp4")),
                (Path("2a.mp4"), Path("out/scene_02/2a.mp4")),
            ],
            methods={"1a.mp4": "filename:scene_letter", "2a.mp4": "qr"},
        )
        buf = io.StringIO()
        self.reporter.report(plan, stream=buf)
        output = buf.getvalue()

        assert "Detection methods:" in output
        assert "1a.mp4: filename:scene_letter" in output
        assert "2a.mp4: qr" in output

    def test_report_without_methods_omits_section(self):
        plan = OrganizePlan(
            mappings=[
                (Path("1a.mp4"), Path("out/scene_01/1a.mp4")),
            ],
        )
        buf = io.StringIO()
        self.reporter.report(plan, stream=buf)
        output = buf.getvalue()

        assert "Detection methods:" not in output

    def test_save_to_file(self, tmp_path):
        plan = OrganizePlan(
            mappings=[
                (Path("1a.mp4"), Path("out/scene_01/1a.mp4")),
            ],
        )
        report_path = tmp_path / "report.txt"
        self.reporter.save(plan, report_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "Files processed: 1" in content
