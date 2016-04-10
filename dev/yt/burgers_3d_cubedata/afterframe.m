yrbcolormap
caxis([0 1])
grid on
axis([0 1 0 1 0 1])
daspect([1 1 1])

hideslices;
showslices('y',7);
showslices('z',5);

showcubes;
hidecubes(1:2);
setcubecolor('k',1);
setcubecolor('k',2);
setcubecolor('k',3);

showpatchborders;
showgridlines(1:2);

cv = 0.1:0.1:0.9;
drawcontourlines(cv);

colorbar;
h = surflight;

% The isosurface is more visible when set to white.
% setsurfcolor('w');

axis off;
shg;

clear afterframe;
