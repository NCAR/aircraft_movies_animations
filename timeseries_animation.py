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

import argparse
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation as animation
import config_loader
from layout import subplot_rows, classify_entry, subplot_position
from paths import find_platform
import xarray as xr
import os
import fnmatch
import shutil
import subprocess
import pandas as pd
import logging
import cartopy.feature as cf
import cartopy.crs as ccrs
from datetime import datetime
import re
from matplotlib.dates import DateFormatter

class SubplotAnimation(animation.TimedAnimation):
    '''
    Animation set up
    Reads the variables listed in the configuration setup
    '''

    def __init__(self, preview=False):

        print('Creating figure subplots')
        fig = plt.figure(figsize=(8, 10))
        plt.rcParams.update({'font.size': 12})
        plt.rc("xtick", labelsize=10)
        plt.rc("ytick", labelsize=10)
        anim_file = xr.open_dataset(flight_data).sel(Time = flight_time)

        ##add map for lat lon plots

        BORDERS2_10m = cf.NaturalEarthFeature('cultural', 'admin_1_states_provinces',
                                              '50m', edgecolor='black', facecolor='none')

        # Your latitude and longitude data
        sub_length = subplot_rows(len(VARLIST))
        axes = []
        lines = []
        x = []
        y = []
        xlims = []
        ylims = []
        xlabs = []
        ylabs = []
        points = []
        def create_subplot(fig, index, var):
            kind = classify_entry(index, len(VARLIST), var)
            nrows, ncols, pos = subplot_position(index, len(VARLIST))
            if kind == 'map':
                # The last entry is always the lat/lon map: place it in the
                # bottom-right quadrant and let it fill the cell (the default
                # 'equal' aspect shrinks it to a narrow box).
                ax = fig.add_subplot(nrows, ncols, pos,
                                     projection=ccrs.PlateCarree())

                ax.coastlines('50m')
                ax.add_feature(cf.OCEAN, facecolor='lightblue')
                ax.add_feature(cf.LAND, facecolor='beige')
                ax.add_feature(BORDERS2_10m, edgecolor='grey')
                ax.set_extent([lons[0], lons[1], lats[0], lats[1]])
                ax.set_aspect('auto')
                # Label the lat/lon axes with gridline values (lon on the
                # bottom, lat on the left).
                gl = ax.gridlines(draw_labels=True, linewidth=0.5,
                                  color='grey', linestyle='--')
                gl.top_labels = False
                gl.right_labels = False
                gl.xlabel_style = {'size': 8}
                gl.ylabel_style = {'size': 8}
            elif kind == 'pair':
                # A parenthesised entry plots one variable against another
                # (e.g. GGALT vs ATX/DPXC), so its x-axis is not time and gets
                # no DateFormatter. May appear anywhere in VARLIST.
                ax = fig.add_subplot(nrows, ncols, pos)
                ax.grid(color='grey', linestyle='--', linewidth=0.5)
            else:
                # A plain variable is plotted against time.
                ax = fig.add_subplot(nrows, ncols, pos)
                ax.grid(color='grey', linestyle='--', linewidth=0.5)
                ax.xaxis.set_major_formatter(DateFormatter('%H%M'))
            return ax
        for i, var in enumerate(VARLIST, start=1):
            #rotation = 25 if i in [5, 6] else None
            ax = create_subplot(fig, i, var)
            fig.tight_layout()
            axes.append(ax)
            print(var)
            if isinstance(var, tuple):
                x1 = anim_file[var[0]]
                y1 = anim_file[var[1]]
                minx = np.nanmin(x1)
                maxx = np.nanmax(x1)
                miny = np.nanmin(y1)
                maxy = np.nanmax(y1)
                xlabel= var[0] + ' [' + anim_file[var[0]].units + ']'
                point = ax.plot([], [], color=PointColor, marker='o', markeredgecolor='r')
                line = ax.plot([], [], color=LineColor, label = var[1])
                if len(var)>2:
                    y2 = anim_file[var[2]]
                    # Make sure that the plot fits both lines
                    miny = np.nanmin(y1) if np.nanmin(y1) < np.nanmin(y2) else np.nanmin(y2)
                    maxy = np.nanmax(y1) if np.nanmax(y1) > np.nanmax(y2) else np.nanmax(y2)
                    line2 = ax.plot([], [], color=LineColor2, linewidth=2, label=var[2]) 
                    point2 = ax.plot([], [], color=PointColor, marker='o', markeredgecolor='r') 
                    ylabel=var[1] + ' '+var[2] +' [' + anim_file[var[1]].units + ']'
                    y.append((y1, y2)) 
                    lines.append([line, line2])
                    points.append([point, point2])
                    ax.set_xlim([minx, maxx])
                    ax.set_ylim([miny, maxy])
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)
                    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2) 
                else:
                    ylabel=var[1] + ' [' + anim_file[var[1]].units + ']'
                    y.append([y1])
                    lines.append([line])
                    points.append([point])
                    if i != len(VARLIST):
                        # Generic variable-vs-variable plot (not the lat/lon
                        # map, whose extent is set by set_extent).
                        ax.set_xlim([minx, maxx])
                        ax.set_ylim([miny, maxy])
                        ax.set_xlabel(xlabel)
                        ax.set_ylabel(ylabel)
                
                ylabs.append(ylabel)
                x.append(x1)
                
                xlims.append([minx, maxx])
                ylims.append([miny, maxy])
                if i <(sub_length+1):
                    ax.xaxis.set_tick_params(labelbottom=False)
            else:
                y1 = anim_file[var]
                print(y1)
                time = pd.to_datetime(y1.Time.values)
                miny = np.nanmin(y1)
                maxy = np.nanmax(y1)
                minx = np.nanmin(time)
                maxx = np.nanmax(time)
                xlabel= 'Time [Hour]' 
                ylabel= var + ' [' + anim_file[var].units + ']'
                line = ax.plot([], [], color=LineColor)
                point = ax.plot([], [], color=PointColor, marker='o', markeredgecolor='r')
                lines.append([line])
                points.append([point])
                x.append(time)
                y.append([y1]) 
                ylabs.append(ylabel)
                xlabs.append(xlabel) 
                xlims.append([minx, maxx])
                ylims.append([miny, maxy])
                if i <len(VARLIST)-2:
                    ax.xaxis.set_tick_params(labelbottom=False)
                ax.set_xlim([minx, maxx])
                ax.set_ylim([miny, maxy])
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel) 
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=25)
        def animate(i):
            print(f'Animating frame {i}')
            for line, point, x1, y1 in zip(lines, points, x, y):
                for l in range(len(line)):
                    line[l][0].set_data(x1[:i], y1[l][:i])
                    point[l][0].set_data([x1[i]], [y1[l][i]])
        
        # In preview mode, render only the first frame to a PNG and skip the
        # full mp4 encode, so the layout can be checked before a long run.
        if preview:
            animate(0)
            preview_file = save_file.rsplit('.mp4', 1)[0] + '_frame0.png'
            fig.savefig(preview_file, dpi=dpi)
            print('Saving preview frame ' + preview_file)
            return

        anim = animation.FuncAnimation(fig, animate, frames=len(x[0]), blit = False) #,
        anim.save(save_file, fps=fps, dpi=dpi)
        print('Saving ' + save_file)

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

