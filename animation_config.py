#! /usr/bin/env python3

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

import os

# Provide project, flight
project = "CAESAR"
flights = ["rf09","rf10"] ##must be a list even if only processing one flight

# Uncomment and edit one of the following types of plots
# Example animation variable selection with two vars in one plot
#Var1 = "GGALT"
#Var2 = "PSX"
#Var3 = "WIC"
#Var4 = "PLWCC"
#Var5 = "CONCS_2DS"
#Var6 = "CONCD_LWI"
#Var7 = "FO3C_ACD"
#Var7a = "ATX"
#Var7b = "DPXC"
#VARLIST = [Var1,Var2,Var7a,Var7b,Var3,Var4,Var5,Var6,Var7,(Var1,Var7a, Var7b),('GGLON', 'GGLAT')]

# Example animation variable selection with two vars plotted against each other
#Var1 = "GGALT"
#Var2 = "DPXC"
#Var3 = "PSX"
#Var4 = "WIC"
#Var5 = "ATX"
#Var6 = "CONCD_RWO"
#Var7 = "ATX"
#VARLIST = [Var1,Var2,Var3,Var4,Var5,Var6,(Var1,Var7), ('GGLON', 'GGLAT')]

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
LineColor2 = "red"
PointColor = "red"
width="400:"

