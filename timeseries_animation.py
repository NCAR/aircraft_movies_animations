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

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import animation as animation
from animation_config import project, flight, dat, flight_data, flight_movie_dir, output_dir, Var1, Var2, Var3, Var4, Var5, Var6, Var7a, Var7b, Var8, dpi, fps, LineColor, LineColor2, width
import netCDF4
from netCDF4 import Dataset
import cftime
#import nc_time_axis
import os
import fnmatch
import subprocess
import logging

# Read in the data file
anim_file = Dataset(flight_data)

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
        plt.rc("xtick", labelsize=7)
        plt.rc("ytick", labelsize=7)

        ax1 = fig.add_subplot(4, 2, 1)
        ax2 = fig.add_subplot(4, 2, 2)
        ax3 = fig.add_subplot(4, 2, 3)
        ax4 = fig.add_subplot(4, 2, 4)
        ax5 = fig.add_subplot(4, 2, 5)
        ax6 = fig.add_subplot(4, 2, 6)
        ax7 = fig.add_subplot(4, 2, 7)
        ax8 = fig.add_subplot(4, 2, 8)

        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=25)
        plt.setp(ax6.xaxis.get_majorticklabels(), rotation=25)

        print('Assigning .nc -32767 values to np.nan')

        self.y1 = np.asarray(anim_file[Var1])
        self.y1 = np.where(self.y1 == -32767, np.nan, self.y1)
        self.y1 = np.array(self.y1, dtype=float)
        self.y2 = np.asarray(anim_file[Var2])
       
        self.y2 = np.where(self.y2 == -32767, np.nan, self.y2)
        miny2 = np.nanmin(self.y2)
        maxy2 = np.nanmax(self.y2)

        self.y3 = np.asarray(anim_file[Var3])
        self.y3 = np.where(self.y3 == -32767, np.nan, self.y3)

        self.y4 = np.asarray(anim_file[Var4])
        self.y4 = np.where(self.y4 == -32767, np.nan, self.y4)

        self.y5 = np.asarray(anim_file[Var5])
        self.y5 = np.where(self.y5 == -32767, np.nan, self.y5)

        self.y6 = np.asarray(anim_file[Var6])
        self.y6 = np.where(self.y6 == -32767, np.nan, self.y6)

        self.y7a = np.asarray(anim_file[Var7a])
        self.y7a = np.where(self.y7a == -32767, np.nan, self.y7a)

        self.y7b = np.asarray(anim_file[Var7b])
        self.y7b = np.where(self.y7b == -32767, np.nan, self.y7b)

        self.y8 = np.asarray(anim_file[Var8])
        self.y8 = np.where(self.y8 == -32767, np.nan, self.y8)

        TIME = anim_file.variables['Time']
        convertedTime = netCDF4.num2date(TIME[:], TIME.units)
        self.t = np.asarray(anim_file['Time'])
        self.x = np.asarray(convertedTime)

        self.longitude = np.asarray(anim_file['GGLON'])
        self.longitude = np.array(self.longitude, dtype=float)
        self.latitude = np.asarray(anim_file['GGLAT'])
        self.latitude = np.array(self.latitude, dtype=float)

        self.longitude = np.where(self.longitude == -32767, np.nan, self.longitude)
        self.latitude = np.where(self.latitude == -32767, np.nan, self.latitude)

        ax1.set_xlabel('Time [Hour]')
        ax1.set_ylabel(Var1 + ' [' + anim_file[Var1].units + ']')
        self.line1 = Line2D([], [], color=LineColor)
        self.line1a = Line2D([], [], color="red", linewidth=2)
        self.line1e = Line2D([], [], color="red", marker='o', markeredgecolor='r')
        ax1.add_line(self.line1)
        ax1.add_line(self.line1a)
        ax1.add_line(self.line1e)
        #ax1.set_xlim(min(self.x), max(self.x))
        ax1.set_ylim(np.nanmin(self.y1), np.nanmax(self.y1))
        ax1.xaxis.set_visible(False)

        ax2.set_xlabel('Time [Hour]')
        ax2.set_ylabel(Var2 + ' [' + anim_file[Var2].units + ']')
        self.line2 = Line2D([], [], color=LineColor)
        self.line2a = Line2D([], [], color='red', linewidth=2)
        self.line2e = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax2.add_line(self.line2)
        ax2.add_line(self.line2a)
        ax2.add_line(self.line2e)
        #ax2.set_xlim(min(self.x), max(self.x))
        ax2.set_ylim(np.nanmin(self.y2), np.nanmax(self.y2))
        ax2.xaxis.set_visible(False)
        ax2.yaxis.set_label_position('right')

        ax3.set_xlabel('Time [Hour]')
        ax3.set_ylabel(Var3 + ' [' + anim_file[Var3].units + ']')
        self.line3 = Line2D([], [], color=LineColor)
        self.line3a = Line2D([], [], color='red', linewidth=2)
        self.line3e = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax3.add_line(self.line3)
        ax3.add_line(self.line3a)
        ax3.add_line(self.line3e)
        #ax3.set_xlim(min(self.x), max(self.x))
        ax3.set_ylim(np.nanmin(self.y3), np.nanmax(self.y3))
        ax3.xaxis.set_visible(False)

        ax4.set_xlabel('Time [Hour]')
        ax4.set_ylabel(Var4 + ' [' + anim_file[Var4].units + ']')
        self.line4 = Line2D([], [], color=LineColor)
        self.line4a = Line2D([], [], color='red', linewidth=2)
        self.line4e = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax4.add_line(self.line4)
        ax4.add_line(self.line4a)
        ax4.add_line(self.line4e)
        #ax4.set_xlim(min(self.x), max(self.x))
        ax4.set_ylim(np.nanmin(self.y4), np.nanmax(self.y4))
        ax4.yaxis.set_label_position('right')
        ax4.xaxis.set_visible(False)

        ax5.set_ylabel(Var5 + ' [' + anim_file[Var5].units + ']')
        self.line5 = Line2D([], [], color=LineColor)
        self.line5a = Line2D([], [], color='red', linewidth=1)
        self.line5e = Line2D([], [], color='red', marker="o", markeredgecolor="r")
        ax5.add_line(self.line5)
        ax5.add_line(self.line5a)
        ax5.add_line(self.line5e)
        #ax5.set_xlim(min(self.x), max(self.x))
        ax5.set_ylim(np.nanmin(self.y5), np.nanmax(self.y5))

        ax6.set_ylabel(Var6 + ' [' + anim_file[Var6].units + ']')
        self.line6 = Line2D([], [], color=LineColor)
        self.line6a = Line2D([], [], color='red', linewidth=1)
        self.line6e = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax6.add_line(self.line6)
        ax6.add_line(self.line6a)
        ax6.add_line(self.line6e)
        #ax6.set_xlim(min(self.x), max(self.x))
        ax6.set_ylim(np.nanmin(self.y6), np.nanmax(self.y6))
        ax6.yaxis.set_label_position('right')

        ax7.set_xlabel(Var7a + ' [' + anim_file[Var7a].units + ']')
        ax7.set_ylabel(Var8 + ' [' + anim_file[Var8].units + ']')
        self.line7a = Line2D([], [], color=LineColor)
        self.line7aa = Line2D([], [], color='red', linewidth=1)
        self.line7ae = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax7.add_line(self.line7a)
        ax7.add_line(self.line7aa)
        ax7.add_line(self.line7ae)
        #ax7.set_xlim(np.nanmin(self.y7a), np.nanmax(self.y7a))
        ax7.set_ylim(np.nanmin(self.y8), np.nanmax(self.y8))

        self.line7b = Line2D([], [], color=LineColor2)
        self.line7ba = Line2D([], [], color='red', linewidth=1)
        self.line7be = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax7.add_line(self.line7b)
        ax7.add_line(self.line7ba)
        ax7.add_line(self.line7be)

        ax8.set_xlabel('GGLON [' + anim_file['GGLON'].units + ']')
        ax8.set_ylabel('GGLAT [' + anim_file['GGLAT'].units + ']')
        self.line8 = Line2D([], [], color=LineColor)
        self.line8a = Line2D([], [], color='red', linewidth=1)
        self.line8e = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        ax8.add_line(self.line8)
        ax8.add_line(self.line8a)
        ax8.add_line(self.line8e)
        #ax8.set_xlim(min(self.longitude), max(self.longitude))
        ax8.set_ylim(min(self.latitude), max(self.latitude))
        ax8.yaxis.set_label_position('right')

        anim = animation.TimedAnimation.__init__(self, fig, blit=True)

    def _draw_frame(self, framedata):
        '''
        Draw the frame of the animation
        '''

        i = framedata
        head = i - 1
        head_slice = (self.t > self.t[i] - 1.0) & (self.t < self.t[i])
        print('Drawing frame: ' + str(i))

        self.line1.set_data(self.x[:i], self.y1[:i])
        self.line1a.set_data(self.x[head_slice], self.y1[head_slice])
        self.line1e.set_data(self.x[head], self.y1[head])

        self.line2.set_data(self.x[:i], self.y2[:i])
        self.line2a.set_data(self.x[head_slice], self.y2[head_slice])
        self.line2e.set_data(self.x[head], self.y2[head])

        self.line3.set_data(self.x[:i], self.y3[:i])
        self.line3a.set_data(self.x[head_slice], self.y3[head_slice])
        self.line3e.set_data(self.x[head], self.y3[head])

        self.line4.set_data(self.x[:i], self.y4[:i])
        self.line4a.set_data(self.x[head_slice], self.y4[head_slice])
        self.line4e.set_data(self.x[head], self.y4[head])

        self.line5.set_data(self.x[:i], self.y5[:i])
        self.line5a.set_data(self.x[head_slice], self.y5[head_slice])
        self.line5e.set_data(self.x[head], self.y5[head])

        self.line6.set_data(self.x[:i], self.y6[:i])
        self.line6a.set_data(self.x[head_slice], self.y6[head_slice])
        self.line6e.set_data(self.x[head], self.y6[head])

        self.line7a.set_data(self.y7a[:i], self.y8[:i])
        self.line7aa.set_data(self.y7a[head_slice], self.y8[head_slice])
        self.line7ae.set_data(self.y7a[head], self.y8[head])

        self.line7b.set_data(self.y7b[:i], self.y8[:i])
        self.line7ba.set_data(self.y7b[head_slice], self.y8[head_slice])
        self.line7be.set_data(self.y7b[head], self.y8[head])

        self.line8.set_data(self.longitude[:i], self.latitude[:i])
        self.line8a.set_data(self.longitude[head_slice], self.latitude[head_slice])
        self.line8e.set_data(self.longitude[head], self.latitude[head])

        self._drawn_artists = [self.line1, self.line1a, self.line1e,
                               self.line2, self.line2a, self.line2e,
                               self.line3, self.line3a, self.line3e,
                               self.line4, self.line4a, self.line4e,
                               self.line5, self.line5a, self.line5e,
                               self.line6, self.line6a, self.line6e,
                               self.line7a, self.line7aa, self.line7ae,
                               self.line7b, self.line7ba, self.line7be,
                               self.line8, self.line8a, self.line8e]

    def new_frame_seq(self):

        return iter(range(self.t.size))

    def _init_draw(self):

        lines = [self.line1, self.line1a, self.line1e,
                 self.line2, self.line2a, self.line2e,
                 self.line3, self.line3a, self.line3e,
                 self.line4, self.line4a, self.line4e,
                 self.line5, self.line5a, self.line5e,
                 self.line6, self.line6a, self.line6e,
                 self.line7a, self.line7aa, self.line7ae,
                 self.line7b, self.line7ba, self.line7be,
                 self.line8, self.line8a, self.line8e]

        for i in lines:
            i.set_data([], [])


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
    save_file = project + flight + 'animation.mp4'
    ani.save(save_file, fps=fps, dpi=dpi)
    print('Saving ' + save_file)

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
    height = height.rstrip()
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
        if fnmatch.fnmatch(file, '*' + flight + '*'):
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
