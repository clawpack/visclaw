function gauges = read_gauge_data()

if (~exist('gauges.data','file'))
    fprintf('File gauges.data does not exist.  No gauges will be plotted.\n');
    return
end

fid = fopen('gauges.data','r');
for i = 1:5
    % Read first five lines of comments
    fgetl(fid);
end

gtype = struct('id',[],'longitude',[],'latitude',[],'t0',[],'t1',[]);

fgetl(fid);  % blank line
l = fgetl(fid);  % Get number of gauges
num_gauges = sscanf(l,'%d',1);
gauges(1:num_gauges) = gtype;
% gauge_handles = zeros(num_gauges,1);
for n = 1:num_gauges
    l = fgetl(fid);
    data = sscanf(l,'%d %e %e %e %d',Inf);
    g = gtype;
    g.id = data(1);
    g.longitude = data(2);
    g.latitude = data(3);
    g.t0 = data(4);
    g.t1 = data(5);
    gauges(n) = g;
%     hg = plot(data(2),data(3),'yx','linewidth',3,'markersize',8);
%     set(hg,'Tag','gauge');
%     set(hg,'userdata',g);
%     hold on;
%     gauge_handles(n) = hg;
%     h = text(data(2),data(3),sprintf('  %d',data(1)),'fontsize',16);
%     set(h,'HorizontalAlignment','right');
end

% set(gca,'NextPlot',np);
% set(gca,'userdata',gauge_handles);


end