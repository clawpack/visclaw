rybcolormap

if (Manifold)
  axis([0 1 0 1 0 1]);
  showmesh(20,1);
else
  axis([0 1 0 1]);
end;
daspect([1 1 2]);

hold on;
xdata = ones(1,101)*0.5;
ydata = 0:0.01:1;
if (Manifold)
  [xdata,ydata,zdata] = mapc2m(xdata,ydata);
else
  zdata = zeros(1,101);
end;
zdata = zdata + 1e-2;
line('XData',xdata,'YData',ydata,'ZData',zdata,'LineWidth',3,'color','w');

hidegridlines;

drawcontourlines(30);

clear afterframe;