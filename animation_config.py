#! /usr/bin/env python3

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

# Provide project, flight, and location of data file
project = "ACES"
flight = "rf01"
dat = f"/scr/raf_data/{project}"
flight_data = f"{dat}/{project}{flight}.nc"

# Define where the existing digital camera movies are located
flight_movie_dir = f"/scr/raf/Raw_Data/{project}/Movies/"
flight_movie = "rf01.240408.160031_201559.mp4"
# Define where you would like the output .mp4 to be written
output_dir = "/h/eol/srunkel/aircraft_movies_animations/"

# Animation variable selection
Var1 = "GGALT"
Var2 = "ATX"
Var3 = "PSX"
Var4 = "ATX"
Var5 = "ATX"
Var6 = "ATX"
Var7a = "ATX"
Var7b = "DPXC"
Var8 = "GGALT"

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
LineColor2 = "red"
width="450:"
