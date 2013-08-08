function setgridlinecolor(c)

%  SETGRIDLINECOLOR sets colors for grid lines.
%
%  SETGRIDLINECOLOR(C) sets the color of grid lines to color C.
%  C should be a valid colorspec value, either a string
%  indicating a color value ('b','r','g', etc.) or an RGB triple.
%
%  See also SHOWGRIDLINES, HIDEGRIDLINES, SHOWPATCHBORDERS,
%  HIDEPATCHBORDERS.
%

sdirs = {'x','y','z'};
for idir = 1:length(sdirs),
  slices = get_slices(sdirs{idir});
  for n = 1:length(slices),
    slice = slices{n};
    for level = 1:length(slice),
      pvec = slice{level};
      for k = 1:length(pvec),
	p = pvec(k);
	udata = get(p,'UserData');
	udata.edgecolor = c;
	set(p,'UserData',udata);
	status = get(p,'EdgeColor');
	if (~strcmp(status,'none'))
	  set(p,'EdgeColor',c);
	end;
      end;
    end;
  end;
end;
