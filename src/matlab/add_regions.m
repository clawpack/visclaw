function rhout = add_regions(t,format)
%
% add_regions plots regions from file 'regions.data'
%
% add_regions(T) will plot a rectangle at regions found in the
% file 'regions.data' if region is active at time T.  
%
% add_regions(T,FORMAT) The format can be specified to make sure that
% regions are plotted at a suitable z-level and that they will appear  on
% top of all levels. Available formats are 'geoclaw' or 'forestclaw'
% (default).
%
% gout = add_regions(...) returns a handle to the region rectangles.
% 
% See also add_gauges, plot_gauges.


if (nargin < 2)
    format = 'ForestClaw';    
end

use_forestclaw = strcmpi(format,'forestclaw');

o = findobj(gcf,'Tag','region');
if (~isempty(o))
    delete(o);
end

np = get(gca,'NextPlot');
set(gca,'NextPlot','add');

if (~exist('regions.data','file'))
    fprintf('File regions.data does not exist.  No regions will be plotted.\n');
    return
end

fid = fopen('regions.data','r');
for i = 1:5
    % Read first five lines of comments
    fgetl(fid);
end
fgetl(fid);  % blank line
l = fgetl(fid);  % Get number of gauges
num_regions = sscanf(l,'%d',1);

c = {'w','w','w','w','w','w','w'};   % Colors for each region

if (use_forestclaw)
    zmax = 0;
    zl = [-20,0];
else
    % Use AMRClaw : set maxlevel = 20
    zmax = 20;
    zl = [0,20];
end

region_handles = zeros(num_regions,1);
for n = 1:num_regions
    l = fgetl(fid);
    data = sscanf(l,'%d %d %e %e %e %e %e %e',Inf);
    minlevel = data(1);
    maxlevel = data(2);
    t0 = data(3);
    t1 = data(4);
    x0 = data(5);
    x1 = data(6);
    y0 = data(7);
    y1 = data(8);
    xp = [x0 x1 x1 x0 x0];
    yp = [y0 y0 y1 y1 y0];
    zp = 0*xp + zmax;
    if (t0 <= t && t <= t1)
        hg = plot3(xp,yp,zp,'linewidth',2,'color',c{mod(n-1,7)+1});
        set(hg,'Tag','region');
    end
    zl = zlim;
    if (use_forestclaw)
        set(gca,'zlim',[min(zl),0]);
    else
        set(gca,'zlim',[0,max(zl)]);
    end
    hold on;
end

set(gca,'NextPlot',np);

if (nargout > 0)
    rhout = region_handles;
end

end
