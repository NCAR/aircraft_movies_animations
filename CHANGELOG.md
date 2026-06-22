# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Build data and movie locations from environment variables (`DATA_DIR`,
  `RAW_DATA_DIR`) instead of hardcoded paths.
- Read flight data with xarray; no longer depends on `nc_utils`.
- Refactored the animation to handle multiple plot configurations flexibly,
  including pairing two variables in a single plot.
- Documented required packages and added a "Running tests" section in the
  README.

### Fixed
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
