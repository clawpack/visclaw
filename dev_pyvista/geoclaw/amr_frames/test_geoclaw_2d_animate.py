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

from dev_pyvista.amrclaw import unpack_frame_2d # to unpack grid patches
from dev_pyvista.geoclaw.util import time_str   # to convert time to HH:MM:SS

global mesh_list

# Things to set:
outdir = CLAW + '/geoclaw/examples/tsunami/chile2010/_output'
warpfactor = 10 # warp vertically based on q[0], set to None for flat 2d plots
#warpfactor = None

# set desired camera position:
if warpfactor is None:
    camera_position =  'xy'
else:
    camera_position = [(-69.658, -33.882, 197.263), (-90.0, -30.0, 0.0), (0.009, 1.0, 0.019)]

make_animation = False  # if False, will open on screen with slider for frameno

if make_animation:
    fname_base = 'pyvista_sample'
    fname_mp4 = fname_base + '.mp4'
    framedir = 'frame_plots'  # where to store png files
    os.system('mkdir -p %s' % framedir)

# plotting parameters (or explicitly modify the plotting commands below)
show_edges = True
clim = (-0.2,0.2)

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
maxlevel = 10
print('Will show grids on levels %i to %i (with holes for finer grids)' \
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

    # topography can be computed as eta - h (surface - depth)
    topo = q[-1,:,:] - q[0,:,:]
    #topo = where(q[0,:,:] > 0.01, nan, topo)
    gridxyz.cell_data['topo'] = topo.flatten(order='F')
    
    if warpfactor is not None:
        # water surface eta:
        eta_point = unpack_frame_2d.extend_cells_to_points(eta_wet)
        eta_point = minimum(eta_point, 0.5)  # limit big values near coast
        gridxyz.point_data['eta_point'] = eta_point.flatten(order='F')

        # topography can be computed as eta - h (surface - depth)
        #topo = q[-1,:,:] - q[0,:,:]
        topo_point = unpack_frame_2d.extend_cells_to_points(topo)

        # mask topo where we want to plot eta:
        topo_point = where(isnan(eta_point), topo_point, nan)
        gridxyz.point_data['topo_point'] = topo_point.flatten(order='F')
        
    return gridxyz

def make_grid_mesh_list(plotter, gridxyz, level, X_edges, Y_edges, q):
    """
    Use add_mesh to add one or more plots for a single patch and return a
    list of handle(s), since these meshes will have to be removed when
    plotting new frameno.
    """

    if warpfactor is None:
        # flat 2d plot:
        topomesh = plotter.add_mesh(gridxyz, scalars='topo', color='g')
        etamesh = plotter.add_mesh(gridxyz, scalars='eta', cmap=tsunami_colormap,
                         clim=clim,show_edges=show_edges)

    else:
        # warp surface based on eta (point_values needed):
        etawarp = gridxyz.warp_by_scalar('eta_point', factor=warpfactor)
        etamesh = plotter.add_mesh(etawarp, cmap=tsunami_colormap,
                         clim=clim,show_edges=show_edges)

        # add warp of topo scaled down so it's nearly flat:
        topowarp = gridxyz.warp_by_scalar('topo_point', factor=1e-5)

        #plotter.add_mesh(topowarp, cmap='gist_earth',
        #                 clim=(-500e-5,3000e-5),show_edges=False)

        #plotter.add_mesh(gridxyz, scalars='topo', color='g',show_edges=False)
                         
        # this works ok to make it solid green:
        topomesh = plotter.add_mesh(topowarp, color='g')
                                                   
    return [topomesh,etamesh]
    
#----------------------
# Set up plotter:

# don't show plots on screen if making animation:
plotter = pv.Plotter(off_screen=make_animation)
plotter.window_size = (1500,1500)
plotter.add_axes()
mesh_list = []  # list of pyvista meshes to be removed for new frameno

plotter.camera_position = camera_position


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
        patch_iterator = unpack_frame_2d.PatchIterator(frameno,
                                   outdir=outdir,
                                   file_format=file_format)
    except:
        print('Could not read frameno %s' % frameno)
        pass
    
    # a dictionary to keep track of all grid patches at each level:
    patches_on_level = {}
    for k in range(1,maxlevel+2):
        patches_on_level[k] = []

    for level,X_edges,Y_edges,q in patch_iterator:

        # process each grid patch and put on lists by level

        if level < minlevel:
            # skip to next patch
            print('Skipping patch at level %i < minlevel' % level)
            continue

        if level > maxlevel+1:
            print('breaking since level = %i > maxlevel+1' % level)
            break

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
            gridmesh_list = make_grid_mesh_list(plotter, gridxyz, level,
                                                X_edges, Y_edges, q)
            for gridmesh in gridmesh_list:
                mesh_list.append(gridmesh)
                                 
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
    
