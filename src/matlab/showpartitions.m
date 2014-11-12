function cm = showpartitions(cm,npmax)

% Assume that data is discrete values [0,1,2,3,4...,npmax-1]
% and that is to be plotted using with distinct colors.

colormap(cm);
caxis([0 npmax]);

showpatchborders;
hidegridlines;

multicolormap_colorbar(npmax);

end

