function mpirank = getmpirank()

% GETMPIRANK returns mpirank of the current patch.
%
%      MPI = GETMPIRANK returns the processor on which the current patch
%      resides.  
%
%      This will be used to visualize MPI partitioning.
%
% See also MULTICOLORMAP.
%

% The mpirank is set by set_mpirank, which is called from
% plotframe2, ploframe3 and showmesh.m

global mpi_set_mpirank;

mpirank = mpi_set_mpirank;