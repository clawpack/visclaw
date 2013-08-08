function setpatchbordercolor(c,level)

%  SETPATCHBORDERCOLOR sets colors for patch borders
%
%  SETPATCHBORDERCOLOR(C,LEVEL) sets the color of all patch borders
%  at levels specified as entries in vector LEVEL to color C.
%  C should be a valid colorspec value, either a string indicating a
%  color value ('b','r','g', etc.) or an RGB triple.
%
%  SETPATCHBORDERCOLOR(C) sets color of all patch borders on all levels to
%  C
%
%  See also SHOWPATCHBORDERS, HIDEPATCHBORDERS, SHOWGRIDLINES,
%  HIDEGRIDLINES, SETGRIDLINECOLOR.
%

sdirs = {'x','y','z'};
for idir = 1:length(sdirs),
  slices = get_slices(sdirs{idir});
  for n = 1:length(slices),
    slice = slices{n};
    if (nargin < 2)
      level = 1:length(slice);
    end;
    for l = 1:length(level),
      pvec = slice{level(l)};
      for k = 1:length(pvec),
	p = pvec(k);
	udata = get(p,'UserData');
	set(udata.border,'Color',c);
      end;
    end;
  end;
end;
