function [amr,t] = readamrdata_binary(dim,Frame,dir,readblocknumber)

% Internal routine for Clawpack graphics.

n1 = Frame+10000;
fname = [dir, 'fort.',num2str(n1)];
fname(length(dir)+6) = 't';

if ~exist(fname,'file')
  amr = {};
  t = [];
  fprintf('\n');
  fprintf('Frame %d (%s) does not exist ***\n',Frame,fname);
  fprintf('\n');
  return
end

% Read data from fname = 'fort.tXXXX'
fid = fopen(fname);

t = fscanf(fid,'%g',1);        fscanf(fid,'%s',1);
meqn = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
ngrids = fscanf(fid,'%d',1);   fscanf(fid,'%s',1);
fscanf(fid,'%d',1);            fscanf(fid,'%s',1);     % Read maux
ndim = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
mbc = fscanf(fid,'%d',1);      fscanf(fid,'%s',1);
fclose(fid);

if ndim ~= dim
    error('readamrdata_binary : Dimensions do not agree');
end

if ndim <= 2
    strip_ghost = true;
else
    strip_ghost = true;
end

% change the file name to read the binary data:
fname(length(dir) + 6) = 'q';
if ~exist(fname,'file')
  amr = {};
  t = [];
  return;
end

fid = fopen(fname);

fname_bin = fname;
fname_bin(length(dir) + 6) = 'b';

fprintf('Reading data from %s ',fname_bin);

if ~exist(fname_bin,'file')
  amr = {};
  t = [];
  return
end


if dim == 1
    amr_s = struct('gridno',[],'level',[],'blockno',[],'mx',[],'xlow',[],...
        'dx',[],'data',[]);
elseif dim == 2
    amr_s = struct('gridno',[],'level',[],'blockno',[],...
        'mx',[],'my',[],'xlow',[],'ylow',[],'dx',[],'dy',[],'data',[]);
else
    amr_s = struct('gridno',[],'level',[],'blockno',[],...
        'mx',[],'my',[],'mz',[],'xlow',[],'ylow',[],'zlow',[],...
        'dx',[],'dy',[],'dz',[],'data',[],'q',[]);
end
amr = repmat(amr_s,ngrids,1);

fid_bin = fopen(fname_bin);

M = floor(ngrids/10);

for ng = 1:ngrids

  % read parameters for this grid:

  amrdata.gridno = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
  amrdata.level = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
  if (dim > 1)
    if (readblocknumber)
      amrdata.blockno = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
    else
      amrdata.blockno = 1;
    end
  end
  amrdata.mx = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
  if (dim > 1)
    amrdata.my = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
    if (dim > 2)
      amrdata.mz = fscanf(fid,'%d',1);     fscanf(fid,'%s',1);
    end
  end

  amrdata.xlow = fscanf(fid,'%g',1);     fscanf(fid,'%s',1);
  if (dim > 1)
    amrdata.ylow = fscanf(fid,'%g',1);     fscanf(fid,'%s',1);
    if (dim > 2)
      amrdata.zlow = fscanf(fid,'%g',1);     fscanf(fid,'%s',1);
    end
  end

  amrdata.dx = fscanf(fid,'%g',1);     fscanf(fid,'%s',1);
  if (dim > 1)
    amrdata.dy = fscanf(fid,'%g',1);     fscanf(fid,'%s',1);
    if (dim > 2)
      amrdata.dz = fscanf(fid,'%g',1);     fscanf(fid,'%s',1);
    end
  end

  mx = amrdata.mx;
  if (dim > 1)
      my = amrdata.my;
      if (dim > 2)
          mz = amrdata.mz;
      end
  end
  
  if strip_ghost
      % Ghost cells written out
      if (dim == 1)
          ntot = (mx+2*mbc)*meqn;
          q1d = fread(fid_bin,ntot,'double');
          q = reshape(q1d,meqn,ntot);
          q1 = zeros(meqn,mx);
          for m = 1:meqn
              q1(m,:) = q(m,mbc+1:mx+mbc);
          end
          amrdata.data = q1;
      elseif dim == 2
          ntot = (mx+2*mbc)*(my+2*mbc)*meqn;
          q1d = fread(fid_bin,ntot,'double');
          q = reshape(q1d,meqn,ntot);
          q1 = zeros(meqn,mx*my);
          for m = 1:meqn
              qt = reshape(q(m,:),(mx+2*mbc),(my+2*mbc));
              q1(m,:) = reshape(qt(mbc+1:mx+mbc,mbc+1:my+mbc),1,mx*my);
          end
          amrdata.data = q1;
      elseif dim == 3
          ntot = (mx+2*mbc)*(my+2*mbc)*(mz+2*mbc)*meqn;
          q1d = fread(fid_bin,ntot,'double');
          q = reshape(q1d,meqn,ntot);
          q1 = zeros(meqn,mx*my*mz);
          for m = 1:meqn
              qt = reshape(q(m,:),(mx + 2*mbc),(my + 2*mbc),(mz + 2*mbc));
              q1(m,:) = reshape(qt(mbc+1:mx+mbc,mbc+1:my+mbc,mbc+1:mz+mbc),1,mx*my*mz);
          end
          amrdata.data = q1;
      end
  else  
      % Ghost cells not written out
      if (dim == 1)
          ntot = mx*meqn;
      elseif dim == 2
          ntot = mx*my*meqn;
      elseif (dim == 3)
          ntot = mx*my*mz*meqn;
      end          
      q1d = fread(fid_bin,ntot,'double');
      q = reshape(q1d,meqn,ntot);
      amrdata.data = q;
  end
  
  amr(ng) = amrdata;   
  
  if mod(ng,M) == 0
      fprintf('.');
  end

end
fprintf(' Done\n');

fclose(fid);

end
