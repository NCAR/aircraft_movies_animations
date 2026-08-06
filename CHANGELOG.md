# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Copy animation_config.py to $PROJ_DIR/<project>/<platform>/scripts on first
  run and subsequently read it from there. This allows the config to be saved
  with the project for documentation purposes and easy reuse.
- `-f/--flight` command line option to process a single flight, superseding the
  `flights` list in animation_config.py, for per-flight runs called from
  push_data.py. `test_timeseries_animation.py` unit tests cover the option
  parsing and the flight selection with and without the argument.
- `--combine-only` command line option to rerun the ffmpeg combine steps and
  reuse the existing animation `.mp4` without regenerating frames.
- `--preview` command line option to render only the first frame of each flight
  to a PNG and skip the full encode, for quickly checking plot layout.
- Lat/lon gridlines with value labels on the map subplot.
- Special-case handling for the `TI3GER-2` project, whose data files drop the
  dash in their names (e.g. `TI3GER2rf01.nc`).
- `layout.py` with pure subplot-layout helpers, and `test_layout.py` unit tests
  covering both supported `VARLIST` plot configurations.
- `paths.py` with `find_platform`, which parses the platform directory under
  `PROJ_DIR/project` robustly (ignoring stray files and unrelated
  directories), and `test_paths.py` unit tests covering extra files, oddly
  named entries, and multiple directories.
- Validation that the `PROJ_DIR` environment variable is set.
- Automatic detection of flight area and time, and a plot legend.

### Changed
- Camera movie creation now runs unattended. Instead of asking whether the user
  is at NCAR RAF, run the project's `createMovies.sh` and answer its
  `combineCameras.pl` prompt. What that script and `combineCameras.pl` need
  (the camera scripts, the parameter file template, the flight's camera images,
  ffmpeg) is deliberately not checked up front, so there is no second copy of
  their requirements here to drift out of step with them; if a prerequisite is
  missing they report it themselves and the flight is skipped with a pointer to
  https://data.eol.ucar.edu/.
- After `createMovies.sh` returns, confirm a camera movie is present in
  `flight_movie_dir` before animating, since the script exits 0 even when it
  skips a flight, then pick that flight back up rather than dropping it.
- Moved content of SubplotAnimation class to animate.py and got rid of
  the vestigial class that inherited, but did not use, animation.TimedAnimation
  Refactored logical code blocks into functions
- Group global vars into FlightContext and RunContext data classes.
- Build data and movie locations from environment variables (`DATA_DIR`,
  `RAW_DATA_DIR`) instead of hardcoded paths.
- Read flight data with xarray; no longer depends on `nc_utils`.
- Refactored the animation to handle multiple plot configurations flexibly,
  including pairing two variables in a single plot.
- Documented required packages and added a "Running tests" section in the
  README.
- Documented in animation_config.py that `flights` can be left at `rfxx` during
  a deployment, since `--flight` supersedes it, and is only edited to process
  several flights in bulk.

### Fixed
- flight_time is only set when a matching camera movie is found. In
  preview mode (layout check) plot the whole flight so can check layout
  with no movie present.
- lats/lons come from the data file's global attributes, not the camera
  movie. Set them unconditionally so can run in --preview mode and test
  plot layout when no movie is present.
- The x-axis label of the bottom-left plot was cropped off the bottom of the
  figure. The layout was tightened once per subplot as each was created, so
  the bottom row was sized before it had its axis label and rotated tick
  labels, leaving no room for them. The grid is now tightened a single time,
  after every plot's labels are in place.
- For the GGLON/GGLAT map, tighten the layout before adding it rather than
  skipping the tighten. Its labelled gridlines report an infinite tight
  bounding box, so with the map in the figure newer cartopy versions make
  tight_layout return NaN positions for every subplot and the draw then
  crashes. The map occupies a fixed grid cell, so tightening without it
  leaves its position unchanged.
- Combine step failed with `No such filter: ''` due to a space in the ffmpeg
  `-filter_complex hstack,format=yuv420p` argument under `shell=True`.
- Plotting broke the generic "var1 vs var2" case after the CAESAR special case
  was added; both configurations are now supported.
- Corrected the wind variables.
- Resolved bugs in global variable references and time automation.
- Removed an incorrect variable label and a local path reference.
- Silenced a `MatplotlibDeprecationWarning`.

## [1.0] - 2023-01-06

### Added
- Initial release: create animated timeseries sub-plots from netCDF flight
  data and combine them with a digital camera movie via FFmpeg.
- Plot scaling to the min/max of each selected variable (NaN-aware).
- A second trace on the bottom-left plot.
- README documentation and project LICENSE.
- PEP 8 cleanup, comments, and Python 3 support.

[Unreleased]: https://github.com/NCAR/aircraft_movies_animations/compare/v1.0...HEAD
[1.0]: https://github.com/NCAR/aircraft_movies_animations/releases/tag/v1.0
