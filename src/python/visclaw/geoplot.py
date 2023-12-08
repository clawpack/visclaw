"""
Useful things for plotting GeoClaw results.
"""

import numpy
import warnings

from clawpack.visclaw import colormaps

# Colormaps from geoclaw
# Color attributes, single instance per run
# Colors
black = [0.0,0.0,0.0]
white = [1.0,1.0,1.0]
green = [0.0,1.0,0.0];
dark_green = [0.1,0.4,0.0];
light_green = [0.8,1.0,0.5];
dark_blue = [0.2,0.2,0.7];
light_blue = [0.5,0.5,1.0];
blue = [0.0,0.0,1.0];
blue_green = [0.0,1.0,1.0]
red = [1.0,0.0,0.0]
tan = [0.9,0.8,0.2];
tan = [0.8,0.5,0.2];
brown = [0.9,0.8,0.2];
gray8 = [0.8,0.8,0.8];

transparent = [0.0, 0.0, 0.0,0.0]
blue_a = [0.0,0.0,1.0,1.0];
red_a = [1.0,0.0,0.0,1.0]
light_green_a = [0.0,1.0,1.0,1.0];
white_a = [1.0,1.0,1.0,1.0]

#Colors taken from Google Earth
biscay = '#203469'   # Dark blue
lightblue = '#4E6498'


# Colormaps
TSUNAMI_MAX_AMPLITUDE = 0.6
googleearth_lightblue = colormaps.make_colormap({-TSUNAMI_MAX_AMPLITUDE:blue_a,
                                                 0.0:lightblue,
                                                 TSUNAMI_MAX_AMPLITUDE:red_a})

googleearth_darkblue = colormaps.make_colormap({-TSUNAMI_MAX_AMPLITUDE:blue_a,
                                                0.0:biscay,
                                                TSUNAMI_MAX_AMPLITUDE:red_a})


googleearth_white = colormaps.make_colormap({-TSUNAMI_MAX_AMPLITUDE:blue_a,
                                                0.0:white_a,
                                                TSUNAMI_MAX_AMPLITUDE:red_a})


googleearth_transparent = colormaps.make_colormap({-1.0:light_green_a,
                                                   0.0:transparent,
                                                   1.0:red_a})

# Start transparency at 0.2
googleearth_flooding = colormaps.make_colormap({ -1:transparent,
                                                 -0.2:light_blue,
                                                 1.0:dark_blue})


tsunami_colormap = colormaps.make_colormap({-TSUNAMI_MAX_AMPLITUDE:blue,
                                            0.0:blue_green,
                                            TSUNAMI_MAX_AMPLITUDE:red})

land1_colormap = colormaps.make_colormap({0.0:dark_green,
                                          1000.0:green,
                                          2000.0:light_green,
                                          4000.0:tan})

land2_colormap = colormaps.make_colormap({0:dark_green,
                                          50:green,
                                          100:light_green,
                                          200:tan})

water_land_colormap = colormaps.make_colormap({-1000:dark_blue,
                                               -500:blue,
                                               0:light_blue,
                                               .1:tan,
                                               5:tan,
                                               6:dark_green,
                                               1000:green,
                                               2000:light_green,
                                               4000:tan})

bathy1_colormap = colormaps.make_colormap({-1000:brown,
                                           0:tan,
                                           .1:dark_green,
                                           1000:green,
                                           2000:light_green})

bathy2_colormap = colormaps.make_colormap({-1000:brown,
                                           -100:tan,
                                           0:dark_green,
                                           .1:dark_green,
                                           1000:green,
                                           2000:light_green})

bathy3_colormap = colormaps.make_colormap({-1:[0.3,0.2,0.1],
                                           -0.01:[0.95,0.9,0.7],
                                           .01:[.5,.7,0],
                                           1:[.2,.5,.2]})

seafloor_colormap = colormaps.make_colormap({-1:[0.3,0.2,0.1],
                                              0:[0.95,0.9,0.7]})

land_colormap = colormaps.make_colormap({ 0:[0.95,0.9,0.7],
                                          1:[.2,.5,.2]})



colormaps_list = {"tsunami":tsunami_colormap,"land1":land1_colormap,
             "land2":land2_colormap,"water_land":water_land_colormap,
                  "bathy1":bathy1_colormap,"bathy2":bathy2_colormap}

