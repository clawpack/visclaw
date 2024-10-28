from pylab import *
from clawpack.pyclaw import Solution
import os
import pyvista as pv

# import dev_pyvista so that relative imports work:
CLAW = os.environ['CLAW']
VISCLAW = CLAW + '/visclaw'
sys.path.insert(0, VISCLAW)
import dev_pyvista
sys.path.pop(0)

from dev_pyvista.amrclaw import unpack_frame_patches # to unpack grid patches

    
def amrclaw_pv_clip(frameno, minlevel = 1, maxlevel=10, outdir='_output',
                    show_edges=True, verbose=True):

    """
    Plot grids from level minlevel up to level maxlevel (or finest level).
    On each level, holes are first cut out for all grids at higher levels.
    """

    import pyvista as pv
    from clawpack.visclaw import colormaps
    from clawpack.pyclaw.fileio.ascii import read_t
        
    try:
        [time,num_eqn,nstates,num_aux,num_dim,num_ghost,file_format] = \
             read_t(frameno,outdir,file_prefix='fort')
    except:
        raise InputError('*** Could not read time from fort.t file')


    print('Will show grids up to level %i (with holes for finer grids)' \
            % maxlevel)

    # make an iterator for looping over all patches in this frame:
    patch_iterator = unpack_frame_patches.PatchIterator(frameno, outdir=outdir,
                                                   file_format=None)

    # a dictionary to keep track of all grid patches at each level:
    patches_on_level = {}
    for k in range(1,maxlevel+2):
        patches_on_level[k] = []

    for level,patch_edges,q in patch_iterator:

        # process each grid patch and put on lists by level

        if level < minlevel:
            # skip to next patch
            print('Skipping patch at level %i < minlevel' % level)
            continue

        if level > maxlevel+1:
            print('breaking since level = %i > maxlevel+1' % level)
            break

        X_edges, Y_edges, Z_edges = patch_edges[:3]
        bounds = [X_edges.min(), X_edges.max(),
                  Y_edges.min(), Y_edges.max(),
                  Z_edges.min(), Z_edges.max()]


        x = X_edges[:,0,0]
        y = Y_edges[0,:,0]
        z = Z_edges[0,0,:]
        #import pdb; pdb.set_trace()
        X,Y,Z = meshgrid(x, y, z, indexing='ij')
        gridxyz = pv.StructuredGrid(X,Y,Z)
        #import pdb; pdb.set_trace()
        print('Created gridxyz at level %s' % level)
        print('  with shape ',X.shape)

        # set value to plot:
        qscalar = q[0,:,:,:]
        gridxyz.cell_data['qscalar'] = qscalar.flatten(order='F')

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

            if 0:
                plotter.add_mesh(gridxyz, scalars='qscalar', 
                             cmap=colormaps.yellow_red_blue,
                             clim=(0,1),show_edges=show_edges)
                             
            plotter.add_mesh(gridxyz, style='wireframe',
                             color='blue', label='Input')
            bounds = [0,0.25, 0.,1, 0,0.25]
            clipped = gridxyz.clip_box(bounds)
            plotter.add_mesh(clipped, label='Clipped')


    #plotter.camera_position = 'xy'
    plotter.add_title('Frame %i at Time = %.2f' % (frameno,time))
    plotter.add_axes()
    plotter.show(window_size=(1500,1500))

if __name__ == '__main__':
    
    # Note: You first need to run the code in 
    #     $CLAW/amrclaw/examples/advection_3d_swirl
    # to create the test data used by this sample command...
    
    outdir = '/Users/rjl/git/clawpack/amrclaw/examples/advection_3d_swirl/_output'
        
    amrclaw_pv_clip(4, minlevel = 1, maxlevel=3, outdir=outdir,
                    show_edges=True, verbose=True)
