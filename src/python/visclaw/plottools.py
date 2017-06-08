
"""
Module with some miscellaneous useful tools.
"""

from __future__ import absolute_import
def plotbox(xy, kwargs={'color':'b', 'linewidth':2}):
    """
    Add a box around a region to an existing plot.
    xy can be a list of [x1, x2, y1, y2] of the corners 
    or a string "x1 x2 y1 y2".
    """
    from pylab import plot
    if type(xy)==str:
        xy=xy.split()
    x1 = float(xy[0])
    x2 = float(xy[1])
    y1 = float(xy[2])
    y2 = float(xy[3])
    plot([x1,x2,x2,x1,x1],[y1,y1,y2,y2,y1],**kwargs)

