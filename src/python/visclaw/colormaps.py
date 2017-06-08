
"""
Module colormap for creating custom color maps.  For example...
  >>> from clawpack.visclaw import colormaps
  >>> mycmap = colormaps.make_colormap({0:'r', 1.:'b'})  # red to blue
  >>> colormaps.showcolors(mycmap)   # displays resulting colormap

Note that many colormaps are also defined in matplotlib and can be set by
  >>> from matplotlib import cm
  >>> mycmap = cm.get_cmap('Greens')
for example, to get colors ranging from white to green.
See matplotlib._cm for the data defining various maps.
"""

from __future__ import absolute_import
from __future__ import print_function
import numpy
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from six.moves import range

#-------------------------
def make_colormap(color_list):
#-------------------------
    """
    Define a new color map based on values specified in the dictionary
    colors, where colors[z] is the color that value z should be mapped to,
    with linear interpolation between the given values of z.

    The z values (dictionary keys) are real numbers and the values
    colors[z] can be either an RGB list, e.g. [1,0,0] for red, or an
    html hex string, e.g. "#ff0000" for red.

    Optionally, an alpha channel can be added to indicate levels of transparency.
    In this case, colors should have a fourth argument, a value between 0 and 1,
    where zero is transparent and 1 is opaque. Ex.

              blue_semi_transparent = [0.0, 0.0, 1.0, 0.5]

    """



    z = numpy.sort(list(color_list.keys()))
    n = len(z)
    z1 = min(z)
    zn = max(z)
    x0 = (z - z1) / (zn - z1)

    CC = colors.ColorConverter()
    R = []
    G = []
    B = []
    A = []
    for i in range(n):
        #i'th color at level z[i]:
        Ci = color_list[z[i]]
        if type(Ci) == str:
            # a hex string of form '#ff0000' for example (for red)
            RGBA = CC.to_rgba(Ci,1.0)
        else:
            # assume it's an RGB (or RGBA) tuple already:
            if (len(Ci) == 3):
                Ci = numpy.concatenate((Ci,[1.0]))  # Add alpha channel
            RGBA = Ci

        R.append(RGBA[0])
        G.append(RGBA[1])
        B.append(RGBA[2])
        A.append(RGBA[3])

    cmap_dict = {}
    cmap_dict['red'] = [(x0[i],R[i],R[i]) for i in range(len(R))]
    cmap_dict['green'] = [(x0[i],G[i],G[i]) for i in range(len(G))]
    cmap_dict['blue'] = [(x0[i],B[i],B[i]) for i in range(len(B))]
    cmap_dict['alpha'] = [(x0[i],A[i],A[i]) for i in range(len(A))]
    mymap = colors.LinearSegmentedColormap('mymap',cmap_dict)
    return mymap


def add_colormaps(colormaps, data_limits=[0.0,1.0], data_break=0.5, 
                             colormap_name="JohnDoe"):
    r"""Concatenate colormaps in *colormaps* list and return Normalize object.

    Appends the colormaps in the list *colormaps* adjusting the mapping to the
    colormap such that it maps the data space limits *data_limits* and puts the
    break in the colormaps at *data_break* which is again in data space.  The
    argument *colormap_name* labels the colormap and is passed to the init
    method of `matplotlib.colors.LinearSegmentedColormap`.

    Originally contributed by Damon McDougall

    returns `matplotlib.colors.LinearSegmentedColormap`, 
            `matplotlib.colors.Normalize`

    Example
    -------
    This example takes two colormaps whose data ranges from [-1.0, 5.0] where
    the break in the colormaps occurs at 1.0.

    >>> import matplotlib.pyplot as plt
    >>> import clawpack.visclaw.colormaps as colormaps
    >>> import numpy
    >>> cmaps = (plt.get_cmap("BuGn_r"), plt.get_cmap("Blues_r"))
    >>> new_cmap, norm = colormaps.add_colormaps(cmaps, data_limits=[-1.0, 5.0],
        data_break=1.0)
    >>> x = numpy.linspace(-1,1,100)
    >>> y = x
    >>> X, Y = numpy.meshgrid(x, y)
    >>> fig = plt.figure()
    >>> axes = fig.add_subplot(1,1,1)
    >>> plot = axes.pcolor(X, Y, 3.0 * X + 2.0, cmap=new_cmap, norm=norm)
    >>> fig.colorbar(plot)
    >>> plt.show()

    """

    lhs_dict = colormaps[0]._segmentdata
    rhs_dict = colormaps[1]._segmentdata
    new_dict = dict(red=[], green=[], blue=[], alpha=[])

    # Add first colorbar
    for key in rhs_dict:
        val_list = rhs_dict[key]
        for val in val_list:
            new_dict[key].append((val[0] * 0.5, val[1], val[2]))

    if 'alpha' not in list(rhs_dict.keys()):
        new_dict['alpha'].append((0.0,1.0,1.0))

    # Add second colorbar
    for key in lhs_dict:
        val_list = lhs_dict[key]
        for val in val_list:
            new_dict[key].append(((val[0] + 1.0) * 0.5, val[1], val[2]))

    if 'alpha' not in list(lhs_dict.keys()):
        new_dict['alpha'].append((1.0,1.0,1.0))

    N = 256
    gamma = 1.0

    cmap = colors.LinearSegmentedColormap(colormap_name, new_dict, N, gamma)

    # Compute new norm object
    bounds = numpy.empty(N)
    bounds[:int(N / 2)] = numpy.linspace(data_limits[0], data_break, int(N / 2))
    bounds[int(N / 2):] = numpy.linspace(data_break, data_limits[1], 
                                                             int(N / 2) + N % 2)
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=N)

    return cmap, norm


