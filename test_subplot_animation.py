#! /usr/bin/env python3

#######################################################################
# Characterization ("golden master") tests for animate.plot.
#
# animate.plot() loads data, builds the matplotlib figure, defines the
# animate closure, and saves the mp4 (or a preview PNG) all in one call.
# These tests pin down its *current* observable behavior so a refactor
# can be confirmed not to change it.
#
# Unlike test_layout / test_paths / test_config_loader (which are
# deliberately stdlib-only), these tests require the full graphics stack
# (matplotlib, xarray, cartopy, pandas, numpy). They are skipped cleanly
# when those imports are unavailable, so `python3 -m unittest discover`
# still works in a bare environment.
#
# To make them hermetic the tests:
#   * patch animate.xr.open_dataset to return a small in-memory dataset
#     (no .nc file needed),
#   * patch animate.animation.FuncAnimation and Figure.savefig so no mp4
#     is encoded (no ffmpeg) and cartopy never draws to disk.
#
# The plotting configuration (VARLIST, colors, dpi, fps) is supplied via
# a small cfg object, exactly as the real config_loader hands one to
# plot(); the per-flight values come through a FlightContext.
#
# IMPORTANT: run this against the UNCHANGED code first and confirm it
# passes. A golden-master test is only meaningful once it is green on
# the current behavior; only then does a later failure mean the refactor
# changed something.
#
# Run with:  python3 -m unittest test_subplot_animation -v
#######################################################################

import contextlib
import types
import unittest
from unittest import mock

try:
    import matplotlib
    matplotlib.use('Agg')          # headless; no GUI backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np
    import pandas as pd
    import xarray as xr
    import cartopy.crs as ccrs
    from cartopy.mpl.geoaxes import GeoAxes
    import animate
    import timeseries_animation as ts
    HAVE_DEPS = True
    _IMPORT_ERR = None

    # Deterministic sample data (5 time steps) so every derived limit/label
    # below is exact. Defined only when numpy is importable; the suite is
    # skipped otherwise, so nothing references these names at runtime.
    GGALT = np.array([100., 200., 150., 300., 250.])     # units 'm'
    ATX = np.array([10., 12., 11., 9., 8.])              # units 'degC'
    DPXC = np.array([5., 7., 6., 4., 3.])                # units 'degC'
    GGLON = np.array([-105., -104., -103., -102., -101.])
    GGLAT = np.array([40., 41., 42., 43., 44.])
except Exception as exc:          # pragma: no cover - depends on env
    HAVE_DEPS = False
    _IMPORT_ERR = exc


# A small VARLIST that exercises every branch of _create_subplot / the
# plotting loop exactly once:
#   entry 1  "GGALT"                  -> 'time'  (plain variable vs time)
#   entry 2  ("GGALT", "ATX")         -> 'pair'  (2-tuple, single line)
#   entry 3  ("GGALT", "ATX", "DPXC") -> 'pair'  (3-tuple, two lines + legend)
#   entry 4  ("GGLON", "GGLAT")       -> 'map'   (trailing lat/lon GeoAxes)
VARLIST = ["GGALT", ("GGALT", "ATX"), ("GGALT", "ATX", "DPXC"),
           ("GGLON", "GGLAT")]
LATS = (40, 44)
LONS = (-105, -101)
N_FRAMES = 5

# Plotting config values plot() reads off the cfg object.
LINE_COLOR = 'blue'
LINE_COLOR2 = 'green'
POINT_COLOR = 'red'
DPI = 100
FPS = 10


def _build_dataset():
    '''In-memory xarray Dataset standing in for the flight .nc file.'''
    times = pd.date_range('2020-01-01T00:00:00', periods=N_FRAMES, freq='s')

    def da(values, units):
        return xr.DataArray(values, dims=['Time'],
                            coords={'Time': times}, attrs={'units': units})

    return xr.Dataset({
        'GGALT': da(GGALT, 'm'),
        'ATX': da(ATX, 'degC'),
        'DPXC': da(DPXC, 'degC'),
        'GGLON': da(GGLON, 'degree_east'),
        'GGLAT': da(GGLAT, 'degree_north'),
    })


