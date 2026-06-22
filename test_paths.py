#! /usr/bin/env python3

#######################################################################
# Unit tests for paths.find_platform.
#
# Builds temporary PROJ_DIR/project trees to verify the platform
# directory is parsed correctly in the presence of extra files,
# oddly named entries, and multiple directories.
#
# Run with:  python3 -m unittest test_paths
#######################################################################

import os
import tempfile
import unittest
from unittest import mock

from paths import find_platform


class FindPlatformTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj_path = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _make_platform(self, name, with_scripts=True):
        '''Create a directory <proj_path>/<name>, optionally with scripts/.'''
        base = os.path.join(self.proj_path, name)
        os.makedirs(os.path.join(base, "scripts") if with_scripts else base)
        return base

    def _make_file(self, name):
        with open(os.path.join(self.proj_path, name), "w") as handle:
            handle.write("")

    def test_single_platform(self):
        self._make_platform("GV_N677F")
        self.assertEqual(find_platform(self.proj_path), "GV_N677F")

    def test_ignores_stray_files(self):
        # Files, even ones that look like platform names, must be ignored.
        self._make_platform("C130_N130AR")
        self._make_file("README.txt")
        self._make_file("GV_N677F")  # a file, not a directory
        self._make_file(".DS_Store")
        self.assertEqual(find_platform(self.proj_path), "C130_N130AR")

    def test_ignores_directories_without_scripts(self):
        # Unrelated directories (no scripts subdir) must not be chosen.
        self._make_platform("logs", with_scripts=False)
        self._make_platform("Movies", with_scripts=False)
        self._make_platform("GV_N677F")
        self.assertEqual(find_platform(self.proj_path), "GV_N677F")

    def test_ignores_weirdly_named_entries(self):
        self._make_platform("weird name with spaces", with_scripts=False)
        self._make_platform("a-b.c_123", with_scripts=False)
        self._make_file("!@#$.tmp")
        self._make_platform("GV_N677F")
        self.assertEqual(find_platform(self.proj_path), "GV_N677F")

    def test_multiple_platforms_prompts_for_selection(self):
        self._make_platform("GV_N677F")
        self._make_platform("C130_N130AR")
        # Candidates are listed sorted: 1=C130_N130AR, 2=GV_N677F.
        with mock.patch("builtins.input", return_value="2"):
            self.assertEqual(find_platform(self.proj_path), "GV_N677F")

    def test_multiple_platforms_reprompts_on_invalid_input(self):
        self._make_platform("GV_N677F")
        self._make_platform("C130_N130AR")
        # Non-numeric, out-of-range, then a valid choice (1=C130_N130AR).
        with mock.patch("builtins.input", side_effect=["x", "0", "9", "1"]):
            self.assertEqual(find_platform(self.proj_path), "C130_N130AR")

    def test_single_platform_does_not_prompt(self):
        self._make_platform("GV_N677F")
        # input() raising ensures it is never called for the single case.
        with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
            self.assertEqual(find_platform(self.proj_path), "GV_N677F")

    def test_no_platform_raises(self):
        self._make_file("only_a_file")
        self._make_platform("not_a_platform", with_scripts=False)
        with self.assertRaises(FileNotFoundError):
            find_platform(self.proj_path)

    def test_empty_project_dir_raises(self):
        with self.assertRaises(FileNotFoundError):
            find_platform(self.proj_path)

    def test_missing_project_dir_raises(self):
        missing = os.path.join(self.proj_path, "does_not_exist")
        with self.assertRaises(FileNotFoundError):
            find_platform(missing)


if __name__ == '__main__':
    unittest.main()
