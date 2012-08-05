
.. _output_ascii:

******************************
ASCII output data format
******************************

Two output files are created at each output time (each frame).  The frames
are generally numbered 0, 1, 2, etc.  The two files, at frame 2, for
example, are called `fort.t0002` and `fort.q0002`.  

`fort.t0002`
------------

This file has the typical form::

    0.50000000E+00    time
    1                 meqn
    36                ngrids
    3                 naux
    2                 ndim

This file contains only 5 lines with information about the current time the
number of AMR grids (terminology: change to patches!) at this time. 

In the above example, Frame 2 contains 36 patches.  
If you are using the classic code
or PyClaw with only a single patch, then `ngrids` would be 1.

The data for all 36 patches is contained in `fort.q0002`.  The data from each
patch is preceeded by a header that tells where the patch is located in the
domain, how many grid cells it contains, and what the cell size is, e.g. 

`fort.q0002`
------------

This header has the typical form::

    1                 grid_number
    1                 AMR_level
    40                mx
    40                my
    0.00000000E+00    xlow
    0.00000000E+00    ylow
    0.25000000E-01    dx
    0.25000000E-01    dy

This would be followed by 40*40 = 1600 lines with the data from cells (i,j).
The order they are written is (in Fortran style)::

    do j = 1,my
        do i = 1,mx
            write (q(i,j,m), m=1,meqn)

Each line has `meqn` (change to `num_eqn`?) values, for the components of
the system in this grid cell.

After the data for this patch, there would be another header for the next
patch, followed by its data, etc.

In the header, `xlow` and `ylow` are the coordinates of the lower left
corner of the patch, `dx` and `dy` are the cell width in `x` and `y`, and 
`AMR_level` is the level of refinement, where 1 is the coarsest level.  
Each patch has a unique `grid_number` that usually isn't needed for
visualization purposes.



