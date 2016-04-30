function lmax = getmaxlevel(amrdata)
% GETMAXLEVEL returns the maximum number of levels in an amr plot.
%
%      LMAX = GETMAXLEVEL returns the maximum number of levels used in an
%      adaptive plot.  
%
% See also getminlevel.
%

n = length(amrdata);
[X{1:length(amrdata)}] = deal(amrdata.level);

lmax = max(cell2mat(X));
