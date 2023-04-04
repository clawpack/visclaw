function o = multicolormap_colorbar(npmax)

% MULTICOLORMAP_COLORBAR produces a colorbar for the mutlticolormap. 
%
% H = MULTICOLORMAP_COLORBAR(NP) produces a handle to a color bar designed
% specifically for use with partition maps, used primiarly to block
% parallel partition boundaries. 
%
% Example : 
% 
% npmax = 10;  % Maximum number of partitions (processors)
% cm = multicolormap(npmax);
% colormap(cm);
% caxis([1 npmax+1]);
% h = multicolormap_colorbar(npmax);

qmin = 0;    % assume min is processor 0 and max if NP-1
qmax = npmax-1;

o = colorbar;
% o = findobj('Tag','Colorbar');
set(o,'ytick',(0:(npmax)) + 0.5);
set(o,'yticklabel',(1:npmax)-1);
set(o,'ylim',[qmin qmax+1]);
set(o,'ticklength',0)
set(o,'fontsize',16,'fontweight','bold')

