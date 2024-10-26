"""
View time frames from GeoClaw output (the full AMR solution or selected levels).

First run this script with `make_animation = False` to open a pyvista window
with a slider bar to step through frames.  If you adjust the viewpoint and
then move the slider bar it will print out the new camera_position, which
could be copied into this script to have it open with that position in the
future (e.g. when making the animation).

Set `make_animation = True` to make a series of png files and then these
are combined into an mp4 file using clawpack.visclaw.animation_tools
(which requires ffmpeg).

Adjust warpfactor_eta and/or warpfactor_topo to change the vertical exaggeration
in the 3D plots.

Terminology:
    patch - an AMR patch from a GeoClaw solution at one time frame
    grid - gridxyz is a 3d numpy grid on which to define solution for plotting
    mesh - a pyvista plot actor created with pv.add_mesh
    
"""

from pylab import *
import os,sys,glob
import pyvista as pv
from clawpack.visclaw import colormaps
from clawpack.pyclaw.fileio.ascii import read_t
from clawpack.visclaw import animation_tools, colormaps
from clawpack.visclaw.geoplot import tsunami_colormap

# import dev_pyvista so that relative imports work:
CLAW = os.environ['CLAW']
VISCLAW = CLAW + '/visclaw'
sys.path.insert(0, VISCLAW)
import dev_pyvista
sys.path.pop(0)

from dev_pyvista.amrclaw import unpack_frame_patches # to unpack AMR patches
from dev_pyvista.geoclaw.util import time_str   # to convert time to HH:MM:SS

global mesh_list  # pv meshes created at one frame to remove at the next

# Things to set:
outdir = CLAW + '/geoclaw/examples/tsunami/chile2010/_output'

warpfactor_eta = 10   # vertical warp factor for eta
warpmax_eta = 0.5
warpmin_eta = -0.5

warpfactor_topo = warpfactor_eta
warpmax_topo = 0.3
warpmin_topo = -0.3
    

make_animation = False  # if False, will open on screen with slider for frameno

if make_animation:
    fname_base = 'pyvista_sample'
    fname_mp4 = fname_base + '.mp4'
    framedir = 'frame_plots'  # where to store png files
    os.system('mkdir -p %s' % framedir)

# plotting parameters (or explicitly modify the plotting commands below)
show_edges = True
clim_eta = (-0.2,0.2) # eta
#clim_topo = (-500,500)
clim_topo = clim_eta

# which frames to include:
if 1:
    # use all output files found:
    fortq_files = glob.glob(outdir + '/fort.q*')
    framenos = [int(f[-4:]) for f in fortq_files]
    framenos.sort()
    print('Setting framenos = ', framenos)
else:
    # set explicitly:
    framenos = range(0,3)


# which levels to plot (usually 1 to 10 will include all levels):
minlevel = 1
maxlevel = 3
print('Will show patches on levels %i to %i (with holes for finer patches)' \
        % (minlevel,maxlevel))

verbose = False  # True plots info about every patch as it's plotted
        
def make_gridxyz(X_edges, Y_edges, q):
    """
    Make gridxzy for a single patch,
        might want to change how this is done for GeoVista plots on sphere
    Set eta_wet and topo as the scalar value to plot (cell averages).
    If warping, also need to set point values at vertices.
    """
    
    z = array([0.])
    x = X_edges[:,0]
    y = Y_edges[0,:]
    X,Y,Z = meshgrid(x, y, z, indexing='ij')
    gridxyz = pv.StructuredGrid(X,Y,Z)
    
    # set value to plot:
    eta_wet = where(q[0,:,:] > 0.001, q[-1,:,:], nan)
    gridxyz.cell_data['eta'] = eta_wet.flatten(order='F')

    # topography can be computed as topo = eta - h (surface - depth)
    topo = q[-1,:,:] - q[0,:,:]
    gridxyz.cell_data['topo'] = topo.flatten(order='F')
    
    # warped surfaces:
    
    eta_point = unpack_frame_patches.extend_cells_to_points(eta_wet)
    eta_point = minimum(eta_point, warpmax_eta)  # limit big values near coast
    eta_point = maximum(eta_point, warpmin_eta)
    gridxyz.point_data['eta_point'] = eta_point.flatten(order='F')

    topo_point = unpack_frame_patches.extend_cells_to_points(topo)
    topo_point = minimum(topo_point, warpmax_topo)
    topo_point = maximum(topo_point, warpmin_topo)
    gridxyz.point_data['topo_point'] = topo_point.flatten(order='F')
        
    return gridxyz

def make_mesh_list(plotter, gridxyz, level, X_edges, Y_edges, q):
    """
    Use add_mesh to add one or more plots for a single patch and return a
    list of handle(s), since these meshes will have to be removed when
    plotting new frameno.
    """

    # warp surface based on eta (point_values needed):
    etawarp = gridxyz.warp_by_scalar('eta_point', factor=warpfactor_eta)
    etamesh = plotter.add_mesh(etawarp, cmap=tsunami_colormap,
                     clim=clim_eta,show_edges=show_edges)

    topowarp = gridxyz.warp_by_scalar('topo_point', factor=warpfactor_topo)
    topomesh = plotter.add_mesh(topowarp, color='lightgreen',
                                 show_edges=False)
                                 
    # this seems to affect color map of eta if clim_topo != clim_eta:
    #topomesh = plotter.add_mesh(topowarp, cmap='gist_earth',
    #                            clim=clim_topo, show_edges=False)

    return [topomesh,etamesh]
    
