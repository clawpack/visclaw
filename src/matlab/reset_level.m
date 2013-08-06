function reset_level(pvec)

% Internal Matlab clawpack graphics routine.

for k = 1:length(pvec),
  p = pvec(k);
  udata = get(p,'UserData');
  set(p,'Vertices',udata.phys_vertices);
  clines = udata.contourLines;
  for i = 1:length(clines),
    cline_udata = get(clines(i),'UserData');
    set(clines(i),'XData',cline_udata.phys_vertices(:,1));
    set(clines(i),'YData',cline_udata.phys_vertices(:,2));
    set(clines(i),'ZData',cline_udata.phys_vertices(:,3));
  end;
end;
