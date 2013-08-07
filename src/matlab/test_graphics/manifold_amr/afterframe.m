grid on;

axis([0 1 0 1 0 1]);
daspect([1 1 2]);
rybcolormap
caxis([-.1 .1])

p = projectcontours('z',-1);
set(p,'FaceColor',[0.5 0.6 0.7]);

yn = input('View projected contours? (y/n) : ','s');
if (strcmp(yn,'y') == 1)
  hideslices;
  setviews;
  view(vtop);
  input('Hit <return> to return to manifold view : ');
end;

showslices;
view(3);
