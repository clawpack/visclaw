"""
Tools to read in a frame of AMR data and unpack into individual grid patches
for plotting purposes.
"""

from pylab import *
from clawpack.pyclaw.solution import Solution
from clawpack.pyclaw.fileio.ascii import read_t


class PatchIterator:

    """
    First pass at an interator class to read in one time frame of AMR
    data and yield one patch at a time.

    Set to yield
        level, patch_edges, q
    for each patch, where
        level = AMR level of the paatch
        patch_edges are arrays of cell edges, with shape [mx+1,my+1,mz+1]
            where mx,my,mz are the number of cells in each direction if
            reading 3D AMR patches.
            In 2D: the patch_edges returned have shape [mx+1,my+1,2]
            with the edges in z at -1, +1.
        q is the solution, of shape [meqn, mx, my, mz].
    """

    def __init__(self, frameno, outdir='_output', file_format=None,
                 verbose=False):

        if file_format is None:
            try:
                [t,num_eqn,nstates,num_aux,num_dim,num_ghost,file_format] = \
                     read_t(frameno,outdir,file_prefix='fort')
            except:
                msg = '*** Could not read file_format from fort.t file in \n  %s' \
                            % outdir
                raise IOError(msg)                

        self.framesoln = Solution(frameno,path=outdir,file_format=file_format)
        self.num_patches = len(self.framesoln.states)
        self.verbose = verbose

        if verbose:
            print('Created patch iterator for frame %i: time = %.1f seconds' \
                  % (frameno,self.framesoln.t))
            print('Iterator returns level, patch_edges, q for each patch,')
            print('  patch_edges[0] is X array, etc., q[meqn,...] is component')
        

    def __iter__(self):
        self.patchno = 0
        return self

    def __next__(self):
        if self.patchno >= self.num_patches:
            raise StopIteration
        
        state = self.framesoln.states[self.patchno]
        patch = state.patch
        level = patch.level
        patch_edges = patch.grid.p_nodes
        if len(patch_edges) == 2:
            if self.verbose:
                print('For 2D problem will add z edges at [-1,1]')
            patch_edges = (patch_edges[0], patch_edges[1], [-1,1])
        q = state.q
        if self.verbose:
            print('Patch iterator: grid patch at AMR level %i with shape %s' \
                  % (level, patch_edges[0].shape))
        self.patchno += 1
        return level, patch_edges, q




def extend_cells_to_points(cell_values):

    """
    Take an array of cell_values defined on a mx by my grid patch
    and extend to an array point_values defined on the (mx+1) by (my+1)
    grid of cell corners.
    
    Only implemented in 2D so far.
    """

    if cell_values.ndim != 2:
        raise NotImplementedError(\
                '*** extend_cells_to_points only implemented in 2D')
                
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