def showcolors(cmap):
    #from scitools.easyviz.matplotlib_ import colorbar, clf, axes, linspace,\
                 #pcolor, meshgrid, show, colormap
    plt.clf()
    x = numpy.linspace(0,1,21)
    X,Y = numpy.meshgrid(x,x)
    plt.pcolor(X,Y,0.5*(X+Y), cmap=cmap, edgecolors='k')
    plt.axis('equal')
    plt.colorbar()
    plt.title('Plot of x+y using colormap')


def schlieren_colormap(color=[0,0,0]):
    """
    For Schlieren plots:
    """
    if color=='k': color = [0,0,0]
    if color=='r': color = [1,0,0]
    if color=='b': color = [0,0,1]
    if color=='g': color = [0,0.5,0]
    color = numpy.array([1,1,1]) - numpy.array(color)
    s  = numpy.linspace(0,1,20)
    colors = {}
    for key in s:
        colors[key] = numpy.array([1,1,1]) - key**0.1 * color
    schlieren_colors = make_colormap(colors)
    return schlieren_colors


# -----------------------------------------------------------------
# Some useful colormaps follow...
# There are also many colormaps in matplotlib.cm

all_white = make_colormap({0.:'w', 1.:'w'})
all_light_red = make_colormap({0.:'#ffdddd', 1.:'#ffdddd'})
all_light_blue = make_colormap({0.:'#ddddff', 1.:'#ddddff'})
all_light_green = make_colormap({0.:'#ddffdd', 1.:'#ddffdd'})
all_light_yellow = make_colormap({0.:'#ffffdd', 1.:'#ffffdd'})

red_white_blue = make_colormap({0.:'r', 0.5:'w', 1.:'b'})
blue_white_red = make_colormap({0.:'b', 0.5:'w', 1.:'r'})
red_yellow_blue = make_colormap({0.:'r', 0.5:'#ffff00', 1.:'b'})
blue_yellow_red = make_colormap({0.:'b', 0.5:'#ffff00', 1.:'r'})
yellow_red_blue = make_colormap({0.:'#ffff00', 0.5:'r', 1.:'b'})
white_red = make_colormap({0.:'w', 1.:'r'})
white_blue = make_colormap({0.:'w', 1.:'b'})

schlieren_grays = schlieren_colormap('k')
schlieren_reds = schlieren_colormap('r')
schlieren_blues = schlieren_colormap('b')
schlieren_greens = schlieren_colormap('g')


#-------------------------------
def make_amrcolors(nlevels=4):
#-------------------------------
    """
    Make lists of colors useful for distinguishing different patches when
    plotting AMR results.

    INPUT::
       nlevels: maximum number of AMR levels expected.
    OUTPUT::
       (linecolors, bgcolors)
       linecolors = list of nlevels colors for patch lines, contour lines
       bgcolors = list of nlevels pale colors for patch background
    """

    # For 4 or less levels:
    linecolors = ['k', 'b', 'r', 'g']
    # Set bgcolors to white, then light shades of blue, red, green:
    bgcolors = ['#ffffff','#ddddff','#ffdddd','#ddffdd']
    # Set bgcolors to light shades of yellow, blue, red, green:
    #bgcolors = ['#ffffdd','#ddddff','#ffdddd','#ddffdd']

    if nlevels > 4:
        linecolors = 4*linecolors  # now has length 16
        bgcolors = 4*bgcolors
    if nlevels <= 16:
        linecolors = linecolors[:nlevels]
        bgcolors = bgcolors[:nlevels]
    else:
        print("*** Warning, suggest nlevels <= 16")

    return (linecolors, bgcolors)
