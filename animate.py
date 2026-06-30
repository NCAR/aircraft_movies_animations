#! /usr/bin/env python3

##############################################################################
# Animation set up
# Reads the variables listed in the configuration setup
# Builds the figure and drives the frame animation via animation.FuncAnimation
# (see plot())
# Plots are generated one plot per value in VARLIST
##############################################################################
from functools import partial
import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import animation as animation
from matplotlib.dates import DateFormatter
from layout import classify_entry, subplot_position, subplot_rows

def _create_subplot(fig, index, var, VARLIST, flight_vars):
    '''
    Create each per-variable sub-panel. Handles timeseries, var vs
    var and map
    '''
    kind = classify_entry(index, len(VARLIST), var)
    nrows, ncols, pos = subplot_position(index, len(VARLIST))
    if kind == 'map':
        ##add map for lat lon plots
        BORDERS2_10m = \
            cf.NaturalEarthFeature('cultural', 'admin_1_states_provinces',
                                   '50m', edgecolor='black',
                                   facecolor='none')
        # The last entry is always the lat/lon map: place it in the
        # bottom-right quadrant and let it fill the cell (the default
        # 'equal' aspect shrinks it to a narrow box).
        ax = fig.add_subplot(nrows, ncols, pos,
                             projection=ccrs.PlateCarree())

        ax.coastlines('50m')
        ax.add_feature(cf.OCEAN, facecolor='lightblue')
        ax.add_feature(cf.LAND, facecolor='beige')
        ax.add_feature(BORDERS2_10m, edgecolor='grey')
        ax.set_extent([flight_vars.lons[0], flight_vars.lons[1],
                       flight_vars.lats[0], flight_vars.lats[1]])
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

def _plot_var(anim_file, i, var, ax, cfg, lines, points, x, y):
    ''' A variable in VARLIST without parenthesis will plot vs time '''
    y1 = anim_file[var]
    time = pd.to_datetime(y1.Time.values)
    miny = np.nanmin(y1)
    maxy = np.nanmax(y1)
    minx = np.nanmin(time)
    maxx = np.nanmax(time)
    xlabel= 'Time [Hour]'
    ylabel= var + ' [' + anim_file[var].units + ']'
    line = ax.plot([], [], color=cfg.LineColor)
    point = ax.plot([], [], color=cfg.PointColor, marker='o',
                    markeredgecolor='r')
    lines.append([line])
    points.append([point])
    x.append(time)
    y.append([y1])
    if i <len(cfg.VARLIST)-2:
        ax.xaxis.set_tick_params(labelbottom=False)
    ax.set_xlim([minx, maxx])
    ax.set_ylim([miny, maxy])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

def _plot_tuple(anim_file, i, var, ax, cfg, lines, points, x, y):
    '''
    Variables within parenthesis are plotted on a single plot
      - (Var1, Var2) will plot Var1 on the X-axis and Var2 on the left Y-axis
      - (Var1, Var2, Var3) will plot Var1 on the X-axis, Var2 on the left
        Y-axis and Var3 on the right Y-axis
    '''
    x1 = anim_file[var[0]]
    y1 = anim_file[var[1]]
    minx = np.nanmin(x1)
    maxx = np.nanmax(x1)
    miny = np.nanmin(y1)
    maxy = np.nanmax(y1)
    xlabel= var[0] + ' [' + anim_file[var[0]].units + ']'
    point = ax.plot([], [], color=cfg.PointColor, marker='o',
                    markeredgecolor='r')
    line = ax.plot([], [], color=cfg.LineColor, label = var[1])
    if len(var)>2:
        y2 = anim_file[var[2]]
        # Make sure that the plot fits both lines
        miny = np.nanmin(y1) if np.nanmin(y1) < np.nanmin(y2) \
            else np.nanmin(y2)
        maxy = np.nanmax(y1) if np.nanmax(y1) > np.nanmax(y2) \
            else np.nanmax(y2)
        line2 = ax.plot([], [], color=cfg.LineColor2, linewidth=2,
                        label=var[2])
        point2 = ax.plot([], [], color=cfg.PointColor, marker='o',
                         markeredgecolor='r')
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
        if i != len(cfg.VARLIST):
            # Generic variable-vs-variable plot (not the lat/lon
            # map, whose extent is set by set_extent).
            ax.set_xlim([minx, maxx])
            ax.set_ylim([miny, maxy])
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)

    x.append(x1)

    sub_length = subplot_rows(len(cfg.VARLIST))
    if i <(sub_length+1):
        ax.xaxis.set_tick_params(labelbottom=False)

def _animate(i, lines, points, x, y):
    print(f'Animating frame {i}')
    for line, point, x1, y1 in zip(lines, points, x, y):
        for l in range(len(line)):
            line[l][0].set_data(x1[:i], y1[l][:i])
            point[l][0].set_data([x1[i]], [y1[l][i]])

def plot(flight_vars, cfg, preview=False):
    print('Creating figure subplots')
    fig = plt.figure(figsize=(8, 10))
    plt.rcParams.update({'font.size': 12})
    plt.rc("xtick", labelsize=10)
    plt.rc("ytick", labelsize=10)

    lines = []
    points = []
    x = []
    y = []

    # flight_time is only set when a matching camera movie was found. In
    # preview mode we may have none (the layout check doesn't need a movie),
    # so plot the whole flight rather than selecting on a None time slice,
    # which would raise KeyError: NaT.
    anim_file = xr.open_dataset(flight_vars.flight_data)
    if flight_vars.flight_time is not None:
        anim_file = anim_file.sel(Time=flight_vars.flight_time)

    for i, var in enumerate(cfg.VARLIST, start=1):
        #rotation = 25 if i in [5, 6] else None
        ax =_create_subplot(fig, i, var, cfg.VARLIST, flight_vars)
        # Newer matplotlib's tight_layout returns NaN axes positions once a
        # cartopy GeoAxes (the map) is in the figure, which later crashes
        # the draw with "cannot convert float NaN to integer". The map
        # always occupies a fixed grid cell (the last entry), so skip the
        # re-tighten for it; the earlier plain-axes passes have already
        # arranged the grid.
        if not hasattr(ax, 'projection'):
            fig.tight_layout()
        print("**************************************************")
        print(var)
        if isinstance(var, tuple):
            # Plot var vs var(s)
            _plot_tuple(anim_file, i, var, ax, cfg, lines, points, x, y)
        else:
            # plot var vs time
            _plot_var(anim_file, i, var, ax, cfg, lines, points, x, y)

        # The map (cartopy GeoAxes) draws its labels via the gridliner,
        # not standard axis ticks; rotating its major tick labels raises a
        # NaN error on newer matplotlib/cartopy, so only rotate plain axes.
        if not hasattr(ax, 'projection'):
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=25)

    # In preview mode, render only the first frame to a PNG and skip the
    # full mp4 encode, so the layout can be checked before a long run.
    if preview:
        _animate(0, lines=lines, points=points, x=x, y=y)
        preview_file = flight_vars.save_file.rsplit('.mp4', 1)[0] + \
                       '_frame0.png'
        fig.savefig(preview_file, dpi=cfg.dpi)
        print('Saving preview frame ' + preview_file)
        return

    anim = animation.FuncAnimation(fig, partial(_animate, lines=lines, points=points, x=x, y=y), frames=len(x[0]),
                                   blit = False) #,
    anim.save(flight_vars.save_file, fps=cfg.fps, dpi=cfg.dpi)
    print('Saving ' + flight_vars.save_file)

