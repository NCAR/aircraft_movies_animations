#! /usr/bin/env python3

########################################################################
# Script to create animations of selected variables from a given
# project and flight
# Duration is determined based on duration of the already created mp4
# Separate .mp4 files are combined using ffmpeg to create final data
# Product with movie and animation.
#
# Copyright (2026) University Corporation for Atmospheric Research
#
# Author: TMT
#######################################################################

from __future__ import annotations  # allow `str | None` on Python 3.9
import argparse
from dataclasses import dataclass
import math
import config_loader
from paths import find_platform
import animate
import xarray as xr
import os
import fnmatch
import subprocess
import logging
import cartopy.feature as cf
import cartopy.crs as ccrs
from datetime import datetime
import re

# Class to hold configuration so we don't need global vars and dependencies
# are more easily traced.
@dataclass
class FlightContext:
    '''Per-flight values discovered by setup_flight_vars and consumed by
    animate.plot and process_animation. Bundling them into one returned
    object keeps the data flow between those functions explicit instead of
    routing it through module globals.

    flight_data, save_file, lats and lons are always set (lats/lons come from
    the data file's global attributes). The movie-dependent fields
    (flight_movie, flight_time) stay None when no camera movie matching the
    flight is found.'''
    flight_data: str                  # path to the flight's .nc data file
    save_file: str                    # path the animation mp4 is written to
    flight_movie: str | None = None   # camera movie filename, if found
    flight_time: slice | None = None  # time slice spanning the movie
    lats: tuple | None = None         # (min, max) latitude bounds
    lons: tuple | None = None         # (min, max) longitude bounds

@dataclass
class RunContext:
    '''Run-level values computed once in main() and shared, unchanged, by every
    flight in the run. These were previously module globals; bundling them into
    one object passed to setup_flight_vars and process_animation removes the
    globals while keeping the per-run scope distinct from the per-flight
    FlightContext.'''
    project: str           # project name, e.g. "TI3GER-2"
    dat: str               # flight data dir: $DATA_DIR/<project>
    flight_movie_dir: str  # camera movies dir: $RAW_DATA_DIR/<project>/Movies/
    output_dir: str        # output dir: $RAW_DATA_DIR/<project>/Animations/

# Define function to check to make sure supplied vars are in the .nc file

def dir_check(directory):

    if not os.path.isdir(directory):
        try:
            os.mkdir(directory)
        except Exception:
            message = 'Could not make raw directory:' + directory
            logging.error(message)
            logging.error('Bailing out')
            exit(1)

def process_animation(flight_vars, flight, cfg, run, render=True):
    print('*******************************************')
    print('******   Starting flight animation   ******')
    print('*******************************************')
    print('Using flight data file: ' + flight_vars.flight_data)

    if render:
        animate.plot(flight_vars, cfg)
    elif not os.path.exists(flight_vars.save_file):
        print('Cannot combine: ' + flight_vars.save_file + ' does not exist. '
              'Run without --combine-only first to create the frames.')
        return

    # Use ffmpeg to align the duration based on number of frames and frame rates
    # This will get the duration of the flight movie file and store as a
    # variable
    Duration1 = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1',
         run.flight_movie_dir + flight_vars.flight_movie])
    Duration1 = float(Duration1)

    # This sets frame rate for the animation file and store as a variable
    Duration2 = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', flight_vars.save_file])
    Duration2 = float(Duration2)

    # Perform the calculation
    scalefactor = str(Duration1 / Duration2)

    # Extract the hieght from the camera image .mp4 for use in the creation of
    # the animations
    height = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=height',
         '-of', 'csv=p=0:s=x', run.flight_movie_dir + flight_vars.flight_movie])
    height = height.rstrip().decode('utf-8')
    dims = cfg.width+height

    # The ffmpeg intermediates and the final combined mp4 all live alongside
    # save_file in output_dir. Build the mid_/final_ names from the basename
    # so the prefix is not prepended to the directory path.
    base = os.path.basename(flight_vars.save_file)
    mid_file = os.path.join(run.output_dir, 'mid_' + base)
    final_file = os.path.join(run.output_dir, 'final_' + base)
    output_file = os.path.join(run.output_dir, run.project + flight + '.mp4')

    # Update duration of the animation mp4 to align with flight movie
    subprocess.run(['ffmpeg', '-i', flight_vars.save_file,
                    '-filter:v', 'setpts=' + scalefactor + '*PTS',
                    mid_file], check=True)

    subprocess.run(['ffmpeg', '-i', mid_file, '-s', dims,
                    '-c:a', 'copy', final_file], check=True)

    subprocess.run(['ffmpeg', '-i', run.flight_movie_dir + flight_vars.flight_movie,
                    '-i', final_file,
                    '-filter_complex', 'hstack,format=yuv420p',
                    '-c:v', 'libx264', '-crf', '18', output_file], check=True)

    os.remove(mid_file)
    os.remove(final_file)

