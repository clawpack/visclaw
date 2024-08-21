"""
Download a satellite image or map to use as a background image or
texture (for warped PyVista meshes).

Adapted from:
  https://makersportal.com/blog/2020/4/24/geographic-visualizations-in-python-with-cartopy
"""


import sys
if 'matplotlib' not in sys.modules:
    import matplotlib
    matplotlib.use('Agg')  # Use an image backend

import matplotlib.pyplot as plt 
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import io
from urllib.request import urlopen, Request
from PIL import Image

def image_spoof(self, tile): # this function pretends not to be a Python script
    url = self._image_url(tile) # get the url of the street map API
    req = Request(url) # start request
    req.add_header('User-agent','Anaconda 3') # add user agent to request
    fh = urlopen(req) 
    im_data = io.BytesIO(fh.read()) # get image
    fh.close() # close url
    img = Image.open(im_data) # open image with PIL
    img = img.convert(self.desired_tile_form) # set image format
    return img, self.tileextent(tile), 'lower' # reformat for cartopy

def fetch_img(extent, fname, source='QuadtreeTiles', scale=None,
                    figsize=None):
    """
    :Input:
        - extent: [x1,x2,y1,y2]
        - fname: image file to save ('.jpg' or '.png' file typically)
        - source: Any source supported by cartopy.io.img_tiles, including
                  'QuadtreeTiles', 'OSM', 'GoogleTiles'
        - scale: resolution of file downloaded, see below
                 if None, value computed based on extent but may need adjustment
        - figsize: if None, will be calculated based on aspect ratio of extent
    
    See https://scitools.org.uk/cartopy/docs/v0.16/cartopy/io/img_tiles.html
    for possible source specifications.

    scale specifications should be selected based on extent:
    -- 2     = coarse image, select for worldwide or continental scales
    -- 4-6   = medium coarseness, select for countries and larger states
    -- 6-10  = medium fineness, select for smaller states, regions, and cities
    -- 10-12 = fine image, select for city boundaries and zip codes
    -- 14+   = extremely fine image, select for roads, blocks, buildings
    """
    
    x1,x2,y1,y2 = extent
    dx = x2-x1
    dy = y2-y1
    maxdxdy = max(dx,dy)
    
    dxm = dx*111e3*np.cos(np.pi*0.5*(y1+y2)/180)
    dym = dy*111e3
    maxdxdym = max(dxm,dym)
    print('max(dx,dy) = %.5f degrees (approx %.2f m)' % (maxdxdy,maxdxdym))
    
    if scale is None:
        # try something reasonable, then user should adjust...
        if maxdxdy < 0.1:
            scale = 16
        elif maxdxdy < 2.1:
            scale = 12
        elif maxdxdy < 5.1:
            scale = 10
        else:
            scale = 4
    else:
        scale = int(scale)
        scale = min(scale, 19)
        scale = max(scale, 2)
    
    print('Using scale = %i, for finer resolution try larger values up to 19' \
            % scale)
    print('  (finer resolution may take longer to download and plot)')
    
    if figsize is None:
        x_inches = 8*dxm/maxdxdym
        y_inches = 8*dym/maxdxdym
        figsize = (x_inches, y_inches)
        print('Using figsize = ', figsize)
    else:
        x_inches, y_inches = figsize
        
    img_fetcher = getattr(cimgt,source)
    img_fetcher.get_image = image_spoof
    img = img_fetcher()

    # plot image with some padding
    fig = plt.figure(figsize=figsize) # open matplotlib figure
    ax1 = plt.axes(projection=img.crs) # use proper coordinate reference system
    
    fig.set_size_inches(x_inches,y_inches)
    ax1.set_frame_on(False)
    plt.margins(0,0)
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
                    hspace = 0, wspace = 0)

    eps = 0.01  # padding so jpg file saved better matches extent
    extent = [x1+eps*dx, x2-eps*dx, y1+eps*dy, y2-eps*dy]

    ax1.set_extent(extent) # set extents
    ax1.add_image(img, int(scale)) # add OSM with zoom specification

    # save image with no border (still not quite the right extent):
    plt.savefig(fname,bbox_inches='tight')
    print('Created ', fname)
    print('extent = ',extent)
