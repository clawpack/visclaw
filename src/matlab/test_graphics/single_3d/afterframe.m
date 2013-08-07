setviews;

grid on;

axis([0 2 0 2 0 2]);
daspect([1 1 1]);

caxis([1 3]);

hideslices;

showslices('x',1);
showslices('y',1)
showslices('z',1);

drawcontourlines(10);
view([132.5 26]);
showgridlines(1,'z');

fprintf('Enter ''x'' to loop over x slices\n');
fprintf('Enter ''y'' to loop over y slices\n');
fprintf('Enter ''z'' to loop over z slices\n');
fprintf('Hit <return> to continue to next time slice\n');
sdir = input('Choice : ','s');
if (~isempty(sdir))
  idir = findstr(lower(sdir),'xyz');
  if (~isempty(idir))
    sliceloop(sdir);
  end;
end;


clear afterframe;