def get_flight_area(dataset):
        # Assuming 'dataset' is an xarray Dataset with the required attributes
    max_lat = dataset.attrs['geospatial_lat_max']
    min_lat = dataset.attrs['geospatial_lat_min']
    max_lon = dataset.attrs['geospatial_lon_max']
    min_lon = dataset.attrs['geospatial_lon_min']

    # Return the latitude and longitude bounds
    return (math.floor(min_lat), math.ceil(max_lat)), \
            (math.floor(min_lon), math.ceil(max_lon))

def create_time_slice(filename):
    # Parse the start time
    filename = filename.rsplit('.mp4', 1)[0]
    time_part = ''.join(filename.split('.', 1)[1:]) # This assumes the format
                                                    # is always as described
    
    # Step 2: Split the time part into start and end times
    start_time_str, end_time_str = time_part.split('_')
    start_time = datetime.strptime(start_time_str, '%y%m%d.%H%M%S')
    
    # Extract the date part from the start time
    start_date_str = start_time.strftime('%y%m%d')
    
    # Combine the start date with the end time's time part
    # Assuming end_time_str format is '%H:%M:%S' and needs to be combined with
    # the start date
    end_time_full_str = f"{start_date_str}.{end_time_str}"
    
    # Parse the modified end time string
    end_time = datetime.strptime(end_time_full_str, '%y%m%d.%H%M%S')
    
    # Format the times as a slice
    time_slice = slice(start_time, end_time)
    
    return time_slice

def setup_flight_vars(flight, run):
    '''
    Gather the variables needed for plotting and animation for each flight
    and return them as a FlightContext. flight_data and save_file are always
    set; the movie-dependent fields are filled in only if a camera movie
    matching the flight is found.
    '''

    # PROJECT-SPECIFIC FIX
    # The TI3GER-2 data files drop the dash in their names (e.g. TI3GER2rf01.nc)
    # even though the project directory keeps it.
    file_project = run.project.replace('-', '') if run.project == 'TI3GER-2' else run.project

    flight_data = f"{run.dat}/{file_project}{flight}.nc"

    anim_file = xr.open_dataset(flight_data)
    # Write all generated files (animation, preview image, ffmpeg
    # intermediates, final combined mp4) to output_dir.
    save_file = os.path.join(run.output_dir, run.project + flight + 'animation.mp4')

    flight_vars = FlightContext(flight_data=flight_data, save_file=save_file)
    # lats/lons come from the data file's global attributes, not the camera
    # movie. Set them unconditionally so can run in --preview mode and test
    # plot layout when no movie is present.
    flight_vars.lats, flight_vars.lons = get_flight_area(anim_file)
    for file in os.listdir(run.flight_movie_dir):
        if fnmatch.fnmatch(file, '*' + flight + '*.mp4'):
            flight_vars.flight_movie = file
            flight_vars.flight_time = create_time_slice(file)
    return flight_vars

