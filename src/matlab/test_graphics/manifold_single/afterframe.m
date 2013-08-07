grid on;

axis([0 1 0 1 -1 1]);
daspect([1 1 2]);
rybcolormap
caxis([-.1 .1])

hidepatchborders;
showmesh(16,1);
hidecontourlines;
p = projectcontours('z',-2);
set(p,'FaceColor',[0.8 0.8 0.8]);
