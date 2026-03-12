"""Tests for Organizer and OrganizePlan."""

from clipsort.organizer import OrganizePlan, Organizer
from clipsort.parser import ClipInfo


class TestOrganizePlan:
    def test_empty_plan(self):
        plan = OrganizePlan()
        assert plan.mappings == []
        assert plan.unsorted == []
        assert plan.conflicts == []
        assert plan.methods == {}


class TestOrganizer:
    def setup_method(self):
        self.organizer = Organizer()

    def test_plan_groups_by_scene(self, tmp_path):
        files = [
            (tmp_path / "1a.mp4", ClipInfo(scene=1, take="a")),
            (tmp_path / "1b.mp4", ClipInfo(scene=1, take="b")),
            (tmp_path / "2a.mp4", ClipInfo(scene=2, take="a")),
        ]
        output = tmp_path / "out"
        plan = self.organizer.plan(files, output)

        assert len(plan.mappings) == 3
        dests = {d.parent.name for _, d in plan.mappings}
        assert dests == {"scene_01", "scene_02"}

    def test_plan_unsorted_files(self, tmp_path):
        files = [
            (tmp_path / "1a.mp4", ClipInfo(scene=1, take="a")),
            (tmp_path / "random.mp4", None),
        ]
        output = tmp_path / "out"
        plan = self.organizer.plan(files, output)

        assert len(plan.mappings) == 1
        assert len(plan.unsorted) == 1
        assert plan.unsorted[0].name == "random.mp4"

    def test_plan_conflict_resolution(self, tmp_path):
        # Two different source files that would both map to the same dest
        f1 = tmp_path / "dir1" / "1a.mp4"
        f2 = tmp_path / "dir2" / "1a.mp4"
        files = [
            (f1, ClipInfo(scene=1, take="a")),
            (f2, ClipInfo(scene=1, take="a")),
        ]
        output = tmp_path / "out"
        plan = self.organizer.plan(files, output)

        assert len(plan.mappings) == 2
        assert len(plan.conflicts) == 1

        dest_names = {d.name for _, d in plan.mappings}
        assert "1a.mp4" in dest_names
        assert "1a_2.mp4" in dest_names

    def test_plan_custom_folder_format(self, tmp_path):
        files = [
            (tmp_path / "1a.mp4", ClipInfo(scene=1, take="a")),
        ]
        output = tmp_path / "out"
        plan = self.organizer.plan(files, output, folder_format="Scene {scene}")

        _, dest = plan.mappings[0]
        assert dest.parent.name == "Scene 1"

    def test_plan_tracks_methods(self, tmp_path):
        files = [
            (tmp_path / "1a.mp4", ClipInfo(scene=1, take="a", method="filename:scene_letter")),
            (tmp_path / "2a.mp4", ClipInfo(scene=2, take="a", method="qr")),
            (tmp_path / "random.mp4", None),
        ]
        output = tmp_path / "out"
        plan = self.organizer.plan(files, output)

        assert plan.methods == {
            "1a.mp4": "filename:scene_letter",
            "2a.mp4": "qr",
        }
        # Unsorted files should not appear in methods
        assert "random.mp4" not in plan.methods

    def test_execute_copies_files(self, sample_video_dir, tmp_path):
        from clipsort.parser import FilenameParser
        from clipsort.scanner import FileScanner

        scanner = FileScanner()
        parser = FilenameParser()
        files = scanner.scan(sample_video_dir)
        parsed = [(f, parser.parse(f.name)) for f in files]

        output = tmp_path / "out"
        plan = self.organizer.plan(parsed, output)
        count = self.organizer.execute(plan)

        assert count == len(files)
        assert (output / "scene_01").exists()
        assert (output / "scene_02").exists()
        # Originals still exist (copy, not move)
        assert all(f.exists() for f in files)

    def test_execute_moves_files(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        f = src / "1a.mp4"
        f.write_text("content")

        output = tmp_path / "out"
        plan = OrganizePlan(mappings=[(f, output / "scene_01" / "1a.mp4")])
        self.organizer.execute(plan, move=True)

        assert not f.exists()
        assert (output / "scene_01" / "1a.mp4").exists()

    def test_execute_creates_unsorted_dir(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        f1 = src / "1a.mp4"
        f1.write_text("video")
        f2 = src / "random.mp4"
        f2.write_text("video")

        output = tmp_path / "out"
        plan = OrganizePlan(
            mappings=[(f1, output / "scene_01" / "1a.mp4")],
            unsorted=[f2],
        )
        count = self.organizer.execute(plan)
        assert count == 2
        assert (output / "unsorted" / "random.mp4").exists()
