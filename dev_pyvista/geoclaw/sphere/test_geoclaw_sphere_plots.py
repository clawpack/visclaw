"""
Sample plot functions for AMR frames of a GeoClaw solution.
This code creates the plot on the sphere using GeoVista, see
        https://geovista.readthedocs.io/en/latest/
"""

from pylab import *
import os,sys

CLAW = os.environ['CLAW']
DEVLIB = CLAW + '/visclaw/dev_pyvista/amrclaw/2d'
sys.path.insert(0, DEVLIB)
import unpack_frame_2d  # should be in DEVLIB
from importlib import reload
reload(unpack_frame_2d)
sys.path.pop(0)



def geoclaw_matplotlib_plot(frameno, minlevel=1, maxlevel=10,
                      outdir='_output',verbose=True):
    """
    Make a simple matplotlib plot with finer grids plotted on top
    of coarser ones.  This is the way visclaw normally makes plots.

    For exploration and debugging purposes, plot grids only from level minlevel
    up to level maxlevel (or finest level present).
    """

    from clawpack.visclaw.geoplot import tsunami_colormap
    #from clawpack.pyclaw.fileio.ascii import read_t

    if outdir == 'chile2010':
        # shorthand for this standard example:
        outdir = CLAW + '/geoclaw/examples/tsunami/chile2010/_output'
    
    figure(1)
    clf()
        
    patch_iterator = unpack_frame_2d.PatchIterator(frameno, outdir=outdir,
                                                   verbose=verbose)
    for level,X,Y,q in patch_iterator:

        if level < minlevel:
            # skip to next patch
            print('Skipping patch at level %i < minlevel' % level)
            continue

        if level > maxlevel:
            print('Not showing patches with level > %i' % maxlevel)
            break

        extent = [X.min(), X.max(), Y.min(), Y.max()]
        if verbose:
            print('    extent = ',extent)
        eta_wet = where(q[0,:,:] > 0.001, q[-1,:,:], nan)
        pcolormesh(X,Y,eta_wet,cmap=tsunami_colormap, edgecolors='k')
        clim(-0.2, 0.2)
    title('Standard matplotlib plot')
    colorbar()
    show()


def geoclaw_sphere_pv_clip(frameno, minlevel = 1, maxlevel=10, outdir='_output',
                    warpfactor=None, verbose=True):

    """
    Plot grids from level minlevel up to level maxlevel (or finest level).
    On each level, holes are first cut out for all grids at higher levels.
    If warpfactor is not None, warp grid by surface elevation.
    
    This code creates the plot on the sphere using GeoVista, see
        https://geovista.readthedocs.io/en/latest/
    """

    import pyvista as pv
    import geovista as gv

    from clawpack.visclaw.geoplot import tsunami_colormap
    from clawpack.pyclaw.fileio.ascii import read_t

    if outdir == 'chile2010':
        # shorthand for this standard example:
        outdir = CLAW + '/geoclaw/examples/tsunami/chile2010/_output'
        
    try:
        [time,num_eqn,nstates,num_aux,num_dim,num_ghost,file_format] = \
             read_t(frameno,outdir,file_prefix='fort')
    except:
        msg = '*** Could not read time from fort.t file in \n    %s' % outdir
        raise OSError(msg)


    print('Will show grids up to level %i (with holes for finer grids)' \
            % maxlevel)

    pv.global_theme.allow_empty_mesh = True


    # make an iterator for looping over all patches in this frame:
    patch_iterator = unpack_frame_2d.PatchIterator(frameno, outdir=outdir,
                                   file_format=file_format)

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

        x = X_edges[:,0]
        y = Y_edges[0,:]

        #z = array([0.])
        #X,Y,Z = meshgrid(x, y, z, indexing='ij')
        #gridxyz = pv.StructuredGrid(X,Y,Z)
        

        # set value to plot:
        eta_wet = where(q[0,:,:] > 0.001, q[-1,:,:], nan)
        gridxyz = gv.Transform.from_1d(x,y,eta_wet.T)
    
        #xx = vstack((x[:-1],x[1:])).T
        #yy = vstack((y[:-1],y[1:])).T
        #gridxyz = gv.Transform.from_1d(xx,yy,eta_wet.T)
        

        #import pdb; pdb.set_trace()
        gridxyz.cell_data['eta'] = eta_wet.flatten(order='F')

        # topography can be computed as eta - h (surface - depth)
        topo = q[-1,:,:] - q[0,:,:]
        gridxyz.cell_data['topo'] = topo.flatten(order='F')
        
        # this reduces size of gridxyz based on nans in eta_wet
        gridxyz = gridxyz.threshold()  # remove nan values

        # append this patch to the set of patches to be plotted:
        patches_on_level[level].append([gridxyz, bounds])

    # now construct plotter:

    #plotter = pv.Plotter()
    plotter = gv.GeoPlotter()
    plotter.add_base_layer(texture=gv.blue_marble())
    plotter.add_coastlines()
    plotter.add_axes()

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

            # now that it's got proper holes cut out, add to plotter:

            plotter.add_mesh(gridxyz, scalars='eta', cmap=tsunami_colormap,
                             clim=(-0.2,0.2),show_edges=True)
            #plotter.add_mesh(gridxyz, scalars='topo', color='g')
            
            #plotter.add_mesh(gridxyz, cmap=tsunami_colormap,
            #                 clim=(-0.2,0.2),show_edges=True)

            if verbose: print(' adding to plotter')

    plotter.camera_position = 'xz'
    plotter.add_title('Time %.1f seconds' % time)
    plotter.show(window_size=(1500,1500))

if __name__ == '__main__':
    
    # Note: You first need to run the code in 
    #     $CLAW/geoclaw/examples/tsunami/chile2010
    # to create the test data used by this sample command...
                          
    geoclaw_sphere_pv_clip(frameno=4, minlevel = 1, maxlevel=10, 
                           outdir='chile2010',
                           warpfactor=None, verbose=True)
                           
