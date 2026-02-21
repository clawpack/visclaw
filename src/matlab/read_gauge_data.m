function gauges = read_gauge_data()
%
% read_gauge_data() reads data in a file 'gauges.data'.  Data is assumed to
% be in the current directory. 
% 
% See also track_gauges, add_gauges, add_regions.

if (~exist('gauges.data','file'))
    fprintf('File gauges.data does not exist.  No gauges will be plotted.\n');
    gauges = [];
    return
end

fid = fopen('gauges.data','r');
for i = 1:5
    % Read first five lines of comments
    fgetl(fid);
end

gtype = struct('id',[],'x',[],'y',[],'t0',[],'t1',[]);

fgetl(fid);  % blank line
l = fgetl(fid);  % Dimension
dim = sscanf(l,'%d',1);
l = fgetl(fid);  % Get number of gauges
num_gauges = sscanf(l,'%d',1);
gauges(1:num_gauges) = gtype;
for n = 1:num_gauges
    l = fgetl(fid);
    data = sscanf(l,'%d %e %e %e %d',Inf);
    g = gtype;
    g.id = data(1);
    g.x = data(2);
    g.y = data(3);
    if dim == 2
        g.t0 = data(4);
        g.t1 = data(5);
    else
        g.z = data(4);
        g.t0 = data(5);
        g.t1 = data(6);
    end

    gauges(n) = g;
end

end
