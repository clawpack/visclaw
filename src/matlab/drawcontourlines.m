function drawcontourlines(v, sdir,snum)

% DRAWCONTOURLINES draws contour lines.
%
%
%     DRAWCONTOURLINES(V,SDIR,SNUM) draw contour lines at levels V
%     on slices xSliceCoords(SNUM), ySliceCoords(SNUM)
%     or zSliceCoords(SNUM), depending on value SDIR ('x','y',or 'z').
%
%     DRAWCONTOURLINES(V,SDIR) draws contour lines on all slices in
%     direction SDIR.
%
%     DRAWCONTOURLINES(V), draws contour lines on all slices in all
%     directions.
%
%     V is anything that is valid for Matlab's contour plotter. If
%     V is a scalar, then V contour lines will be automically chosen
%     and drawn on each specified slice.  Note that the values of the
%     contour lines in this case will be independently chosen, and
%     so will not match up across AMR patches, or at slice intersections.
%     If V is a vector of length N, then N contour levels at levels
%     specified in V will be chosen.  To plot a single contour line
%     at level C, set V = [C C].
%
%     DRAWCONTOURLINES(...) removes any existing contour lines on specified
%     slices before plotting new lines specified in V.
%
%     See also SHOWCONTOURLINES, HIDECONTOURLINES.

if (nargin < 2)
  sdirs = {'x', 'y','z'};
else
  sdirs = {sdir};
end;

for idir = 1:length(sdirs),
  sdir = sdirs{idir};
  slices = get_slices(sdir);
  if (nargin < 3)
    snum = 1:length(slices);
  end;
  for ns = 1:length(snum),
    n = snum(ns);
    if (n < 1 | n > length(slices))
      continue;
    end;
    slice = slices{n};
    for level = 1:length(slice),
      pvec = slice{level};
      for k = 1:length(pvec);
	p = pvec(k);
	udata = get(p,'UserData');
	delete(udata.contourLines);
	[xc_like, yc_like, zc_like] = ...
	    get_xyzlike(udata.xc,udata.yc,udata.zc,sdir);
	c = contourc(yc_like,zc_like,udata.q,v);
	udata.contourLines = create_clines(c,udata.sval,...
	    sdir,udata.mappedgrid,udata.manifold,udata.blockno);
	set(p,'UserData',udata);
	set_cline_visibility(p);
      end;
    end;
    mask_patches_all(slice);  % To mask any contourlines.
  end;
end;
