function setcontourlineprops(varargin)
%SETCONTOURLINEPROPS sets colors, linewidth, etc for patch borders
%
%   SETCONTOURLINEPROPS(LEVEL,PROPS) sets properties for contour lines
%   at level LEVEL, using any of the allowable line style properties.  
%
%   SETCONTOURLINEPROPS(PROPS) sets the properties at all levels.
%
%   PROPS are parameter pairs (PropertyName,PropertyValue)
%
%   Example :
%   setcontourlineprops(3,'color','r','linewidth',2,'linestyle','dashed');
%
%   See also SHOWPATCHBORDERS, HIDEPATCHBORDERS, SHOWGRIDLINES,
%   HIDEGRIDLINES, SETPATCHBORDERPROPS
%

if (isnumeric(varargin{1}))
  level = varargin{1};
  props = {varargin{2:end}};
  narginlt2 = false;
else
  narginlt2 = true;
  props = {varargin{:}};
end;

sdirs = {'x','y','z'};
for idir = 1:length(sdirs),
  slices = get_slices(sdirs{idir});
  for n = 1:length(slices),
    slice = slices{n};
    if (narginlt2)
      level = 1:length(slice);
    end;
    for l = 1:length(level),
      pvec = slice{level(l)};
      for k = 1:length(pvec),
	p = pvec(k);
	udata = get(p,'UserData');
	set(udata.contourLines,props{:});
      end;
    end;
  end;
end;