def plot_colormaps():
    r"""Plots all colormaps avaiable or the ones specified"""

    import numpy as np
    import matplotlib.pyplot as plt

    a = np.linspace(0, 1, 256).reshape(1,-1)
    a = np.vstack((a,a))

    nmaps = len(colormaps_list) + 1

    fig = plt.figure(figsize=(5,10))
    fig.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)

    for i,name in enumerate(colormaps_list):
        ax = plt.subplot(nmaps,1,i+1)
        plt.axis("off")
        plt.imshow(a, aspect='auto', cmap=colormaps_list[name], origin='lower')
        pos = list(ax.get_position().bounds)
        fig.text(pos[0] - 0.01, pos[1], name, fontsize=10, horizontalalignment='right')

    #plt.show()

land_colors = colormaps.make_colormap({0:[.5,.7,0], 1:[.2,.5,.2]})
# water_colors = colormaps.make_colormap({-1.:'r', 0.:[0, .8, .8], 1.: 'b'})
# land_colors = land2_colormap
water_colors = tsunami_colormap

# Plotting functions

# The drytol parameter is used in masking land and water and
# affects what color map is used for cells with small water depth h.
# The best value to use often depends on the application and can
# be set for an application by setting current_data.user['dry_tolerance'] in
# a beforeframe function, for example.  If it's not set by the user,
# the following default value is used (in meters):

drytol_default = 1.e-3

def topo(current_data):
   """
   Return topography = eta - h.
   Surface eta is assumed to be output as 4th column of fort.q files.
   """
   q = current_data.q
   h = q[0,...]
   eta = q[-1,...]
   topo = eta - h
   return topo


def land(current_data):
   """
   Return a masked array containing the surface elevation only in dry cells.
   """
   drytol = current_data.user.get('dry_tolerance', drytol_default)
   q = current_data.q
   h = q[0,...]
   eta = q[-1,...]
   land = numpy.ma.masked_where(h>drytol, eta)
   return land


def water(current_data):
   """Deprecated: use surface instead."""
   raise DeprecationWarning("Deprecated function, use surface instead.")
   drytol = current_data.user.get('dry_tolerance', drytol_default)
   q = current_data.q
   h = q[0,...]
   eta = q[-1,...]
   water = numpy.ma.masked_where(h<=drytol, eta)
   return water


def depth(current_data):
   """
   Return a masked array containing the depth of fluid only in wet cells.
   """
   drytol = current_data.user.get('dry_tolerance', drytol_default)
   q = current_data.q
   h = q[0,...]
   depth = numpy.ma.masked_where(h<=drytol, h)
   try:
       # Use mask covering coarse regions if it's set:
       m = current_data.mask_coarse
       depth = numpy.ma.masked_where(m, depth)
   except:
       pass

   return depth


def surface(current_data):
    """
    Return a masked array containing the surface elevation only in wet cells.
    Surface is eta = h+topo, assumed to be output as 4th column of fort.q
    files.
    """
    drytol = current_data.user.get('dry_tolerance', drytol_default)
    q = current_data.q
    h = q[0,...]
    eta = q[-1,...]

    water = numpy.ma.masked_where(h <= drytol,eta)

    try:
        # Use mask covering coarse regions if it's set:
        m = current_data.mask_coarse
        water = numpy.ma.masked_where(m, water)
    except:
        pass

    return water


def surface_or_depth(current_data):
    """
    Return a masked array containing the surface elevation where the topo is
    below sea level or the water depth where the topo is above sea level.
    Mask out dry cells.  Assumes sea level is at topo=0.
    Surface is eta = h+topo, assumed to be output as 4th column of fort.q
    files.
    """

    drytol = current_data.user.get('dry_tolerance', drytol_default)
    q = current_data.q
    h = q[0,...]
    eta = q[-1,...]
    topo = eta - h

    # With this version, the land was plotted as white in png files for KML.
    # surface = ma.masked_where(h <= drytol, eta)
    # depth = ma.masked_where(h <= drytol, h)
    # surface_or_depth = where(topo<0, surface, depth)

    # With this version, the land is transparent.
    surface_or_depth = numpy.ma.masked_where(h <= drytol,
                                             numpy.where(topo<0, eta, h))

    try:
        # Use mask covering coarse regions if it's set:
        m = current_data.mask_coarse
        surface_or_depth = numpy.ma.masked_where(m, surface_or_depth)
    except:
        pass

    return surface_or_depth


