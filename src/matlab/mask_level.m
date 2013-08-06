function mask_level(pvec,pmask)

% Internal matlab routine for Clawpack graphics.

if (isempty(pvec))
  return;
end;

udata = get(pmask,'UserData');
xlow = udata.xmin;
xhigh = udata.xmax;
ylow = udata.ymin;
yhigh = udata.ymax;
zlow = udata.zmin;
zhigh = udata.zmax;
sdir = udata.sdir;

for k = 1:length(pvec)
  p = pvec(k);
  mask_patch(p,sdir,xlow,xhigh,ylow,yhigh,zlow,zhigh);
  mask_clines(p,sdir,xlow,xhigh,ylow,yhigh,zlow,zhigh);
  % mask_mesh(p,sdir,xlow,xhigh,ylow,yhigh,zlow,zhigh);
end;  % End loop on patches that need to be masked.
