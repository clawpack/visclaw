function set_clines(sdir,snum,p,hlines)

% Internal matlab routine for Clawpack graphics.

ftag = get(gcf,'Tag');

if (~strcmp(ftag,'AMRClawSlicePlot'))
  error('get_clines : Current figure does not contain slice data');
end;

amrplot = get(gcf,'UserData');

idir = findstr(lower(sdir),'xyz');

% Get array of structures for contour lines segments on patch p.
cvallist = amrplot.contourlist{idir};

% Loop over contour line segments on this patch.
for i = 1:length(hlines),
  udata = get(hlines(i),'UserData');
  cval = udata.cval;
  if (isempty(cvallist))
    j = [];
  else
    j = find(cvallist.cval == cval);
  end;
  if (isempty(j))
    cvallist(end+1).cval = cval;
    cvallist(end+1).hlines == hlines(i);
    cvallist(end+1).plist = p;
  else
    cvallist(j).hlines(end+1) = hlines(i);
    cvallist(j).plist(end+1) = p;
  end;
end;



set(gcf,'UserData',amrplot);