def u_velocity(current_data):
    """
    Return a masked array containing the u velocity (x-component)
    Mask out dry cells.  
    """

    drytol = current_data.user.get('dry_tolerance', drytol_default)
    q = current_data.q
    h = q[0,...]
    hu = q[1,...]
    h_wet = numpy.ma.masked_where(h<=drytol, h)
    u_wet = hu / h_wet

    try:
        # Use mask covering coarse regions if it's set:
        m = current_data.mask_coarse
        u_wet = numpy.ma.masked_where(m, u_wet)
    except:
        pass

    return u_wet


def v_velocity(current_data):
    """
    Return a masked array containing the v velocity (y-component)
    Mask out dry cells.  
    """

    drytol = current_data.user.get('dry_tolerance', drytol_default)
    q = current_data.q
    h = q[0,...]
    hv = q[2,...]
    h_wet = numpy.ma.masked_where(h<=drytol, h)
    v_wet = hv / h_wet

    try:
        # Use mask covering coarse regions if it's set:
        m = current_data.mask_coarse
        v_wet = numpy.ma.masked_where(m, v_wet)
    except:
        pass

    return v_wet

def speed(current_data):
    """
    Return a masked array containing the speed.
    Mask out dry cells.  
    """

    drytol = current_data.user.get('dry_tolerance', drytol_default)
    q = current_data.q
    h = q[0,...]
    hu = q[1,...]
    hv = q[2,...]
    h_wet = numpy.ma.masked_where(h<=drytol, h)
    u_wet = hu / h_wet
    v_wet = hv / h_wet
    speed = numpy.sqrt(u_wet**2 + v_wet**2)

    try:
        # Use mask covering coarse regions if it's set:
        m = current_data.mask_coarse
        speed = numpy.ma.masked_where(m, speed)
    except:
        pass

    return speed



def kml_build_colorbar(cb_filename, cmap, cmin, cmax):

    """
    This version is deprecated, please use 
        clawpack.geoclaw.kmltools.kml_build_colorbar
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import warnings

    msg = "geoplot.kml_build_colorbar is deprecated, " \
        + "instead use clawpack.geoclaw.kmltools.kml_build_colorbar"
    warnings.warn(msg)

    fig = plt.figure(figsize=(0.8,3))
    ax1 = fig.add_axes([0.1, 0.075, 0.25, 0.85])
    tick = ax1.yaxis.get_major_ticks()
    plt.tick_params(axis='y', which='major', labelsize=8)

    norm = mpl.colors.Normalize(vmin=cmin,vmax=cmax)

    cb1 = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,
                                    norm=norm,
                                    orientation='vertical')
    # This is called from plotpages, in <plotdir>.
    plt.savefig(cb_filename,Transparent=True)


# Some discrete color maps useful for contourf plots of fgmax results:

def discrete_cmap_1(clines):
    """
    Construct a discrete color map for the regions between the contour lines
    given in clines. Colors go from turqouise through yellow to red.
    Good for zeta.
    """
    from numpy import floor, linspace, hstack, ones, zeros
    nlines = len(clines)
    n1 = int(floor((nlines-1)/2.))
    n2 = nlines - 1 - n1
    Green = hstack([linspace(1,1,n1),linspace(1,0,n2)])
    Red = hstack([linspace(0,0.8,n1), ones(n2)])
    Blue = hstack([linspace(1,0.2,n1), zeros(n2)])
    colors = list(zip(Red,Green,Blue))
    return colors

def discrete_cmap_2(clines):
    """
    Construct a discrete color map for the regions between the contour lines
    given in clines.  Colors go from red to turquoise.
    Good for arrival times.
    """
    from numpy import floor, linspace, hstack, ones, zeros, flipud
    nlines = len(clines)
    n1 = int(floor((nlines-1)/2.))
    n2 = nlines - 1 - n1
    Green = flipud(hstack([linspace(1,1,n1),linspace(1,0,n2)]))
    Red = flipud(hstack([linspace(0,0.8,n1), ones(n2)]))
    Blue = flipud(hstack([linspace(1,0.2,n1), zeros(n2)]))
    colors = list(zip(Red,Green,Blue))
    return colors
