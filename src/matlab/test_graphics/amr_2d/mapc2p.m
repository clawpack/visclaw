function [xp,yp] = mapc2p(xc,yc)

xp = yc.*cos(2*pi*xc);
yp = yc.*sin(2*pi*xc);
