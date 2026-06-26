#! /usr/bin/env python3

#######################################################################
# Unit tests for config_loader.
#
# Covers project resolution (--project vs $PROJECT), building the
# per-project config path from a temporary PROJ_DIR tree, and the
# seed-or-load behavior on first vs subsequent runs.
#
# Run with:  python3 -m unittest test_config_loader
#######################################################################

import os
import tempfile
import unittest
from unittest import mock

import config_loader
from config_loader import resolve_project, config_path_for, load


class ResolveProjectTests(unittest.TestCase):
    def test_arg_overrides_env(self):
        with mock.patch.dict(os.environ, {"PROJECT": "FROMENV"}):
            self.assertEqual(resolve_project("FROMARG"), "FROMARG")

    def test_falls_back_to_env(self):
        with mock.patch.dict(os.environ, {"PROJECT": "FROMENV"}):
            self.assertEqual(resolve_project(None), "FROMENV")

    def test_empty_arg_falls_back_to_env(self):
        # An empty string is falsy, so $PROJECT still wins.
        with mock.patch.dict(os.environ, {"PROJECT": "FROMENV"}):
            self.assertEqual(resolve_project(""), "FROMENV")

    def test_errors_when_neither_set(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("builtins.print"):
            with self.assertRaises(SystemExit) as cm:
                resolve_project(None)
        self.assertEqual(cm.exception.code, 1)


class ConfigPathForTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj_dir = self._tmp.name
        self.project = "CAESAR"
        self.platform = "GV_N677F"
        # PROJ_DIR/<project>/<platform>/scripts is how find_platform
        # identifies the platform.
        self.scripts_dir = os.path.join(
            self.proj_dir, self.project, self.platform, "scripts")
        os.makedirs(self.scripts_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_builds_path_via_find_platform(self):
        expected = os.path.join(self.scripts_dir, "animation_config.py")
        with mock.patch.dict(os.environ, {"PROJ_DIR": self.proj_dir}):
            self.assertEqual(config_path_for(self.project), expected)


class LoadOrSeedTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj_dir = self._tmp.name
        self.project = "CAESAR"
        self.scripts_dir = os.path.join(
            self.proj_dir, self.project, "GV_N677F", "scripts")
        os.makedirs(self.scripts_dir)
        self.config_path = os.path.join(self.scripts_dir, "animation_config.py")

        # A stand-in template with known, importable settings, so the tests
        # do not depend on the checkout's real animation_config.py.
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False)
        handle.write('flights = ["rf01"]\ndpi = 123\n')
        handle.close()
        self.template_path = handle.name

        self._patches = [
            mock.patch.dict(os.environ, {"PROJ_DIR": self.proj_dir}),
            mock.patch.object(config_loader, "TEMPLATE_PATH", self.template_path),
            mock.patch("builtins.print"),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        os.unlink(self.template_path)
        self._tmp.cleanup()

    def test_seeds_template_and_exits_when_missing(self):
        self.assertFalse(os.path.exists(self.config_path))
        with self.assertRaises(SystemExit) as cm:
            load(self.project)
        # Exit 0: an action is needed, not an error.
        self.assertEqual(cm.exception.code, 0)
        # The template was copied into the scripts dir.
        self.assertTrue(os.path.exists(self.config_path), self.config_path)
        with open(self.config_path) as handle:
            self.assertIn('flights = ["rf01"]', handle.read())

    def test_seeding_fills_in_project_name(self):
        # The template's <project> placeholder gets the real project name
        # substituted in on seed.
        with open(self.template_path, "w") as handle:
            handle.write('### Configuration is for project <project> ###\n'
                         'flights = ["rfxx"]\n')
        with self.assertRaises(SystemExit):
            load(self.project)
        with open(self.config_path) as handle:
            seeded = handle.read()
        self.assertIn("project CAESAR", seeded)
        self.assertNotIn("<project>", seeded)

    def test_loads_existing_config(self):
        with open(self.config_path, "w") as handle:
            handle.write('flights = ["rf09", "rf10"]\n'
                         'VARLIST = ["GGALT"]\n'
                         'dpi = 400\n')
        cfg = load(self.project)
        self.assertEqual(cfg.flights, ["rf09", "rf10"])
        self.assertEqual(cfg.VARLIST, ["GGALT"])
        self.assertEqual(cfg.dpi, 400)

    def test_existing_config_not_reseeded(self):
        # An existing config must be loaded as-is, never overwritten by the
        # template.
        with open(self.config_path, "w") as handle:
            handle.write('flights = ["rf99"]\n')
        cfg = load(self.project)
        self.assertEqual(cfg.flights, ["rf99"])
        with open(self.config_path) as handle:
            self.assertNotIn("rf01", handle.read())


if __name__ == '__main__':
    unittest.main()
