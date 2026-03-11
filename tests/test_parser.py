"""Tests for FilenameParser."""

import pytest

from clipsort.parser import ClipInfo, FilenameParser


class TestClipInfo:
    def test_defaults(self):
        info = ClipInfo(scene=1)
        assert info.scene == 1
        assert info.take is None
        assert info.confidence == 1.0
        assert info.method == "filename"

    def test_equality(self):
        a = ClipInfo(scene=1, take="a")
        b = ClipInfo(scene=1, take="a")
        assert a == b


class TestFilenameParser:
    def setup_method(self):
        self.parser = FilenameParser()

    # --- Scene+letter pattern ---

    @pytest.mark.parametrize(
        "filename, scene, take",
        [
            ("1a.mp4", 1, "a"),
            ("1b.mov", 1, "b"),
            ("2a.mkv", 2, "a"),
            ("12c.mp4", 12, "c"),
            ("3A.mp4", 3, "a"),  # uppercase letter
            ("01a.mp4", 1, "a"),  # leading zero
        ],
    )
    def test_scene_letter(self, filename, scene, take):
        result = self.parser.parse(filename)
        assert result is not None
        assert result.scene == scene
        assert result.take == take

    # --- Scene_take numeric pattern ---

    @pytest.mark.parametrize(
        "filename, scene, take",
        [
            ("1_1.mp4", 1, 1),
            ("2_3.mov", 2, 3),
            ("10-2.mp4", 10, 2),
        ],
    )
    def test_scene_take_numeric(self, filename, scene, take):
        result = self.parser.parse(filename)
        assert result is not None
        assert result.scene == scene
        assert result.take == take

    # --- Scene_Take verbose pattern ---

    @pytest.mark.parametrize(
        "filename, scene, take",
        [
            ("Scene1_Take2.mp4", 1, 2),
            ("scene_01_take_03.mp4", 1, 3),
            ("Scene3Take1.mp4", 3, 1),
            ("scene2_take1.mov", 2, 1),
        ],
    )
    def test_scene_take_verbose(self, filename, scene, take):
        result = self.parser.parse(filename)
        assert result is not None
        assert result.scene == scene
        assert result.take == take

    # --- Short form pattern ---

    @pytest.mark.parametrize(
        "filename, scene, take",
        [
            ("S01T03.mp4", 1, 3),
            ("s1t1.mp4", 1, 1),
            ("S10T02.mov", 10, 2),
        ],
    )
    def test_short_form(self, filename, scene, take):
        result = self.parser.parse(filename)
        assert result is not None
        assert result.scene == scene
        assert result.take == take

    # --- No match ---

    @pytest.mark.parametrize(
        "filename",
        [
            "random_file.txt",
            "behind_the_scenes.mp4",
            "notes.mp4",
            "",
            "..mp4",
        ],
    )
    def test_no_match_returns_none(self, filename):
        result = self.parser.parse(filename)
        assert result is None

    def test_method_includes_pattern_name(self):
        result = self.parser.parse("1a.mp4")
        assert result is not None
        assert "scene_letter" in result.method
