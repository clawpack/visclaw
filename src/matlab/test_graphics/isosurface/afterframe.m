yrbcolormap
grid on
axis([0 1 0 1 0 1])
daspect([1 1 1]);

hideslices;
showslices('x',6);
showslices('y',6);
showslices('z',6);

setsurfalpha(0.5,[1 3]); % set alpha on surface 1 and 3 to 0.5
reducesurf(0.5);  % reduce number of faces
showsurfmesh(2);  % show mesh on surface 2.
lighting phong;
camlight;


looping = 1;
while(looping)
  fprintf('Hit ''l'' to enter isosurface loop.\n');
  fprintf('Hit <return> to continue to next time frame\n');
  ch = input('Choice : ','s');
  if (strcmp(ch,'l'))
    surfloop;
  else
    looping = 0;
  end;
end;
