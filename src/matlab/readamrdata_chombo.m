function [amr,t] = readamrdata_chombo(dim,Frame,dir,...
    outputprefix);

% Internal routine for ChomboClaw graphics.

vstr = version;
% if (~strcmp(vstr(1:5),'6.5.1'))
%   error(['Matlab version 6.5.1 is required to plot output from ',...
%       'ChomboClaw.']);
% end;

nstr = num2str(Frame+10000);
nstr = nstr(2:end);
fname = [dir,outputprefix, nstr,'.',num2str(dim),'d.hdf5'];

if ~exist(fname)
  amr = {};
  t = [];
  disp(' ');
  disp(['Frame ',num2str(Frame),' (',fname,') does not exist ***']);
  disp(' ');
  return;
end

disp(['Reading data from ',fname]);

t = hdf5read(fname,'/time');
meqn = double(hdf5read(fname,'/num_components'));

% These are the low values for the level 0 grid.
xlower = 0;
ylower = 0;
zlower = 0;

fileinfo = hdf5info(fname);

% This is the maximum number of levels created, and may be smaller
% than claw.max_level, set in the ChomboClaw input file.
max_level = length(fileinfo.GroupHierarchy.Groups) - 2;

clear amr;
ng = 1;
for level = 0:max_level,

  % read parameters for this level
  gstring = ['/level_',num2str(level)];

  dx = hdf5read(fname,[gstring,'/dx']);
  dy = dx;
  if (dim == 3)
    dz = dx;
  end;

  % Dimensions of boxes at this level.
  % This is where we really read everything in.

  data = hdf5read(fname,[gstring,'/data:datatype=0']);
  didx = 0;

  boxes = hdf5read(fname,[gstring,'/boxes']);
  for j = 1:length(boxes),
    clear amrdata;
    amrdata.gridno = ng;
    amrdata.level = level + 1;  % Chombo levels start at 0;
    amrdata.dx = dx;
    amrdata.dy = dx;
    if (dim == 3)
      amrdata.dz = dx;
    end;

    if (dim == 2)
      lo_i = double(boxes(j).Data{1});
      lo_j = double(boxes(j).Data{2});
      hi_i = double(boxes(j).Data{3});
      hi_j = double(boxes(j).Data{4});
    elseif (dim == 3)
      lo_i = double(boxes(j).Data{1});
      lo_j = double(boxes(j).Data{2});
      lo_k = double(boxes(j).Data{3});
      hi_i = double(boxes(j).Data{4});
      hi_j = double(boxes(j).Data{5});
      hi_k = double(boxes(j).Data{6});
    end;
    amrdata.mx = hi_i - lo_i + 1;
    amrdata.my = hi_j - lo_j + 1;
    if (amrdata.mx == 1 | amrdata.my == 1)
      % Can't plot these tiny grids...
      % continue;
    end;
    if (dim == 3)
      amrdata.mz = hi_k - lo_k + 1;
      if (amrdata.mz == 1)
	continue;
      end
    end;

    amrdata.xlow = xlower + dx*lo_i;
    amrdata.ylow = ylower + dy*lo_j;
    if (dim == 3)
      amrdata.zlow = zlower + dz*lo_k;
    end;

    len = amrdata.mx*amrdata.my;
    if (dim == 3)
      len = len*amrdata.mz;
    end;
    amrdata.data = reshape(data(didx+1:didx+len*meqn),len,meqn)';
    didx = didx + len*meqn;

    amr(ng) = amrdata;
    ng = ng + 1;
  end;  % end loop over boxes on this level
end;  % end loop on levels