def _build_cfg():
    '''Stand-in for the object config_loader.load() hands to plot().'''
    return types.SimpleNamespace(
        VARLIST=VARLIST,
        LineColor=LINE_COLOR, LineColor2=LINE_COLOR2, PointColor=POINT_COLOR,
        dpi=DPI, fps=FPS,
    )


@unittest.skipUnless(HAVE_DEPS,
                     'graphics stack unavailable: %s' % (_IMPORT_ERR,))
class SubplotAnimationCharacterizationTests(unittest.TestCase):
    '''Drives animate.plot() and inspects the figure it builds.'''

    def setUp(self):
        self.dataset = _build_dataset()
        self.cfg = _build_cfg()

    def _flight_vars(self, with_movie=True):
        '''A FlightContext as setup_flight_vars would return it. With a movie,
        flight_time is the slice spanning the data; without one (e.g. a
        --preview run with no camera movie) flight_time is None but lats/lons
        are still set from the data file.'''
        times = self.dataset.Time.values
        return ts.FlightContext(
            flight_data='dummy.nc',
            save_file='/tmp/out/PROJrf01animation.mp4',
            flight_time=slice(times[0], times[-1]) if with_movie else None,
            lats=LATS, lons=LONS,
        )

    @contextlib.contextmanager
    def _run(self, preview, flight_vars=None):
        '''Run animate.plot() under the necessary patches; yield
        (figure, FuncAnimation mock, savefig mock).'''
        created = {}
        real_figure = plt.figure

        def capture_figure(*a, **k):
            fig = real_figure(*a, **k)
            created['fig'] = fig
            return fig

        if flight_vars is None:
            flight_vars = self._flight_vars()

        with mock.patch.object(animate.xr, 'open_dataset',
                               return_value=self.dataset), \
             mock.patch.object(animate.plt, 'figure',
                               side_effect=capture_figure), \
             mock.patch.object(animate.animation, 'FuncAnimation') as func_anim, \
             mock.patch.object(Figure, 'savefig') as savefig:
            animate.plot(flight_vars, self.cfg, preview=preview)
            try:
                yield created['fig'], func_anim, savefig
            finally:
                plt.close(created['fig'])

    # ---- figure structure -------------------------------------------------

    def test_one_axis_per_varlist_entry(self):
        with self._run(preview=False) as (fig, _fa, _sf):
            self.assertEqual(len(fig.axes), len(VARLIST))

    def test_time_axis_labels_and_ylim(self):
        with self._run(preview=False) as (fig, _fa, _sf):
            ax = fig.axes[0]                       # "GGALT" vs time
            self.assertEqual(ax.get_xlabel(), 'Time [Hour]')
            self.assertEqual(ax.get_ylabel(), 'GGALT [m]')
            self.assertEqual(ax.get_ylim(), (GGALT.min(), GGALT.max()))
            # data line + moving point
            self.assertEqual(len(ax.get_lines()), 2)
            self.assertIsNone(ax.get_legend())

    def test_single_pair_axis(self):
        with self._run(preview=False) as (fig, _fa, _sf):
            ax = fig.axes[1]                       # ("GGALT", "ATX")
            self.assertEqual(ax.get_xlabel(), 'GGALT [m]')
            self.assertEqual(ax.get_ylabel(), 'ATX [degC]')
            self.assertEqual(ax.get_xlim(), (GGALT.min(), GGALT.max()))
            self.assertEqual(ax.get_ylim(), (ATX.min(), ATX.max()))
            self.assertEqual(len(ax.get_lines()), 2)   # point + line
            self.assertIsNone(ax.get_legend())

    def test_double_pair_axis_has_two_lines_and_legend(self):
        with self._run(preview=False) as (fig, _fa, _sf):
            ax = fig.axes[2]                       # ("GGALT","ATX","DPXC")
            self.assertEqual(ax.get_xlabel(), 'GGALT [m]')
            # ylabel combines both y-variable names with var[1]'s units
            self.assertEqual(ax.get_ylabel(), 'ATX DPXC [degC]')
            self.assertEqual(ax.get_xlim(), (GGALT.min(), GGALT.max()))
            # y-limits span both ATX and DPXC
            lo = min(ATX.min(), DPXC.min())
            hi = max(ATX.max(), DPXC.max())
            self.assertEqual(ax.get_ylim(), (lo, hi))
            self.assertEqual(len(ax.get_lines()), 4)   # 2 lines + 2 points
            self.assertIsNotNone(ax.get_legend())

    def test_map_axis_is_geoaxes_with_configured_extent(self):
        with self._run(preview=False) as (fig, _fa, _sf):
            ax = fig.axes[3]                       # ("GGLON", "GGLAT")
            self.assertIsInstance(ax, GeoAxes)
            # cartopy pads the requested extent slightly when reconciling the
            # axes aspect, and the exact padding is cartopy-version-dependent.
            # Use a generous tolerance: this only needs to confirm the
            # FlightContext lats/lons were wired into set_extent (a real bug
            # would be degrees off), not the exact post-aspect bounds.
            x0, x1, y0, y1 = ax.get_extent(ccrs.PlateCarree())
            self.assertAlmostEqual(x0, LONS[0], delta=1.0)
            self.assertAlmostEqual(x1, LONS[1], delta=1.0)
            self.assertAlmostEqual(y0, LATS[0], delta=1.0)
            self.assertAlmostEqual(y1, LATS[1], delta=1.0)
            # The map keeps its set_extent; no x/y axis labels are applied.
            self.assertEqual(ax.get_xlabel(), '')
            self.assertEqual(ax.get_ylabel(), '')

    # ---- animation wiring -------------------------------------------------

    def test_funcanimation_frame_count_and_save_call(self):
        fv = self._flight_vars()
        with self._run(preview=False, flight_vars=fv) as (fig, func_anim, _sf):
            func_anim.assert_called_once()
            _args, kwargs = func_anim.call_args
            self.assertEqual(kwargs['frames'], N_FRAMES)
            self.assertFalse(kwargs['blit'])
            func_anim.return_value.save.assert_called_once_with(
                fv.save_file, fps=FPS, dpi=DPI)

    def test_animate_sets_growing_line_and_current_point(self):
        with self._run(preview=False) as (fig, func_anim, _sf):
            # Recover the animate closure passed to FuncAnimation and drive it.
            animate_fn = func_anim.call_args.args[1]
            animate_fn(3)
            ax = fig.axes[0]                       # "GGALT" vs time
            line, point = ax.get_lines()
            # The line shows samples [0:3]; the point marks sample 3.
            self.assertEqual(len(line.get_xdata()), 3)
            np.testing.assert_array_equal(line.get_ydata(), GGALT[:3])
            self.assertEqual(len(point.get_xdata()), 1)
            np.testing.assert_array_equal(point.get_ydata(), [GGALT[3]])

    # ---- preview mode -----------------------------------------------------

    def test_preview_saves_frame0_png_and_skips_encode(self):
        with self._run(preview=True) as (fig, func_anim, savefig):
            # Preview renders a single PNG and must not encode the mp4.
            func_anim.assert_not_called()
            savefig.assert_called_once()
            (path,), kwargs = savefig.call_args
            self.assertEqual(
                path, '/tmp/out/PROJrf01animation_frame0.png')
            self.assertEqual(kwargs['dpi'], DPI)

    def test_preview_without_movie_plots_full_flight(self):
        '''A --preview run with no matching camera movie has flight_time=None
        (but lats/lons are still set from the data file). plot() must skip the
        time selection and render the whole flight instead of crashing. Guards
        the fixes for the None time-slice and the unset map extent.'''
        fv = self._flight_vars(with_movie=False)
        with self._run(preview=True, flight_vars=fv) as (fig, func_anim, savefig):
            func_anim.assert_not_called()
            savefig.assert_called_once()
            # Still builds every subplot, including the map with its extent.
            self.assertEqual(len(fig.axes), len(VARLIST))
            map_ax = fig.axes[3]
            self.assertIsInstance(map_ax, GeoAxes)
            x0, x1, y0, y1 = map_ax.get_extent(ccrs.PlateCarree())
            self.assertAlmostEqual(x0, LONS[0], delta=1.0)
            self.assertAlmostEqual(y1, LATS[1], delta=1.0)


if __name__ == '__main__':
    unittest.main()