def process_animation(flight, render=True):
    print('*******************************************')
    print('******   Starting flight animation   ******')
    print('*******************************************')
    print('Using flight data file: ' + flight_data)

    if render:
        ani = SubplotAnimation()
    elif not os.path.exists(save_file):
        print('Cannot combine: ' + save_file + ' does not exist. '
              'Run without --combine-only first to create the frames.')
        return

    # Use ffmpeg to align the duration based on number of frames and frame rates
    # This will get the duration of the flight movie file and store as a variable
    Duration1 = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1',
         flight_movie_dir + flight_movie])
    Duration1 = float(Duration1)

    # This sets frame rate for the animation file and store as a variable
    Duration2 = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', save_file])
    Duration2 = float(Duration2)

    # Perform the calculation
    scalefactor = str(Duration1 / Duration2)

    # Extract the hieght from the camera image .mp4 for use in the creation of the animations
    height = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=height',
         '-of', 'csv=p=0:s=x', flight_movie_dir + flight_movie])
    height = height.rstrip().decode('utf-8')
    dims = width+height

    # The ffmpeg intermediates and the final combined mp4 all live alongside
    # save_file in output_dir. Build the mid_/final_ names from the basename
    # so the prefix is not prepended to the directory path.
    base = os.path.basename(save_file)
    mid_file = os.path.join(output_dir, 'mid_' + base)
    final_file = os.path.join(output_dir, 'final_' + base)
    output_file = os.path.join(output_dir, project + flight + '.mp4')

    # Update duration of the animation mp4 to align with flight movie
    subprocess.run(['ffmpeg', '-i', save_file,
                    '-filter:v', 'setpts=' + scalefactor + '*PTS',
                    mid_file], check=True)

    subprocess.run(['ffmpeg', '-i', mid_file, '-s', dims,
                    '-c:a', 'copy', final_file], check=True)

    subprocess.run(['ffmpeg', '-i', flight_movie_dir + flight_movie,
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
    return (math.floor(min_lat), math.ceil(max_lat)), (math.floor(min_lon), math.ceil(max_lon))

def create_time_slice(filename):
    # Parse the start time
    filename = filename.rsplit('.mp4', 1)[0]
    time_part = ''.join(filename.split('.', 1)[1:]) # This assumes the format is always as described
    
    # Step 2: Split the time part into start and end times
    start_time_str, end_time_str = time_part.split('_')
    start_time = datetime.strptime(start_time_str, '%y%m%d.%H%M%S')
    
    # Extract the date part from the start time
    start_date_str = start_time.strftime('%y%m%d')
    
    # Combine the start date with the end time's time part
    # Assuming end_time_str format is '%H:%M:%S' and needs to be combined with the start date
    end_time_full_str = f"{start_date_str}.{end_time_str}"
    
    # Parse the modified end time string
    end_time = datetime.strptime(end_time_full_str, '%y%m%d.%H%M%S')
    
    # Format the times as a slice
    time_slice = slice(start_time, end_time)
    
    return time_slice

def setup_flight_vars(flight):
    ##Setup the global variables for plotting and animation for each flight
    global flight_movie
    global flight_time
    global lats
    global lons
    global flight_data
    global anim_file
    global save_file

    # The TI3GER-2 data files drop the dash in their names (e.g. TI3GER2rf01.nc)
    # even though the project directory keeps it.
    file_project = project.replace('-', '') if project == 'TI3GER-2' else project
    flight_data = f"{dat}/{file_project}{flight}.nc"

    anim_file = xr.open_dataset(flight_data)
    # Write all generated files (animation, preview image, ffmpeg
    # intermediates, final combined mp4) to output_dir.
    save_file = os.path.join(output_dir, project + flight + 'animation.mp4')
    print("Finding movies in " + flight_movie_dir)
    flight_movie = None
    for file in os.listdir(flight_movie_dir):
        if fnmatch.fnmatch(file, '*' + flight + '*.mp4'):
            flight_movie = file
            lats, lons = get_flight_area(anim_file)
            flight_time=create_time_slice(file)
        else:
            pass
    if flight_movie is None:
        print("No .mp4 for flight " + flight + " found in " + flight_movie_dir)
        # TODO: Spawn off creation of movie if it doesn't exist but for now...
        #print("Generating movie...")
        exit(1)

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

def main():

    # Process command line arguments.
    args = parse_args()

    # Set variables that used to be imported from animation_config as global
    global project, flights, dat, flight_movie_dir, output_dir
    global VARLIST, dpi, fps, LineColor, LineColor2, PointColor, width

    # Check for required environment variables. Exit if not found.
    if 'DATA_DIR' not in os.environ:
        print('DATA_DIR environment variable not set.')
        exit(1)
    if 'RAW_DATA_DIR' not in os.environ:
        print('RAW_DATA_DIR environment variable not set.')
        exit(1)
    if 'PROJ_DIR' not in os.environ:
        print('PROJ_DIR environment variable not set.')
        exit(1)

    # Determine project
    project = config_loader.resolve_project(args.project)

    # Build the paths to the data directories based on the environment variables
    # - Build location of data
    dat = os.path.join(os.environ['DATA_DIR'], project)
    # - Define where the existing digital camera movies are located
    flight_movie_dir = os.path.join(os.environ['RAW_DATA_DIR'], project, "Movies/")
    # - Define where the output .mp4 files will be written
    output_dir = os.path.join(os.environ['RAW_DATA_DIR'], project, "Animations/")

    # Read the configuration file. On the first run for a project (no config in
    # $PROJ_DIR/<project>/<platform>/scripts), copy the template there and stop
    # so template can be configured for the project.
    config = config_loader.load(project)

    # Bind the per-project settings from the loaded config
    flights = config.flights
    VARLIST = config.VARLIST
    dpi = config.dpi
    fps = config.fps
    LineColor = config.LineColor
    LineColor2 = config.LineColor2
    PointColor = config.PointColor
    width = config.width

    # Perform checks to see if dirs are already present, make them if not
    dir_check(dat)
    dir_check(flight_movie_dir)
    dir_check(output_dir)

    for flight in flights:
        setup_flight_vars(flight)

        if args.preview:
            # Only create one frame then exit. Useful when determining if the
            # generated plots are correct.
            SubplotAnimation(preview=True)
            continue

        # Read in the movie file created from CombineCameras.pl
        if os.path.exists(flight_movie_dir + flight_movie):

            process_animation(flight, render=not args.combine_only)

        # If the movie file doesn't exist, then see if the user wants to make it.
        else:
            print('Could not find a camera images .mp4 file in: ' + flight_movie_dir + flight + '*')
            print('Please download the .mp4 file from https://data.eol.ucar.edu/')
            process = input('If you are at NCAR RAF and you would like to ' + \
                            'generate the camera images .mp4 file, press ' + \
                            'Enter. Anything else will not process.')

            if process == '':
                proj_path = os.path.join(os.environ["PROJ_DIR"], project)
                # The platform (e.g. GV_N677F) is the directory component that
                # sits under PROJ_DIR/project.
                platform = find_platform(proj_path)
                script = os.path.join(proj_path, platform, "scripts",
                                      "createMovies.sh")
                command = [script,'-p',project,flight]
                print(command)
                subprocess.run(command, check=True)

            elif process != '':
                print('Please download the desired .mp4 camera images file and start again.')
                exit(1)


if __name__ == '__main__':

    main()
