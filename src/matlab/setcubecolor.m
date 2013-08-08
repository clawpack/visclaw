function setcubecolor(c,level)

%  SETCUBECOLOR sets the color of 3d amr cubes.
%
%   SHOWCUBECOLOR(C,LEVEL) sets the color of 3d cubes at levels in
%   specifed as entries in vector LEVEL to C.  C must be a valid
%   colorspec, either a string ('k','b','g', etc) or an RGB triple.
%
%   SHOWCUBECOLOR(C) sets the color at all levels to color C.
%
%   See SHOWCUBES, HIDECUBES, SHOWPATCHBORDERS, HIDEPATCHBORDERS.

cubes = get_cubes;

if (nargin < 2)
  level = 1:length(cubes);
end;

for l = 1:length(level),
  cube_vec = cubes{level(l)};
  for k = 1:length(cube_vec),
    cube = cube_vec(k);
    set(cube.c,'Color',c);
  end;
end;
