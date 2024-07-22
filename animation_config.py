#! /usr/bin/env python3

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

# Provide project, flight, and location of data file
# Provide project, flight, and location of data file
project = "CAESAR"
flights = ["rf09","rf10"] ##must be a list even if only processing one flight
dat = f"/scr/raf_data/{project}"
#flight_data = f"{dat}/{project}{flight}.nc"

# Define where the existing digital camera movies are located
flight_movie_dir = f"/scr/raf/Raw_Data/{project}/Movies/"
##flight_movie = "rf01.240408.160031_201559.mp4" ## Currently, the flight movie is found by the timeseries_animation.py script, but could be set here
# Define where you would like the output .mp4 to be written
output_dir = "/h/eol/srunkel/aircraft_movies_animations/"

# Animation variable selection
Var1 = "GGALT"
Var2 = "PSX"
Var3 = "WIC"
Var4 = "PLWCC" 
Var5 = "CONCS_2DS"
Var6 = "CONCD_LWI"
Var7 = "FO3C_ACD"
Var7a = "ATX"
Var7b = "DPXC"

VARLIST = [Var1,Var2, Var7a, Var7b,  Var3,Var4, Var5, Var6,Var7, (Var1,Var7a, Var7b), ('GGLON', 'GGLAT')]

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
LineColor2 = "red"
PointColor = "red"
width="400:"

