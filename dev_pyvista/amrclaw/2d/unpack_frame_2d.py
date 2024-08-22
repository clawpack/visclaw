
from pylab import *
from clawpack.pyclaw.solution import Solution

def load_frame(frameno, outdir='_output', file_format='binary32'):
    """
    Sample code to load all grid patches from a single output frame and print
    some info about each patch.

    Shows how framesoln for one time frame can be read and unpacked.
    Returns framesoln.
    """
    framesoln = Solution(frameno,path=outdir,file_format=file_format)
    print('======================')
    print('Frame %i: time = %.1f seconds' % (frameno,framesoln.t))
    print('At this time there are %i grid patches' % len(framesoln.states))
    for state in framesoln.states:
        print('------------------')
        patch = state.patch
        print('Grid at AMR level %i' % patch.level)
        X_center, Y_center = patch.grid.p_centers
        X_edges, Y_edges = patch.grid.p_nodes
        print('X_edges, Y_edges have shape: ', X_edges.shape)
        print('Lower left corner: x = %.6f, y = %.6f' \
                % (patch.grid.x.lower, patch.grid.y.lower))
        print('dx = %.6f,  dy = %.6f' \
                % (patch.grid.delta[0], patch.grid.delta[1]))
        #print(patch.grid.x)
        #print(patch.grid.y)
        h = state.q[0,:,:]  # water depth
        eta = state.q[3,:,:]  # surface elevation h+B
        B = eta - h  # topography in grid cell
    print('======================')

    return framesoln


class PatchIterator:

    """
    First pass at an interator class to read in one time frame of AMR
    data and yield one patch at a time.

    Set to yield
        level, X_edges, Yedges, q
    for each patch, where
        level = AMR level of the paatch
        X_edges,Y_edges are 2D arrays of cell edges, with shape [mx+1,my+1]
            where mx,my are the number of cells in each direction
        q is the solution, of shape [meqn, mx, my].
        For GeoClaw applications,
            q[0,:,:] =h is the water depth,
            q[1,:,:] = hu, momentum in x direction
            q[2,:,:] = hv, momentum in y direction
            q[3,:,:] = eta = h+B, water surface elevation (B = topography elev)
    """

    def __init__(self, frameno, outdir='_output', file_format='ascii',
                 verbose=False):
        self.framesoln = Solution(frameno,path=outdir,file_format=file_format)
        self.num_patches = len(self.framesoln.states)
        self.verbose = verbose

        if verbose:
            print('Created patch iterator for frame %i: time = %.1f seconds' \
                  % (frameno,self.framesoln.t))
            print('        to iterate over %i grid patches' % self.num_patches)
            print('Iterator returns level, X_edges, Y_edges, q for each patch')


    def __iter__(self):
        self.patchno = 0
        return self

    def __next__(self):
        if self.patchno >= self.num_patches:
            raise StopIteration

        state = self.framesoln.states[self.patchno]
        patch = state.patch
        level = patch.level
        X_center, Y_center = patch.grid.p_centers
        X_edges, Y_edges = patch.grid.p_nodes
        q = state.q
        if self.verbose:
            print('Patch iterator: %3ix%3i grid patch at AMR level %i' \
                  % (X_edges.shape[0], X_edges.shape[1], level))
        self.patchno += 1
        return level, X_edges, Y_edges, q


def test_plot(frameno, minlevel=1, maxlevel=10, verbose=True):
    """
    Make a simple matplotlib plot with finer grids plotted on top
    of coarser ones.

    Plot grids up to level maxlevel (or finest level present).
    """

    from clawpack.visclaw.geoplot import tsunami_colormap
    figure(1)
    clf()
    patch_iterator = PatchIterator(frameno, outdir='_output',
                                   file_format='binary32', verbose=verbose)
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
        pcolor(X,Y,eta_wet,cmap=tsunami_colormap, edgecolors='k')
        clim(-0.2, 0.2)
    colorbar()


def extend_cells_to_points(cell_values):

    """
    Take an array of cell_values defined on a mx by my grid patch
    and extend to an array point_values defined on the (mx+1) by (my+1)
    grid of cell corners.
    """

    point_values = zeros((cell_values.shape[0]+1, cell_values.shape[1]+1))

    # add together 4 copies, shifted by one in each direction:
    point_values[:-1, :-1] += cell_values
    point_values[1:, :-1] += cell_values
    point_values[:-1, 1:] += cell_values
    point_values[1:, 1:] += cell_values

    # convert sums to averages:

    # interior of patch:
    point_values[1:-1, 1:-1] /= 4

    # patch edges except corners:
    point_values[1:-1, 0] /= 2
    point_values[1:-1, -1] /= 2
    point_values[0, 1:-1] /= 2
    point_values[-1, 1:-1] /= 2

    # corners are fine since only copy reached each corner

    return point_values


def test_pv_clip(frameno, minlevel = 1, maxlevel=10, outdir='_output',
                 file_format='binary32', verbose=True):

    """
    Plot grids up to level maxlevel.
    On each level, holes are first cut out for all grids at higher levels.
    If warp_plot is True below, warp grid by surface elevation.
    """

    import pyvista as pv
    from clawpack.visclaw.geoplot import tsunami_colormap

    warp_plot = True

    # read frame solution just to get time:
    framesoln = Solution(frameno,path=outdir,file_format=file_format)
    print('Frame %i: time = %.1f seconds' % (frameno,framesoln.t))
    time = framesoln.t

    print('Will show grids up to level %i (with holes for finer grids)' \
            % maxlevel)

    # make an iterator for looping over all patches in this frame:
    patch_iterator = PatchIterator(frameno, outdir=outdir,
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

        if warp_plot:
            # water surface eta:
            eta_point = extend_cells_to_points(eta_wet)
            eta_point = minimum(eta_point, 0.5)  # limit big values near coast
            gridxyz.point_data['eta_point'] = eta_point.flatten(order='F')

            # topography can be computed as eta - h (surface - depth)
            #topo = q[-1,:,:] - q[0,:,:]
            topo_point = extend_cells_to_points(topo)

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

            if not warp_plot:
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
                warpfactor = 20.
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
