function showcubes(level)

% SHOWCUBES shows 3d patch borders
%
%   SHOWCUBES(LEVEL) shows 3d amr cubes at levels specified by vector
%   LEVEL.
%
%   SHOWCUBES, by itself, shows 3d amr cubes at all levels.
%
%   See SETCUBECOLORS, SETPLOT3, HIDECUBES, SHOWPATCHBORDERS,
%   HIDEPATCHBORDERS.

cubes = get_cubes;

if nargin < 1
  level = 1:length(cubes);
end;

for l = 1:length(level),
  cube_vec = cubes{level(l)};
  for k = 1:length(cube_vec),
    cube = cube_vec(k);
    set(cube.c,'Visible','on');
  end;
end;