#----------------------
# Set up plotter:

# don't show plots on screen if making animation:
plotter = pv.Plotter(off_screen=make_animation)
plotter.window_size = (2000,1500)
plotter.add_axes()
mesh_list = []  # list of pyvista meshes to be removed for new frameno

plotter.camera_position =  [(-89.445, -139.758, 79.617), (-87.315, -31.325, -1.567), (-0.012, 0.599, 0.8)]

#---------------------------------------------------------------------------
# The rest of this may not need to change from one application to the next...

def set_frameno(frameno):
    """
    Make the plot for a single frame, looping over all AMR patches.
    Remove old meshes from plotter, and add new ones.
    """
    
    global mesh_list
    
    frameno = int(frameno)

    try:
        [time,num_eqn,nstates,num_aux,num_dim,num_ghost,file_format] = \
             read_t(frameno,outdir,file_prefix='fort')
    except:
        msg = '*** Could not read time from fort.t file in \n    %s' % outdir
        raise OSError(msg)

    plotter.add_title('Time %s, frame %i' % (time_str(time),frameno))
        
    try:
        # make an iterator for looping over all patches in this frame:
        patch_iterator = unpack_frame_patches.PatchIterator(frameno,
                                   outdir=outdir,
                                   file_format=file_format)
    except:
        print('Could not read frameno %s' % frameno)
        pass
    
    # a dictionary to keep track of all AMR patches at each level:
    patches_on_level = {}
    for k in range(1,maxlevel+2):
        patches_on_level[k] = []

    for level,patch_edges,q in patch_iterator:

        # process each AMR patch and put on lists by level

        if level < minlevel:
            # skip to next patch
            print('Skipping patch at level %i < minlevel' % level)
            continue

        if level > maxlevel+1:
            print('breaking since level = %i > maxlevel+1' % level)
            break

        X_edges,Y_edges = patch_edges[:2]
        bounds = [X_edges.min(), X_edges.max(),
                  Y_edges.min(), Y_edges.max(), -1, 1]

        gridxyz = make_gridxyz(X_edges,Y_edges,q)

        # append this patch to the set of patches to be plotted:
        patches_on_level[level].append([gridxyz, bounds])
    
    # remove old patches:
    for mesh in mesh_list:
        plotter.remove_actor(mesh)
    
    # now make plot and add_mesh for each of these patches:
    for k in range(1,maxlevel+1):
        if verbose:
            print('Now working on level %i with %i patches' \
                  % (k, len(patches_on_level[k])))

        for patch in patches_on_level[k]:
            gridxyz,bounds = patch
            if verbose: print('working on patch with bounds = ',bounds)

            # loop over next finer level to cut out its extent:
            if len(patches_on_level[k+1]) > 0:
                if verbose: print('clip from level %i' % (k+1))
                for clip_patch in patches_on_level[k+1]:
                    clip_bounds = clip_patch[1]
                    if verbose: print('clip with bounds = ',clip_bounds)
                    gridxyz = gridxyz.clip_box(clip_bounds)
                patch[0] = gridxyz

            # now that it's got proper holes cut out, make plot, add to plotter:
            patch_mesh_list = make_mesh_list(plotter, gridxyz, level,
                                                X_edges, Y_edges, q)
            for mesh in patch_mesh_list:
                # add mesh plots from this patch to list of all meshes for frame
                mesh_list.append(mesh)
                                 
    if not make_animation:

        # round off entries in p.camera_position and print out, so user
        # can copy and paste into this script once good position is found:
        camera_position = list(plotter.camera_position)
        for i,a in enumerate(camera_position):
            b = []
            for j in range(len(a)):
                b.append(round(a[j],3))
            camera_position[i] = tuple(b)
        print('plotter.camera_position = ',camera_position)


# Now either make a set of png files and combine into mp4 animation,
# or plot on screen with slider bar so plots can be viewed interactively:

if make_animation:
    # create png file for each frameno and the combine into animation:
    
    for frameno in framenos:
        set_frameno(frameno)
        fname_png = '%s/%s%s.png' % (framedir,fname_base,str(frameno).zfill(4))
        plotter.screenshot(fname_png)
        print('Created ',fname_png)

    plotter.close()

    fname_pattern='%s*.png' % fname_base
    anim = animation_tools.make_anim(framedir, fname_pattern=fname_pattern)
    animation_tools.make_mp4(anim, fname_mp4)

else:
    # create slider bar for user to adjust:
    frameno_limits = [framenos[0], framenos[-1]]
    plotter.add_slider_widget(set_frameno, frameno_limits, value=framenos[0],
                              title='frameno', fmt='%.1f',
                              pointa=(0.6,0.85), pointb=(0.9,0.85),
                              tube_width=0.01, slider_width=0.03)
    plotter.show()
    # Note: user must close window manually when done
    