def parse_args():
    """ Instantiate a command line argument parser """

    parser = argparse.ArgumentParser(
        description='Create timeseries animations for the configured flights.')
    parser.add_argument('-p', '--project',
                        help='Project name (e.g. CAESAR). Falls back to the '
                             '$PROJECT environment variable. On the first run '
                             'for a project the config template is copied into '
                             'the project scripts dir for you to edit.')
    parser.add_argument('--preview', action='store_true',
                        help='Render only the first frame of each flight to a '
                             'PNG and skip the mp4 encode, to check the layout.')
    parser.add_argument('--combine-only', action='store_true',
                        help='Skip frame rendering and reuse the existing '
                             'animation mp4, only running the ffmpeg combine '
                             'steps. Use to rerun ffmpeg without recreating '
                             'frames.')
    args = parser.parse_args()

    return args

def setup_run_vars(args):
    '''Validate the environment and gather the run-level values into a
    RunContext. Mirrors setup_flight_vars: it computes the values shared by
    every flight in the run (project name and the data/movie/output dirs)
    and returns them as one object, so main() does not handle them piecemeal.
    Exits if a required environment variable is missing.'''

    # Check for required environment variables. Exit if not found.
    for var in ('DATA_DIR', 'RAW_DATA_DIR', 'PROJ_DIR'):
        if var not in os.environ:
            print(var + ' environment variable not set.')
            exit(1)

    # Determine project
    project = config_loader.resolve_project(args.project)

    # Build the paths to the data directories based on the environment variables
    return RunContext(
        project=project,
        # - Location of the flight data
        dat=os.path.join(os.environ['DATA_DIR'], project),
        # - Where the existing digital camera movies are located
        flight_movie_dir=os.path.join(os.environ['RAW_DATA_DIR'], project,
                                      "Movies/"),
        # - Where the output .mp4 files will be written
        output_dir=os.path.join(os.environ['RAW_DATA_DIR'], project,
                                "Animations/"),
    )

def main():

    # Process command line arguments.
    args = parse_args()

    # Gather the run-level values (project + data/movie/output dirs) shared by
    # every flight, instead of routing them through module globals.
    run = setup_run_vars(args)

    # Read the configuration file. On the first run for a project (no config in
    # $PROJ_DIR/<project>/<platform>/scripts), copy the template there and stop
    # so template can be configured for the project.
    cfg = config_loader.load(run.project)

    # Perform checks to see if dirs are already present, make them if not
    dir_check(run.dat)
    dir_check(run.flight_movie_dir)
    dir_check(run.output_dir)

    for flight in cfg.flights:
        flight_vars = setup_flight_vars(flight, run)

        if args.preview:
            # Only create one frame then exit. Useful when determining if the
            # generated plots are correct.
            animate.plot(flight_vars, cfg, preview=True)
            continue

        # Read in the movie file created from CombineCameras.pl
        if flight_vars.flight_movie is not None and os.path.exists(run.flight_movie_dir + flight_vars.flight_movie):

            process_animation(flight_vars, flight, cfg, run,
                              render=not args.combine_only)

        # If the movie file doesn't exist, then see if the user wants to make it
        else:
            print('Could not find a camera images .mp4 file in: ' +
                  run.flight_movie_dir + flight + '*')
            print('Please download .mp4 file from https://data.eol.ucar.edu/')
            process = input('If you are at NCAR RAF and you would like to ' + \
                            'generate the camera images .mp4 file, press ' + \
                            'Enter. Anything else will not process.')

            if process == '':
                proj_path = os.path.join(os.environ["PROJ_DIR"], run.project)
                # The platform (e.g. GV_N677F) is the directory component that
                # sits under PROJ_DIR/project.
                platform = find_platform(proj_path)
                script = os.path.join(proj_path, platform, "scripts",
                                      "createMovies.sh")
                command = [script,'-p',run.project,flight]
                print(command)
                subprocess.run(command, check=True)

            elif process != '':
                print('Please download the desired .mp4 camera images file' +
                      'and start again.')
                exit(1)


if __name__ == '__main__':

    main()
