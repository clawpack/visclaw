function [xp,yp,zp] = mapc2m(xc,yc)

xp = xc;
yp = yc;
zp = sin(pi*xc).*sin(pi*yc);
