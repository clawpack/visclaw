function mask_patches2(pvecl,pvecu)

% Internal matlab routine for Clawpack graphics.

% This masks the patches in pvecl using the patches in pvecu.

if (isempty(pvecu))
  return;
end;

for j = 1:length(pvecu),
  % I shouldn't have to get this data here, but rather should have a routine
  % mask(pvec1,pvec2), where pvec2 masks pvec1.

  pj = pvecu(j);
  udata = get(pj,'UserData');
  xlow = udata.xmin;
  ylow = udata.ymin;
  zlow = udata.zmin;
  xhigh = udata.xmax;
  yhigh = udata.ymax;
  zhigh = udata.zmax;
  sdir = udata.sdir;

  for k = 1:length(pvecl)
    pk = pvecl(k);
    mask_patch(pk,sdir,xlow,xhigh,ylow,yhigh,zlow,zhigh);
    mask_clines(pk,sdir,xlow,xhigh,ylow,yhigh,zlow,zhigh);
    % mask_mesh(pk,sdir,xlow,xhigh,ylow,yhigh,zlow,zhigh);
  end;
end;  % End loop on patches that need to be masked.
