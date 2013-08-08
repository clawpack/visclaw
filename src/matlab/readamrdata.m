function [amr,t] = readamrdata(dim,Frame,dir,outputflag,outputprefix,readblocknumber);

% READAMRDATA reads amr data produced by Clawpack output routines.
%
%   [AMRDATA,T] = READAMRDATA(DIM,FRAME) reads fort.tXXXX and fort.qXXXX
%   files produced by calls to the Clawpack output routines (outN.f) and
%   stores them in the structure AMRDATA for use by the Matlab Clawpack
%   graphing routines.  DIM specifies the dimension (1,2 or 3) of the data
%   to be read, FRAME specifies the frame number (e.g. NN in fort.q00NN).
%   The files should be in the user's current directory.  The simulation time
%   for output file is returned as T.
%
%   [...] = READAMRDATA(...,DIR) looks for the fort.XXXXX files in directory
%   DIR.  Default is the current working directory.
%
%   [...] = READAMRDATA(...,FLAG) uses FLAG to determine what kind of data
%   to read.  FLAG = 'ascii' means read the standard ascii output files
%   fort.q00NN produced by Clawpack.  FLAG = 'hdf' will read HDF4 files
%   produced by Clawpack.  FLAG='chombo' will read the HDF5 files produced
%   by ChomboClaw.  The default option is FLAG='ascii'.
%
%   The output argument AMRDATA is an array of structures whose fields are
%   some or all of :
%
%          Fields in AMRDATA(n) :
%
%            gridno              : Grid number of amr data (1..ngrids)
%            level               : Data level (1,2,3...)
%            mx, my, mz          : Dimensions of data
%            xlow, ylow, zlow    : Lower value of comp. domain
%            dx, dy, dz          : Mesh size
%            data                : Data, in linear array of size
%                                  mx (1d), mx*my (2d) or (mx*my*mz) (3d)
%
%   Example :
%
%           [amrdata,t] = readamrdata(2,12,'./results/');
%           % reads Frame 12 of 2d ascii file in ./results/
%
%           ngrids = length(amrdata);  % number of amr grids in this file
%           maxlevels = max(amrdata.level);  % maximum level.
%           lvec = zeros(maxlevels,1);
%           for i = 1:ngrids,   % loop over all grids in file
%              mx = amrdata(i).mx;        % size of grid i.
%              my = amrdata(i).my;
%              level = amrdata(i).level;
%              lvec(level) = lvec(level) + mx*my;
%           end;
%           for level = 1:maxlevels,
%              fprintf('Cells at level % d : %d\n',level,lvec(level));
%           end;
%
%   See CLAWGRAPH, CHOMBOCLAW.
%

if (nargin < 6)
  readblocknumber = 0;
  if (nargin < 5)
    outputprefix = '';
    if (nargin < 4)
      outputflag = 'ascii';
      if (nargin < 3)
	dir = './';
      end;
    end;
  end;
end


if (strcmp(dir(end),'/') == 0)
  dir = [dir, '/'];
end;

if (strcmp(lower(outputflag),'ascii') == 1)
  [amr,t] = readamrdata_ascii(dim,Frame,dir,readblocknumber);
elseif (strcmp(lower(outputflag),'hdf') == 1)
  [amr,t] = readamrdata_hdf(dim,Frame,dir);
elseif (strcmp(lower(outputflag),'chombo') == 1)
  [amr,t] = readamrdata_chombo(dim,Frame,dir,outputprefix);
else
  str = sprintf(['readamrdata : ''%s'' is not a valid OutputFlag. Use ',...
	'flag = ''ascii'' or flag = ''hdf''.'],flag);
  error(str);
end
