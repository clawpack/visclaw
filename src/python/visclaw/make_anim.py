"""
Make stand-alone animations similar to the movies in the plots directory.

First run `make plots` so that directory exists with png files for the
individual frames.

For illustration of other tools defined in the animation_tools module, 
see the notebook
  $CLAW/apps/notebooks/visclaw/animation_tools_demo.html
also visible in rendered form in the Clawpack gallery:
  http://www.clawpack.org/gallery/_static/apps/notebooks/visclaw/animation_tools_demo.html
  
"""

import matplotlib
matplotlib.use('Agg')
import os

from clawpack.visclaw import animation_tools

# file name prefix obtained from this directory name:
this_dir = os.path.split(os.getcwd())[-1]
file_name_prefix = this_dir + '_'

# Plots directory:  (first run `make plots`)
plotdir = '_plots'

# Search for all movie files in plotdir to determine what movies to make:
fignos = 'all'

# The type of outputs desired (from 'mp4', 'html', 'rst', the latter for use
# with Sphinx documentation (reStructured text):
outputs = ['html','rst','mp4']

# Size of figure:
figsize = (5,4)

# Dots per inch:
dpi = None

# Frames per second (for mp4 file only):
fps = 5

animation_tools.make_anim_outputs_from_plotdir(plotdir=plotdir, fignos=fignos,
        outputs=outputs, file_name_prefix=file_name_prefix,
        figsize=figsize, dpi=dpi, fps=fps)
