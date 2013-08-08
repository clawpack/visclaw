function setpatchborderprops(varargin)

%  SETPATCHBORDERPROPS sets colors, linewidth, etc for patch borders
%
%  SETPATCHBORDERPROPS(LEVEL,PROPS) sets properties for patch borders
%  using any of the allowable line style properties.  Patches at level LEVEL
%  will be affected.  LEVEL may be a vector of valid levels.
%
%  SETPATCHBORDERPROPS(PROPS) sets the properties at all levels.
%
%  Example :
%       setpatchborderproperties(3,'color','r','linewidth',2,'linestyle','dashed');
%
%  See also SHOWPATCHBORDERS, HIDEPATCHBORDERS, SHOWGRIDLINES,
%  HIDEGRIDLINES, SETGRIDLINECOLOR.
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
        if level(l) > length(slice)
            continue;
        end
        pvec = slice{level(l)};
        for k = 1:length(pvec),
            p = pvec(k);
            udata = get(p,'UserData');
            set(udata.border,props{:});
        end;
    end;
  end;
end;
