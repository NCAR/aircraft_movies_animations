# Timeseries Animation

![Frame](https://github.com/tthomas88/timeseries_animation/blob/master/wecanexample.png)


## Required packages

The code needs Python 3, FFmpeg (`ffmpeg` + `ffprobe`), and the Python packages
numpy, matplotlib, xarray, netcdf4, pandas, and cartopy. `netcdf4` is the xarray
backend that reads the `.nc` flight data files — without it xarray raises
`ValueError: found the following matches ... but their dependencies may not be
installed`.

### AlmaLinux 9 (EOL servers)
```
dnf install python3
dnf install ffmpeg
dnf install ffprobe
pip install numpy matplotlib xarray netcdf4 pandas cartopy
```

### macOS
On a Mac, install FFmpeg with Homebrew and the Python stack with conda from the
`environment.yml` shipped with the repo (conda-forge ships cartopy with its
native GEOS/PROJ/shapely dependencies, which plain `pip` does not):
```
brew install ffmpeg            # also provides ffprobe
conda env create -f environment.yml
conda activate animation
```
## Summary

In order to create movies with animations, you must first create or download a digital camera movie (.mp4) for your desired project and flight. If you have access to EOL servers, you can find processed movies available in `/scr/raf/Raw_Data/<PROJECT>`. If you do not already have the Low Rate netCDF flight data file, you can  download it from the EOL Data Archive or access under `/scr/raf/Prod_Data/<PROJECT>/LRT`. When you have the digital camera movie and netCDF, you are ready to configure the script to create and combine the set of animated plots. Download the code from this GitHub repo: [https://github.com/NCAR/aircraft_movies_animations]

`timeseries_animation.py` is a program that reads variables from a config file `animation_config.py` and uses them to create a set of animated timeseries sub-plots that are time-aligned and combined with a .mp4 file. The list of variables 'Var1' to 'Var8' are used to select variables from a supplied netCDF file for the given flight.

If you aren't sure which variables exist in the netCDF file that you have downloaded, you execute the following from a unix shell: `ncdump -h file.nc | grep float`. This will print a list of variables from the header of file.nc.

'Var1' to 'Var6' are plotted as time series while 'Var7' and 'Var8' are plotted as an animated scatter plot in the lower left of the frame. The plots are set to autoscale to the minimum and maximum value of the selected variable during the flight selected. 

The y-axis of each plot is labeled with the variable name and the units from the netCDF variable attribute 'units'. The line color in the timeseries animation can also be defined based on the input in the parameter file.

Once the animation is created, the program calls FFmpeg to set the duration and frame count using a corresponding digital camera movie located in the user defined `flight_movie_dir`. Once the animation .mp4 and the digital camera movie .mp4 files have identical duration, the FFmpeg utility is called to combine the two .mp4 files into a single .mp4 file that has the camera images displayed the left and the timeseries animation displayed on the right, with time synchronized variables displayed as the aircraft images are updated.

The variables in the parameter file will need to be updated to reflect your project, flight, paths, and variables.

## Running tests

Unit tests use only the Python standard library (`unittest`), so they run
without matplotlib, cartopy, or any data files:

- `test_layout.py` (with `layout.py`) verifies that both supported `VARLIST`
  styles (two variables on one plot, and two variables plotted against each
  other) map onto the subplot grid correctly.
- `test_paths.py` (with `paths.py`) verifies that the platform directory under
  `PROJ_DIR/project` is parsed correctly, including with extra files, oddly
  named entries, and multiple directories (which prompt for a selection).

Run all tests from the repo root with:
```
python3 -m unittest discover
```
Or run a single suite, optionally with `-v` for per-test output:
```
python3 -m unittest test_layout -v
python3 -m unittest test_paths -v
python3 -m unittest test_config_loader -v
```

### To run golden-master tests of animate.plot (the figure/animation builder)
### (useful for confirming refactor doesn't break anything)
First time,
```
conda env create -f environment.yml
```
Then just run:
```
conda run -n animation python -m unittest test_subplot_animation -v
```
