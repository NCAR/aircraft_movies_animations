#! /usr/bin/env python3

########################################################################
# Script to create animations of selected variables from a given
# project and flight
# Duration is determined based on duration of the already created mp4
# Separate .mp4 files are combined using ffmpeg to create final data
# Product with movie and animation.
#
# Copyright (2022) University Corporation for Atmospheric Research
#
# Author: TMT
#######################################################################

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation as animation
from animation_config_local import FLIGHT_TIME, project, flight, dat, flight_data, flight_movie_dir, output_dir, VARLIST, LATS, LONS, dpi, fps, LineColor, LineColor2, width,PointColor
import xarray as xr
import os
import fnmatch
import subprocess
import pandas as pd
import logging
import cartopy.feature as cf
import cartopy.crs as ccrs


BORDERS2_10m = cf.NaturalEarthFeature('cultural', 'admin_1_states_provinces',
                                                '50m', edgecolor='black', facecolor='none')

# Read in the data file
anim_file = xr.open_dataset(flight_data)
save_file = project + flight + 'animation.mp4'
print('*******************************************')
print('******   Starting flight animation   ******')
print('*******************************************')
print('Using flight data file: ' + flight_data)


class SubplotAnimation(animation.TimedAnimation):
    '''
    Animation set up
    Reads the variables listed in the configuration setup
    '''

    def __init__(self):

        print('Creating figure subplots')
        fig = plt.figure(figsize=(8, 10))
        plt.rcParams.update({'font.size': 12})
        plt.rc("xtick", labelsize=10)
        plt.rc("ytick", labelsize=10)
        anim_file = xr.open_dataset(flight_data).sel(Time = FLIGHT_TIME)

        ##add map for lat lon plots

        BORDERS2_10m = cf.NaturalEarthFeature('cultural', 'admin_1_states_provinces',
                                                        '50m', edgecolor='black', facecolor='none')

        # Your latitude and longitude data
        sub_length = math.ceil(len(VARLIST) / 2)
        axes = []
        lines = []
        x = []
        y = []
        xlims = []
        ylims = []
        xlabs = []
        ylabs = []
        points = []
        def create_subplot(fig, index):
            if index == len(VARLIST):  
                ax = fig.add_subplot(sub_length, 1, sub_length,projection=ccrs.PlateCarree())
                
                ax.coastlines('50m')
                ax.add_feature(cf.OCEAN, facecolor='lightblue')
                ax.add_feature(cf.LAND, facecolor='beige')
                ax.add_feature(BORDERS2_10m, edgecolor='grey')
                ax.set_extent([ LONS[0], LONS[1],LATS[0], LATS[1],])
            else:
                ax = fig.add_subplot(sub_length, 2, index)
                ax.grid(color='grey', linestyle='--', linewidth=0.5)
            
            return ax
        for i, var in enumerate(VARLIST, start=1):
            #rotation = 25 if i in [5, 6] else None
            ax = create_subplot(fig, i)
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
                line = ax.plot([], [], color=LineColor)
                point = ax.plot([], [], color=PointColor, marker='4', markeredgecolor='r')
                if len(var)>2:
                    y2 = anim_file[var[2]]
                    miny = np.nanmin(y1) if np.nanmin(y1) < np.nanmin(y2) else np.nanmin(y2) ##Make sure that the plot fits both lines
                    maxy = np.nanmax(y1) if np.nanmax(y1) > np.nanmax(y2) else np.nanmax(y2) ##Make sure that the plot fits both lines
                    line2 = ax.plot([], [], color=LineColor2, linewidth=2) 
                    point = ax.plot([], [], color=PointColor, marker='o', markeredgecolor='r')
                    point2 = ax.plot([], [], color=PointColor, marker='o', markeredgecolor='r') 
                    ylabel=var[1] + ' '+var[2] +' [' + anim_file[var[1]].units + ']'
                    y.append((y1,y2)) 
                    lines.append([line, line2])
                    points.append([point, point2])
                    ax.set_xlim([minx, maxx])
                    ax.set_ylim([miny, maxy])
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel) 
                else:
                    ylabel=var[1] + ' [' + anim_file[var[1]].units + ']'
                    y.append([y1]) 
                    lines.append([line])
                    points.append([point])
                
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
                if i <len(VARLIST)-1:
                    ax.xaxis.set_tick_params(labelbottom=False)
                ax.set_xlim([minx, maxx])
                ax.set_ylim([miny, maxy])
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel) 
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=25)
        def animate(i):
            print(f'Animating frame {i}')
            for line, point, x1,y1 in zip(lines,points,x, y):
                for l in range(len(line)):
                    line[l][0].set_data(x1[:i], y1[l][:i])
                    point[l][0].set_data(x1[i], y1[l][i])
        
        anim = animation.FuncAnimation(fig, animate, frames = len(x[0]) , blit = False) #,
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


def process_animation():

    ani = SubplotAnimation()
    

    # Use ffmpeg to align the duration based on number of frames and frame rates
    # This will get the duration of the flight movie file and store as a variable
    Duration1 = subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ' + flight_movie_dir + flight_movie, shell=True)
    Duration1 = float(Duration1)

    # This sets frame rate for the animation file and store as a variable
    Duration2 = subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ' + save_file, shell=True)
    Duration2 = float(Duration2)

    # Perform the calculation
    scalefactor = str(Duration1 / Duration2)

    # Extract the hieght from the camera image .mp4 for use in the creation of the animations
    height = subprocess.check_output("ffprobe -v error -show_entries stream=height -of csv=p=0:s=x " + flight_movie_dir + flight_movie, shell=True)
    height = height.rstrip().decode('utf-8')
    dims = width+height

    # Update duration of the animation mp4 to align with flight movie
    command = 'ffmpeg -i ' + save_file + ' -filter:v setpts=' + scalefactor + '*PTS mid_' + save_file
    os.system(command)

    command = 'ffmpeg -i mid_' + save_file + ' -s ' + dims + ' -c:a copy final_' + save_file
    os.system(command)

    command = 'ffmpeg -i ' + flight_movie_dir + flight_movie + ' -i final_' + save_file + ' -filter_complex hstack,format=yuv420p -c:v libx264 -crf 18 ' + output_dir + project + flight + '.mp4'
    os.system(command)

    command = 'rm mid_' + save_file
    os.system(command)

    command = 'rm final_' + save_file
    os.system(command)


def main():

    # Perform checks to see if dirs are already present, make them if not
    dir_check(dat)
    dir_check(flight_movie_dir)
    dir_check(output_dir)

    for file in os.listdir(flight_movie_dir):
        if fnmatch.fnmatch(file, '*' + flight + '*.mp4'):
            global flight_movie
            flight_movie = file

        else:
            pass
    # Read in the movie file created from CombineCameras.pl
    if os.path.exists(flight_movie_dir + flight_movie):

        process_animation()

    # If the movie file doesn't exist, then see if the user wants to make it.
    else:
        print('Could not find a camera images .mp4 file in: ' + flight_movie_dir + flight + '*')
        print('Please download the .mp4 file from https://data.eol.ucar.edu/')
        process = input('If you are at NCAR RAF and you would like to generate the camera images .mp4 file, press Enter. Anything else will not process.')

        if process == '':
            command = ('/net/work/bin/converters/createMovies/combineCameras.pl /net/jlocal/projects/SOCRATES/GV_N677F/scripts/' + project + '.paramfile ' + flight)
            os.system(command)
            print(command)

        elif process != '':
            print('Please download the desired .mp4 camera images file and start again.')
            exit(1)


if __name__ == '__main__':

    main()
