"""
Tools to read in a frame of AMR data and unpack into individual grid patches
for plotting purposes.
"""

from pylab import *
from clawpack.pyclaw.solution import Solution
from clawpack.pyclaw.fileio.ascii import read_t

def load_frame(frameno, outdir='_output', file_format=None):
    """
    Sample code to load all grid patches from a single output frame and print
    some info about each patch.

    Shows how framesoln for one time frame can be read and unpacked.
    Returns framesoln.
    """

    if file_format is None:
        try:
            [t,num_eqn,nstates,num_aux,num_dim,num_ghost,file_format] = \
                 read_t(frameno,outdir,file_prefix='fort')
        except:
            raise InputError('*** Could not read file_format from fort.t file')

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
        Note that for GeoClaw applications,
            q[0,:,:] =h is the water depth,
            q[1,:,:] = hu, momentum in x direction
            q[2,:,:] = hv, momentum in y direction
            q[3,:,:] = eta = h+B, water surface elevation (B = topography elev)
    """

    def __init__(self, frameno, outdir='_output', file_format=None,
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
