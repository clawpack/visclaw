"""
Functions to take a rectangular patch of data, or an AMRClaw framesoln
containing many patches, and extract values on a new single grid.
Can be used to generate a uniform grid from an AMR solution, or to extract
a 1d transect (or values at any given set of points) from a 2d patch or
framesoln.


:Functions:
  - grid_eval_2d: take single patch of 2d data and evaluate on new grid
  - grid_output_2d: take 2d (AMR) solution and evaluate on new grid
 
:Todo:
  - extend to 1d and 3d inputs.

"""

from __future__ import print_function
import numpy as np

def grid_eval_2d(X, Y, Q, xout, yout, method='nearest', return_ma=True):
    """
    Utility function that takes a single patch of data in 2d and
    returns values on 1d or 2d grid specified by xout, yout.

    Input:
        arrays X,Y defining a grid patch and data Q on this patch,
            Q can be a 2d array of the same shape as X,Y or a
            3d array with Q[m,:,:] corresponding to the m'th value at each point
        xout, yout defining the points for output (1d or 2d arrays)
        method: by default 'nearest', which samples piecewise constant 
            values in each cell.  Can also set to 'linear'
        return_ma (bool) determines if output is a masked array
    Returns:
        qout
        
    ndim(Q) is either 2 or 3.  If 3, then Q[m,i,j] is  m'th variable at i,j
    if ndim(xout)==ndim(yout)==1 then an arbitrary set of points can be
        specified (e.g. along a transect, or curve, or scattered).
    if ndim(xout)==ndim(yout)==2 then Q is interpolated to this grid of points.
    
    if return_ma==True then the result is masked at points outside
        the limits of X,Y.   Otherwise result is NaN at these points.
    Uses zero-order interpolation, i.e.
        Sets value qout[i,j] to value in the finite volume grid cell
        of X,Y that contains (xout[i,j],yout[i,j]).
    Future: allow bilinear interpolation instead but this requires
        ghost cell values around Q grid.  (These are present in binary
        output fort.b files but normally thrown away.)
    """

    from scipy.interpolate import RegularGridInterpolator
    from numpy import ma  # for masked arrays
    
    Qdim = Q.ndim
    if Qdim == 2:
        # change to 3d array of shape (1, Q.shape[0], Q.shape[1]):
        Q = np.array([Q])
        
    nvars = Q.shape[0]  # number of arrays to interpolate

    ndim_out = len(xout.shape)
    xout1 = np.ravel(xout)
    yout1 = np.ravel(yout)
    x1 = X[:,0]
    y1 = Y[0,:]
    dx = x1[1] - x1[0]
    dy = y1[1] - y1[0]
    if dx<=0 or dy<=0:
        raise ValueError('X[:,0],Y[0,:] must be increasing. ' \
                + 'Need to transpose arrays?')

    # augment Q with border of values on all 4 sides:
    x1 = np.hstack((x1[0]-0.501*dx, x1, x1[-1]+0.501*dx))
    y1 = np.hstack((y1[0]-0.501*dy, y1, y1[-1]+0.501*dy))
    Q1 = np.empty((nvars,len(x1),len(y1)))
    Q1[:,1:-1, 1:-1] = Q   # center portion
    Q1[:,1:-1,0] = Q[:,:,0]
    Q1[:,1:-1,-1] = Q[:,:,-1]
    Q1[:,0,1:-1] = Q[:,0,:]
    Q1[:,-1,1:-1] = Q[:,-1,:]
    # corners:
    Q1[:,0,0] = Q[:,0,0]
    Q1[:,0,-1] = Q[:,0,-1]
    Q1[:,-1,-1] = Q[:,-1,-1]
    Q1[:,-1,0] = Q[:,-1,0]

    qout = np.empty([nvars]+list(xout.shape))
    for k in range(nvars):
        evalfunc = RegularGridInterpolator((x1,y1), Q1[k,:,:], method=method,
                bounds_error=False, fill_value=np.nan)
        xyout = np.vstack((xout1,yout1)).T
        qout_k = evalfunc(xyout)
        if ndim_out == 2:
            qout_k = np.reshape(qout_k, xout.shape)   
            qout[k,:,:] = qout_k
        else:
            qout[k,:] = qout_k

    if Qdim==2 and ndim_out==2:
        qout = qout[0,:,:]  # revert back to 2d array
    if Qdim==2 and ndim_out==1:
        qout = qout[0,:]  # revert back to 1d array

    if return_ma:
        # convert from an array with nan's to a masked array:
        qout = ma.masked_where(qout != qout, qout)

    #print('type is %s' % type(qout))

    return qout
    

def grid_output_2d(framesoln, out_var, xout, yout, levels='all', 
                   method='nearest', return_ma=True):

    """
    :Input:
        framesoln:  One frame of Clawpack solution (perhaps with AMR),
                 An object of type pyclaw.Solution.solution.
        out_var: function that maps q to desired quantities Q[m,i,j] or
                 Q[i,j] if only one.  
                 If type(out_var) == int, then Q[i,j] = q[out_var,i,j]
        xout, yout: arrays of output points (1d or 2d arrays)
        levels: list of levels to use, or 'all'
        method: by default 'nearest', which samples piecewise constant 
            values in each cell.  Can also set to 'linear'
        return_ma: True to return as masked_array, False to return with
                NaN in locations that framesoln doesn't cover.
    :Output:
        qout: Solution obtained on xout,yout grid

    Loop over all patches in framesoln and apply grid_eval function.
    Use non-NaN values that this returns to update qout array over the
        region covered by this patch

    :Example:

    Note that one frame of a Clawpack simulation can be loaded via, e.g.:

        from clawpack.pyclaw.solution import Solution
        framesoln = Solution(frameno=1, path='_output', 
                             file_format='ascii')

    Then define `xout, yout, out_var` and call this function.

    """
        
    from numpy import ma  # for masked arrays
    if levels == 'all':
        levels = range(1,100)  # more levels than will ever use

    qout = np.empty(xout.shape)
    qout[:] = np.nan
    xmin = xout.min()
    xmax = xout.max()
    ymin = yout.min()
    ymax = yout.max()
    for stateno,state in enumerate(framesoln.states):
        state = framesoln.states[stateno]
        patch = state.patch
        #print('level = ',patch.level)

        if patch.level not in levels:
            # skip this patch
            continue

        if (xmin > state.grid.x.upper) or (xmax < state.grid.x.lower) \
                or (ymin > state.grid.y.upper) or (ymax < state.grid.y.lower):
            # no overlap
            continue
            
        #print('overlap at level %i' % patch.level)
        Xc,Yc = state.grid.c_centers
        xc = Xc[:,0]
        yc = Yc[0,:]

        if type(out_var) == int:
            Q = state.q[out_var, :, :]
        else:
            Q = out_var(state.q)

        qout1 = grid_eval_2d(Xc, Yc, Q, xout, yout, method=method, 
                             return_ma=False)
        qout = np.where(np.isnan(qout1), qout, qout1)
        if return_ma:
            # convert from an array with nan's to a masked array:
            qout = ma.masked_where(qout != qout, qout)
    return qout

