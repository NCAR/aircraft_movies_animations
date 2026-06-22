#! /usr/bin/env python3

#######################################################################
# Filesystem path helpers for timeseries_animation.py
#
# Kept free of matplotlib/cartopy/xarray dependencies so the logic can
# be unit tested in isolation.
#######################################################################

import os


def _prompt_for_platform(candidates):
    '''Ask the user to choose among multiple platform directories.

    Re-prompts until a valid selection number is entered.
    '''
    print("Multiple platform directories found:")
    for number, name in enumerate(candidates, start=1):
        print("  {}: {}".format(number, name))

    while True:
        choice = input("Select a platform by number: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(candidates):
                return candidates[index - 1]
        print("Please enter a number between 1 and {}.".format(len(candidates)))


def find_platform(proj_path):
    '''Return the platform directory that sits under PROJ_DIR/project.

    The platform (e.g. 'GV_N677F') is the sub-directory that contains a
    'scripts' directory, which is where createMovies.sh lives. Requiring
    the 'scripts' sub-directory ignores stray files and unrelated
    directories, so extra files or oddly named entries do not confuse the
    lookup.

    Exactly one candidate is the normal case. If more than one is found
    (which should not happen) the user is prompted to choose, rather than
    silently picking one. Raises FileNotFoundError if no platform directory
    is found (which includes proj_path not existing).
    '''
    try:
        entries = sorted(os.listdir(proj_path))
    except FileNotFoundError:
        raise FileNotFoundError(
            "Project directory does not exist: " + proj_path)

    candidates = [
        name for name in entries
        if os.path.isdir(os.path.join(proj_path, name, "scripts"))
    ]

    if not candidates:
        raise FileNotFoundError(
            "No platform directory (one containing a 'scripts' "
            "sub-directory) found in: " + proj_path)

    if len(candidates) == 1:
        return candidates[0]

    return _prompt_for_platform(candidates)
