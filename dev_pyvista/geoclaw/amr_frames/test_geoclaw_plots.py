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
    colorbar()



def geoclaw_pv_clip(frameno, minlevel = 1, maxlevel=10, outdir='_output',
                    warpfactor=None, verbose=True):

    """
    Plot grids from level minlevel up to level maxlevel (or finest level).
    On each level, holes are first cut out for all grids at higher levels.
    If warpfactor is not None, warp grid by surface elevation.
    """

    import pyvista as pv
    from clawpack.visclaw.geoplot import tsunami_colormap
    from clawpack.pyclaw.fileio.ascii import read_t

    if outdir == 'chile2010':
        # shorthand for this standard example:
        outdir = CLAW + '/geoclaw/examples/tsunami/chile2010/_output'
        
    try:
        [time,num_eqn,nstates,num_aux,num_dim,num_ghost,file_format] = \
             read_t(frameno,outdir,file_prefix='fort')
    except:
        raise InputError('*** Could not read time from fort.t file')
            
    # read frame solution just to get time:
    # framesoln = Solution(frameno,path=outdir,file_format=None)
    # print('Frame %i: time = %.1f seconds' % (frameno,framesoln.t))
    #time = framesoln.t

    print('Will show grids up to level %i (with holes for finer grids)' \
            % maxlevel)

    # make an iterator for looping over all patches in this frame:
    patch_iterator = unpack_frame_2d.PatchIterator(frameno, outdir=outdir,
                                                   file_format=None)

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

        # append this patch to the set of patches to be plotted:
        patches_on_level[level].append([gridxyz, bounds])

    # now construct plotter:

    plotter = pv.Plotter()

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

            if warpfactor is None:
                # flat 2d plot:
                plotter.add_mesh(gridxyz, scalars='eta', cmap=tsunami_colormap,
                                 clim=(-0.2,0.2),show_edges=True)
                if 0:
                    # this plots grey everywhere topo is nan,
                    # Would like to be transparent, as in warped version.
                    #plotter.add_mesh(gridxyz, scalars='topo', cmap='gist_earth',
                    #             clim=(-500,3000),show_edges=False)

                    plotter.add_mesh(gridxyz, color='g')
            else:
                # warp surface based on eta (point_values needed):
                etawarp = gridxyz.warp_by_scalar('eta_point', factor=warpfactor)
                plotter.add_mesh(etawarp, cmap=tsunami_colormap,
                                 clim=(-0.2,0.2),show_edges=False)

                # add warp of topo scaled down so it's nearly flat:
                topowarp = gridxyz.warp_by_scalar('topo_point', factor=1e-5)
                #plotter.add_mesh(topowarp, cmap='gist_earth',
                #                 clim=(-500e-5,3000e-5),show_edges=False)

                # this works ok to make it solid green:
                plotter.add_mesh(topowarp, color='g')

            if verbose: print(' adding to plotter')

    plotter.camera_position = 'xy'
    plotter.add_title('Time %.1f seconds' % time)
    plotter.show(window_size=(1500,1500))
