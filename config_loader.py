#! /usr/bin/env python3

#######################################################################
# Resolve the project and load (or seed) its per-project
# animation_config.py.
#######################################################################

import importlib.util
import os
import shutil
import sys

from paths import find_platform

# The config template shipped with the checkout. It is seeded into a
# project's scripts dir on first use and is never edited per project.
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "animation_config.py")

def resolve_project(arg_project):
    '''
    Return the project name from the --project argument, falling back to
    the $PROJECT environment variable. Exit with a clear message if neither
    is set.

    project is required *before* any config is read (it locates the
    per-project config), so it cannot come from the config itself.

    If we are running in realtime mode on the groundstation where $PROJECT
    is set, use that: no --project arg required but no harm if it's set
    '''
    project = arg_project or os.environ.get("PROJECT")
    if not project:
        print("No project set. Pass --project <name> or set $PROJECT.")
        sys.exit(1)
    return project

def config_path_for(project):
    '''Return the full path to the per-project animation_config.py:
    $PROJ_DIR/<project>/<platform>/scripts/animation_config.py.'''
    proj_path = os.path.join(os.environ["PROJ_DIR"], project)
    platform = find_platform(proj_path)
    return os.path.join(proj_path, platform, "scripts", "animation_config.py")

def _import_from_path(path):
    '''
    Import animation_config from it's project-specific location. This mimics
    using "import animation_config.py" for a local file, but works for a file
    in any location. Since import searches sys.path, we would have to add the
    proj dir to our path to use import, so instead do this.
    animation_config is just a label - set to the filename by convention, but
    it doesn't have to be.
    '''
    # Build a spec: the import system's recipe for the module. It bundles
    # the module name and, crucially, a loader that knows how to read and
    # run the file at `path`.
    spec = importlib.util.spec_from_file_location("animation_config", path)
    # Create an empty module object from that recipe (no code run yet).
    module = importlib.util.module_from_spec(spec)
    # Execute the file's code to populate the module (defines flights,
    # VARLIST, dpi, etc.).
    spec.loader.exec_module(module)
    return module

def _set_project(config_path, project):
    '''
    Fill the project name into a freshly seeded config so the copy names
    the project it belongs to. The running code still takes project from
    --project/$PROJECT (it must, to locate this file at all); this value is
    documentation, not the source of truth. The template's <project> entry
    is rewritten in place; if no such value exists the file is left unchanged.
    '''

    with open(config_path) as file:
        text = file.read()
    text = text.replace("<project>", project)
    with open(config_path, "w") as file:
        file.write(text)

def load(project):
    ''' Load configuration from animation_config.py

    The first time this is is run for a project (no config in the scripts dir)
    copy the template from the code checkout there, ask user to edit it and
    stop with exit code 0 (no error, action needed).
    '''

    config_path = config_path_for(project)
    if not os.path.exists(config_path):
        shutil.copy(TEMPLATE_PATH, config_path)
        _set_project(config_path, project)
        print("Template config copied to " + config_path)
        print("Edit it for " + project + ", then rerun")
        sys.exit(0)
    return _import_from_path(config_path)

