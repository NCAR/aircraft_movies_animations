#! /usr/bin/python

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

# Provide project, flight, and location of data file
project = "TI3GER"
flight = "rf01"
dat = "/h/eol/taylort/aircraft_movies_animations/data_ti3ger/"
flight_data = "/h/eol/taylort/aircraft_movies_animations/data_ti3ger/TI3GERrf01.nc"

# Define where the existing digital camera movies are located
flight_movie_dir = "/h/eol/taylort/aircraft_movies_animations/movies_ti3ger/"

# Define where you would like the output .mp4 to be written
output_dir = "/h/eol/taylort/aircraft_movies_animations/"

# Animation variable selection
Var1 = "GGALT"
Var2 = "CONCU_FBTM"
Var3 = "PSX"
Var4 = "WIC"
Var5 = "ATX"
Var6 = "CONCD_LWOO"
Var7a = "ATX"
Var7b = "DPXC"
Var8 = "GGALT"

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
LineColor2 = "red"
width="450:"
