function set_slices(sdir,slices)

% Internal matlab routine for Clawpack graphics.

ftag = get(gcf,'Tag');

if (~strcmp(ftag,'AMRClawSlicePlot'))
  error('get_slices : Current figure does not contain slice data');
end

amrplot = get(gcf,'UserData');
slice_handles = amrplot.slices;

idir = strfind('xyz',lower(sdir));
if (isempty(idir))
  error('set_slices : sdir must be equal to ''x'', ''y'', or ''z''');
end

slice_handles{idir} = slices;
amrplot.slices = slice_handles;
set(gcf,'UserData',amrplot);
