function ghout = add_gauges(format)
%
% add_gauges plots gauge locations from file 'gauges.data'
%
% add_gauges() will plot a symbol at gauge locations found in the
% file 'gauges.data'.  
%
% add_gauges(FORMAT) The format can be specified to make sure that gauges
% are plotted at suitable z-level and that they will appear  on top of all
% levels. Available formats are either 'geoclaw' or 'forestclaw' (default).
%
% gout = add_gauges(...) returns a handle to the symbols plotting for
% gauges.  
% 
% See also add_regions, plot_gauges.


if (nargin < 1)
    format = 'ForestClaw';
end

o = findobj(gcf,'Tag','gauge');
if (~isempty(o))
    delete(o);
end

use_forestclaw = strcmpi(format,'forestclaw');

np = get(gca,'NextPlot');
set(gca,'NextPlot','add');

if (~exist('gauges.data','file'))
    fprintf('File gauges.data does not exist.  No gauges will be plotted.\n');
    return
end

fid = fopen('gauges.data','r');
for i = 1:5
    % Read first five lines of comments
    l = fgetl(fid);
end


if (use_forestclaw)
    zmax = 0;
    zl = [-20,0];
else
    % Use AMRClaw : set maxlevel = 20
    zmax = 20;
    zl = [0,20];
end

gtype = struct('id',[],'longitude',[],'latitude',[],'t0',[],'t1',[]);

l = fgetl(fid);  % blank line
l = fgetl(fid);  % Get number of gauges
num_gauges = sscanf(l,'%d',1);
gauge_handles = zeros(num_gauges,1);
for n = 1:num_gauges
    l = fgetl(fid);
    data = sscanf(l,'%d %e %e %e %d',Inf);
    g = gtype;
    g.id = data(1);
    g.longitude = data(2);
    g.latitude = data(3);
    g.t0 = data(4);
    g.t1 = data(5);    
    zp = zmax;
    hg = plot3(data(2),data(3),zp,'m.','linewidth',3,'markersize',95);
    set(gca,'zlim',zl);
    view(2);
    % set(gca,'zlimmode','auto');
    set(hg,'Tag','gauge');
    set(hg,'userdata',g);
    h = text(data(2),data(3),zp,sprintf('%d',data(1)),'fontsize',11,'color','k');
    set(h,'HorizontalAlignment','center');
    % set(h,'backgroundcolor','none');
    gauge_handles(n) = hg;
end

zl = zlim;
if (use_forestclaw)
    set(gca,'zlim',[min(zl),zmax]);
else
    set(gca,'zlim',[0,zmax]);
end


set(gca,'NextPlot',np);
set(gca,'userdata',gauge_handles);

if (nargout > 0)
    ghout = gauge_handles;
end

end