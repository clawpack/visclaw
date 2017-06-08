"""
Useful things for plotting GeoClaw results.
"""

from __future__ import absolute_import
from __future__ import print_function
import numpy
import warnings

from clawpack.visclaw import colormaps
from matplotlib.colors import Normalize
from clawpack.geoclaw import topotools
from six.moves import range


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
# be set for an application by setting current_data.user.drytol in
# a beforeframe function, for example.  If it's not set by the user,
# the following default value is used (in meters):

drytol_default = 1.e-3

def topo(current_data):
   """
   Return topography = eta - h.
   Surface eta is assumed to be output as 4th column of fort.q files.
   """
   q = current_data.q
   h = q[0,:,:]
   eta = q[3,:,:]
   topo = eta - h
   return topo


def land(current_data):
   """
   Return a masked array containing the surface elevation only in dry cells.
   """
   drytol = getattr(current_data.user, 'drytol', drytol_default)
   q = current_data.q
   h = q[0,:,:]
   eta = q[3,:,:]
   land = numpy.ma.masked_where(h>drytol, eta)
   return land


def water(current_data):
   """Deprecated: use surface instead."""
   raise DeprecationWarning("Deprecated function, use surface instead.")
   drytol = getattr(current_data.user, 'drytol', drytol_default)
   q = current_data.q
   h = q[0,:,:]
   eta = q[3,:,:]
   water = numpy.ma.masked_where(h<=drytol, eta)
   return water


def depth(current_data):
   """
   Return a masked array containing the depth of fluid only in wet cells.
   """
   drytol = getattr(current_data.user, 'drytol', drytol_default)
   q = current_data.q
   h = q[0,:,:]
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
    drytol = getattr(current_data.user, 'drytol', drytol_default)
    q = current_data.q
    h = q[0,:,:]
    eta = q[3,:,:]

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

    drytol = getattr(current_data.user, 'drytol', drytol_default)
    q = current_data.q
    h = q[0,:,:]
    eta = q[3,:,:]
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


class TopoPlotData(object):

    def __init__(self, fname):
        deprecation_msg = "This object is being deprecated in favor of the " + \
                          "Topography class in clawpack.geoclaw.topotools."
        warnings.filterwarnings('default', category=DeprecationWarning)
        warnings.warn(deprecation_msg, DeprecationWarning, stacklevel=2)
        warnings.resetwarnings()
        self.fname = fname
        self.topotype = 3
        self.neg_cmap = None
        self.pos_cmap = None
        self.cmap = None
        self.cmax = 100.
        self.cmin = -4000.
        self.climits = None
        self.figno = 200
        self.addcolorbar = False
        self.addcontour = False
        self.contour_levels = [0, 0]
        self.xlimits = None
        self.ylimits = None
        self.coarsen = 1
        self.imshow = True
        self.gridedges_show = True
        self.print_fname = True

    def plot(self):
        plot_topo_file(self)


