#! /usr/bin/python

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

# Provide project, flight, and location of data file
project = "SPICULE"
flight = "rf09"
dat = "/scr/raf_data/SPICULE/field_data/"
flight_data = "/scr/raf_data/SPICULE/field_data/SPICULErf09.nc"

# Define where the existing digital camera movies are located
flight_movie_dir = "/scr/raf_Raw_Data/SPICULE/Movies/"

# Define where you would like the output .mp4 to be written
output_dir = "/scr/raf_Raw_Data/SPICULE/Movies/animations/"

# Animation variable selection
Var1 = "GGALT"
Var2 = "CONC1DC_RWOO"
Var3 = "PSX"
Var4 = "WIC"
Var5 = "ATX"
Var6 = "CONCP_LWOI"
Var7 = "ATX"
Var8 = "GGALT"

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
width="450:"
