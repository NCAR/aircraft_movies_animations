#! /usr/bin/env python3

#######################################################################
# Pure layout helpers for timeseries_animation.py
#
# These functions decide, for a given VARLIST, how each entry maps onto
# the subplot grid and how it should be plotted. They are kept free of
# matplotlib/cartopy/data dependencies so the placement logic can be
# unit tested in isolation.
#######################################################################

import math


def subplot_rows(n_vars):
    '''Number of rows in the (rows x 2) subplot grid for n_vars entries.'''
    return math.ceil(n_vars / 2)


def classify_entry(index, n_vars, var):
    '''Classify a 1-based VARLIST entry.

    'map'  -> the trailing lat/lon map (always the last entry)
    'pair' -> a tuple entry plotted as one variable against another
    'time' -> a plain variable plotted against time
    '''
    if index == n_vars:
        return 'map'
    if isinstance(var, tuple):
        return 'pair'
    return 'time'


def subplot_position(index, n_vars):
    '''Grid placement (nrows, ncols, pos) for a 1-based VARLIST entry.

    The map (last entry) always occupies the bottom-right cell; every
    other entry keeps its natural position in the 2-column grid.
    '''
    rows = subplot_rows(n_vars)
    if index == n_vars:
        return rows, 2, 2 * rows
    return rows, 2, index
