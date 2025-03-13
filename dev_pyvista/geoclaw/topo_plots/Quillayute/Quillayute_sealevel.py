"""
Plot a topo DEM warped by some warpfactor with an image specified by bg_file
drapped over it (or using a colormap based on elevation if bg_file == None).

An image can be downloaded using Quillayute_bg_image.py, or
you could take a screen shot of Google Earth, or use some other desired image.
"""

from pylab import *
import pyvista as pv
from clawpack.geoclaw import topotools
from clawpack.clawutil.data import get_remote_file
import os


global etamesh

make_snapshots = False  # True to capture a few frames, False for slider bar
make_html = False  # True to make html version of each snapshot (requires trame)

use_texture = False  # drape an image on the topo?  If False, color by elevation


# Load the topo DEM:

topo_fname = 'Quillayute_13s.asc'
if not os.path.isfile(topo_fname):
    # need to download it first...
    url = 'http://depts.washington.edu/clawpack/geoclaw/topo/WA/' + topo_fname
    get_remote_file(url, output_dir='.', file_name=topo_fname, verbose=True)

topo = topotools.Topography(topo_fname)

# Crop to the desired extent:
extent = [-124.66, -124.57, 47.9, 47.93]
topo = topo.crop(extent)

# matplotlib topo plot:
#topo.plot(limits=(-25,25))


if use_texture:
    # background image to use a texture on warped topo:
    bg_file ='Quillayute_img.jpg'

    if not os.path.isfile(bg_file):
        print('First run Quillayute_bg_image.py or provide other bg image file')
        print('Settting bg_file to None')
        bg_file = None

def round_and_print(camera_position):
    # round off entries in camera_position and print out, so user
    # can copy and paste into this script once good position is found:
    camera_position = list(camera_position)
    for i,a in enumerate(camera_position):
        b = []
        for j in range(len(a)):
            b.append(round(a[j],3))
        camera_position[i] = tuple(b)
    print('camera_position = ', camera_position)


camera_position =  [(4168.867, -7291.297, 5584.997), (3480.581, -2112.37, -4.258), (-0.032, 0.731, 0.681)]


z = array([0.])
x = (topo.x - topo.x[0]) * 111e3 * cos(topo.y.mean()*pi/180)
y = -(topo.y - topo.y[0]) * 111e3
print('xmax = %.1fm, ymax = %.1fm' % (x.max(),y.max()))
X,Y,Z = meshgrid(x, y, z, indexing='ij')
topoxyz = pv.StructuredGrid(X,Y,Z)

B = flipud(topo.Z)
if 0:
    Bmax = 200.  # truncate topo above this value (not needed here)
    B = minimum(B, Bmax)
topoxyz.point_data['B'] = B.flatten(order='C')

clim_B = (-100,100)  # colormap limits for topo (if not use_texture)

warpfactor = 3   # amplification of elevations

topowarp = topoxyz.warp_by_scalar('B', factor=warpfactor)


p = pv.Plotter(off_screen=make_snapshots)

if use_texture:
    # Add bg image as texture:
    bg_extent = extent
    texture = pv.read_texture(bg_file)

    x1,x2 = (asarray(bg_extent[:2]) - topo.x[0]) * 111e3 * cos(topo.y.mean()*pi/180)
    y1,y2 = (asarray(bg_extent[2:]) - topo.y[0]) * 111e3

    o = (x1, y1, 0.)
    u = (x2, y1, 0.)
    v = (x1, y2, 0.)

    mapped_surf = topowarp.texture_map_to_plane(o, u, v)
    p.add_mesh(mapped_surf,texture=texture)

else:
    p.add_mesh(topowarp,cmap='gist_earth',clim=clim_B)


sea_level = 0.
eta = where(B < sea_level, sea_level, nan)
topoxyz.point_data['eta'] = eta.flatten(order='C')
etawarp = topoxyz.warp_by_scalar('eta', factor=warpfactor)
etamesh = p.add_mesh(etawarp,color='c')



def set_sea_level(sea_level):
    global etamesh
    eta = where(B < sea_level, sea_level, nan)
    topoxyz.point_data['eta'] = eta.flatten(order='C')
    etawarp = topoxyz.warp_by_scalar('eta', factor=warpfactor)
    p.remove_actor(etamesh)
    etamesh = p.add_mesh(etawarp,color='c')

    if not make_snapshots:
        #round_and_print(camera_position)
        pass


if not make_snapshots:
    p.add_title('MHW after sea level rise / subsidence')
    p.add_slider_widget(set_sea_level, [-5,5], value=0, title='Sea Level',
                        pointa=(0.1,0.1), pointb=(0.4,0.1),)
    cpos = p.show(window_size=(2500,1500), cpos=camera_position, return_cpos=True)
    round_and_print(cpos)
else:
    p.window_size = (2500,1500)
    for slr in [0,1,2,3]:
        set_sea_level(slr)
        p.add_title('MHW after %i m subsidence (or sea level rise)' % slr)
        fname_png = 'Quillayute_mhw%im.png' % slr
        p.camera_position = camera_position
        p.screenshot(fname_png)
        print('Created ',fname_png)

        if make_html:
            fname_html = 'Quillayute_mhw%im.html' % slr
            p.export_html(fname_html)
            print('Created ',fname_html)
    p.close()
