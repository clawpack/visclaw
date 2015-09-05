function lmax = getminlevel(amrdata)
% GETMINLEVEL returns the minimum number of levels in an amr plot.
%
%      LMAX = GETMINILEVEL returns the minimum number of levels used in an
%      adaptive plot.  
%
% See also getmaxlevel.
%

n = length(amrdata);
[X{1:length(amrdata)}] = deal(amrdata.level);

lmax = min(cell2mat(X));