def plot_topo_file(topoplotdata):
    """
    Read in a topo or bathy file and produce a pcolor map.
    """

    deprecation_msg = "This function is being deprecated in favor of the " + \
                      "Topography class in clawpack.geoclaw.topotools and " + \
                      "plotting tools associated with it."
    warnings.filterwarnings('default', category=DeprecationWarning)
    warnings.warn(deprecation_msg, DeprecationWarning, stacklevel=2)
    warnings.resetwarnings()

    import os
    import pylab
    from clawpack.clawutil.data import ClawData

    fname = topoplotdata.fname
    topotype = topoplotdata.topotype
    if topoplotdata.climits:
        # deprecated option
        cmin = topoplotdata.climits[0]
        cmax = topoplotdata.climits[1]
    else:
        cmin = topoplotdata.cmin
        cmax = topoplotdata.cmax
    figno = topoplotdata.figno
    addcolorbar = topoplotdata.addcolorbar
    addcontour = topoplotdata.addcontour
    contour_levels = topoplotdata.contour_levels
    xlimits = topoplotdata.xlimits
    ylimits = topoplotdata.ylimits
    coarsen = topoplotdata.coarsen
    imshow = topoplotdata.imshow
    gridedges_show = topoplotdata.gridedges_show
    neg_cmap = topoplotdata.neg_cmap
    pos_cmap = topoplotdata.pos_cmap
    cmap = topoplotdata.cmap
    print_fname = topoplotdata.print_fname


    if neg_cmap is None:
        neg_cmap = colormaps.make_colormap({cmin:[0.3,0.2,0.1],
                                                0:[0.95,0.9,0.7]})
    if pos_cmap is None:
        pos_cmap = colormaps.make_colormap({    0:[.5,.7,0],
                                        cmax:[.2,.5,.2]})
    if cmap is None:
        cmap = colormaps.make_colormap({-1:[0.3,0.2,0.1],
                                           -0.00001:[0.95,0.9,0.7],
                                           0.00001:[.5,.7,0],
                                           1:[.2,.5,.2]})
        #cmap = colormaps.make_colormap({-1:[0,0,1],0:[1,1,1],1:[1,0,0]})

    if abs(topotype) == 1:

        X,Y,topo = topotools.topofile2griddata(fname, topotype)
        topo = pylab.flipud(topo)
        Y = pylab.flipud(Y)
        x = X[0,:]
        y = Y[:,0]
        xllcorner = x[0]
        yllcorner = y[0]
        cellsize = x[1]-x[0]


    elif abs(topotype) == 3:

        file = open(fname, 'r')
        lines = file.readlines()
        ncols = int(lines[0].split()[0])
        nrows = int(lines[1].split()[0])
        xllcorner = float(lines[2].split()[0])
        yllcorner = float(lines[3].split()[0])
        cellsize = float(lines[4].split()[0])
        NODATA_value = int(lines[5].split()[0])

        print("Loading file ",fname)
        print("   nrows = %i, ncols = %i" % (nrows,ncols))
        topo = pylab.loadtxt(fname,skiprows=6,dtype=float)
        print("   Done loading")

        if 0:
            topo = []
            for i in range(nrows):
                topo.append(pylab.array(lines[6+i],))
            print('+++ topo = ',topo)
            topo = pylab.array(topo)

        topo = pylab.flipud(topo)

        x = pylab.linspace(xllcorner, xllcorner+ncols*cellsize, ncols)
        y = pylab.linspace(yllcorner, yllcorner+nrows*cellsize, nrows)
        print("Shape of x, y, topo: ", x.shape, y.shape, topo.shape)

    else:
        raise Exception("*** Only topotypes 1 and 3 supported so far")


    if coarsen > 1:
        topo = topo[slice(0,nrows,coarsen), slice(0,ncols,coarsen)]
        x = x[slice(0,ncols,coarsen)]
        y = y[slice(0,nrows,coarsen)]
        print("Shapes after coarsening: ", x.shape, y.shape, topo.shape)


    if topotype < 0:
        topo = -topo

    if figno:
        pylab.figure(figno)

    if topoplotdata.imshow:
            color_norm = Normalize(cmin,cmax,clip=True)
            xylimits = (x[0],x[-1],y[0],y[-1])
            #pylab.imshow(pylab.flipud(topo.T), extent=xylimits, \
            pylab.imshow(pylab.flipud(topo), extent=xylimits, \
                    cmap=cmap, interpolation='nearest', \
                    norm=color_norm)
            #pylab.clim([cmin,cmax])
            if addcolorbar:
                pylab.colorbar()
    else:
        neg_topo = ma.masked_where(topo>0., topo)
        all_masked = (ma.count(neg_topo) == 0)
        if not all_masked:
            pylab.pcolormesh(x,y,neg_topo,cmap=neg_cmap)
            pylab.clim([cmin,0])
            if addcolorbar:
                pylab.colorbar()

        pos_topo = ma.masked_where(topo<0., topo)
        all_masked = (ma.count(pos_topo) == 0)
        if not all_masked:
            pylab.pcolormesh(x,y,pos_topo,cmap=pos_cmap)
            pylab.clim([0,cmax])
    if addcolorbar:
        pylab.colorbar()

    pylab.axis('scaled')


    if addcontour:
        pylab.contour(x,y,topo,levels=contour_levels,colors='k')

    patchedges_show = True
    if patchedges_show:
        pylab.plot([x[0],x[-1]],[y[0],y[0]],'k')
        pylab.plot([x[0],x[-1]],[y[-1],y[-1]],'k')
        pylab.plot([x[0],x[0]],[y[0],y[-1]],'k')
        pylab.plot([x[-1],x[-1]],[y[0],y[-1]],'k')

    if print_fname:
        fname2 = os.path.splitext(fname)[0]
        pylab.text(xllcorner+cellsize, yllcorner+cellsize, fname2, color='m')

    topodata = ClawData()
    topodata.x = x
    topodata.y = y
    topodata.topo = topo

    return topodata


def kml_build_colorbar(cb_filename, cmap, cmin, cmax):

    import matplotlib.pyplot as plt
    import matplotlib as mpl

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
