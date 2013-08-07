rybcolormap

if (Manifold)
  axis([0 1 0 1 0 1]);
else
  axis([0 1 0 1]);
end;


hold on;
xdata = ones(1,101)*0.5;
ydata = 0:0.01:1;
if (Manifold)
  [xdata,ydata,zdata] = mapc2m(xdata,ydata);
else
  zdata = zeros(1,101);
end;
zdata = zdata + 3 + 1e-2;
line('XData',xdata,'YData',ydata,'ZData',zdata,'LineWidth',3,'color','w');

hidegridlines(3);
showpatchborders;
setpatchborderprops(1:10,'linewidth',2);

% for contour plots (PlotType==2):
clines = 0:0.02:0.1;
clines(1) = 0.0001;
drawcontourlines(clines);

clear afterframe;