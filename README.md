# Timeseries Animation

![Frame](https://github.com/tthomas88/timeseries_animation/blob/master/wecanexample.png)


### Summary

In order to create movies with animations, you must first have a digital camera movie (.mp4) for your desired project and flight. You can download any .mp4 you would like from the EOL Data Archive. Once you have downloaded your digital camera movie from the EOL Data Archive, you are ready to proceeed. If you do not already have the Low Rate netCDF flight data file, you can also download it from the EOL Data Archive. Now that you have the digital camera movie and netCDF, you are ready to configure the script to create and combine the set of animated plots. Download the code from this GitHub repo: [https://github.com/NCAR/aircraft_movies_animations]

timeseries_animation.py is a program that reads variables from a config file animation_config.py and uses them to create a set of animated timeseries sub-plots that are time-aligned and combined with a .mp4 file. The list of variables 'Var1' to 'Var8' are used to select variables from a supplied netCDF file for the given flight.

If you aren't sure which variables exist in the netCDF file that you have downloaded, you execute the following from a unix shell: ncdump -h file.nc | grep float. This will print a list of variables from the header of file.nc.

'Var1' to 'Var6' are plotted as time series while 'Var7' and 'Var8' are plotted as an animated scatter plot in the lower left of the frame. The plots are set to autoscale to the minimum and maximum value of the selected variable during the flight selected. 

The y-axis of each plot is labeled with the variable name and the units from the netCDF variable attribute 'units'. The line color in the timeseries animation can also be defined based on the input in the parameter file.

Once the animation is created, the program calls FFmpeg to set the duration and frame count using a corresponding digital camera movie located in the user defined 'flight_movie_dir'. Once the animation .mp4 and the digital camera movie .mp4 files have identical duration, the FFmpeg utility is called to combine the two .mp4 files into a single .mp4 file that has the camera images displayed the left and the timeseries animation displayed on the right, with time synchronized variables displayed as the aircraft images are updated.

The variables in the parameter file will need to be updated to reflect your project, flight, paths, and variables.
