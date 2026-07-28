#! /usr/bin/env python3

#######################################################################
# Unit tests for the --flight command line option.
#
# Covers parsing of -f/--flight and the flight selection in main(): a
# --flight argument supersedes the flights list in animation_config.py
# (the per-flight case called from push_data.py), and leaving it off
# processes every flight in the config.
#
# Nothing here draws or reads data, but importing timeseries_animation
# pulls in cartopy/xarray, so (as in test_subplot_animation) the suite is
# skipped cleanly when those are unavailable and `python3 -m unittest
# discover` still works in a bare environment.
#
# Run with:  python3 -m unittest test_timeseries_animation
#######################################################################

import types
import unittest
from unittest import mock

try:
    import timeseries_animation
    from timeseries_animation import RunContext
    HAVE_DEPS = True
    _IMPORT_ERR = None
except Exception as exc:          # pragma: no cover - depends on env
    HAVE_DEPS = False
    _IMPORT_ERR = exc


@unittest.skipUnless(HAVE_DEPS,
                     'graphics stack unavailable: %s' % (_IMPORT_ERR,))
class FlightArgTests(unittest.TestCase):
    """Parsing of the -f/--flight option itself."""

    def parse(self, argv):
        with mock.patch("sys.argv", ["timeseries_animation.py"] + argv):
            return timeseries_animation.parse_args()

    def test_defaults_to_none(self):
        # No --flight means fall back to the config's flights list.
        self.assertIsNone(self.parse([]).flight)

    def test_long_option(self):
        self.assertEqual(self.parse(["--flight", "rf05"]).flight, "rf05")

    def test_short_option(self):
        # push_data.py may call either spelling.
        self.assertEqual(self.parse(["-f", "rf05"]).flight, "rf05")


@unittest.skipUnless(HAVE_DEPS,
                     'graphics stack unavailable: %s' % (_IMPORT_ERR,))
class FlightSelectionTests(unittest.TestCase):
    """Which flights main() loops over, given --flight or not."""

    def setUp(self):
        self.processed = []
        self.cfg = types.SimpleNamespace(flights=["rf01", "rf02", "rf03"])

        self._patches = [
            # Stand in for the environment/path validation so the tests do not
            # need DATA_DIR et al. or any real directories.
            mock.patch.object(
                timeseries_animation, "setup_run_vars",
                return_value=RunContext(project="TEST", dat="/dat",
                                        flight_movie_dir="/movies",
                                        output_dir="/out")),
            mock.patch.object(timeseries_animation.config_loader, "load",
                              return_value=self.cfg),
            mock.patch.object(timeseries_animation, "dir_check"),
            # Record each flight main() hands off, and skip opening data files.
            mock.patch.object(
                timeseries_animation, "setup_flight_vars",
                side_effect=lambda flight, run: self.processed.append(flight)),
            mock.patch.object(timeseries_animation.animate, "plot"),
            mock.patch("builtins.print"),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in self._patches:
            patch.stop()

    def run_main(self, argv):
        # --preview keeps main() out of the movie/ffmpeg path, which is not
        # what these tests are about.
        with mock.patch("sys.argv",
                        ["timeseries_animation.py", "--preview"] + argv):
            timeseries_animation.main()

    def test_flight_arg_supersedes_config_list(self):
        self.run_main(["--flight", "rf02"])
        self.assertEqual(self.processed, ["rf02"])

    def test_flight_arg_need_not_be_in_config_list(self):
        # The usual deployment case: the config is left at its "rfxx"
        # placeholder and the flight comes from push_data.py.
        self.cfg.flights = ["rfxx"]
        self.run_main(["--flight", "rf07"])
        self.assertEqual(self.processed, ["rf07"])

    def test_config_list_used_when_flight_arg_omitted(self):
        self.run_main([])
        self.assertEqual(self.processed, ["rf01", "rf02", "rf03"])

    def test_flight_arg_does_not_modify_config_list(self):
        # The config object is shared for the whole run, so selecting one
        # flight must not rewrite it.
        self.run_main(["--flight", "rf02"])
        self.assertEqual(self.cfg.flights, ["rf01", "rf02", "rf03"])


if __name__ == '__main__':
    unittest.main()
