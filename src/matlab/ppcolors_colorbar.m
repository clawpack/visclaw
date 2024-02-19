function o = ppcolors_colorbar()

% PPCOLORS_COLORBAR produces a colorbar for the mutlticolormap. 
%
% H = PPCOLORS_COLORBAR(NP) produces a handle to a color bar designed
% specifically for use with partition maps, used primiarly to block
% parallel partition boundaries. 
%
% Example : 
% 
% npmax = 10;  % Maximum number of partitions (processors)
% cm = ppcolors(npmax);
% colormap(cm);
% caxis([1 npmax+1]);
% h = ppcolors_colorbar(npmax);

pp = parallelpartitions;
npmax = pp.npmax;

o = findobj('Tag','Colorbar');
if ishandle(o)
    delete(o);
end

o = colorbar;

if pp.invert
    qmin = pp.qmin(1);
    qmax = pp.qmax(2);
else
    qmin = pp.qmin;
    qmax = pp.qmax;
end


if pp.plotq
    set(o,'ylim',[qmin,qmax])
    clim([qmin,qmax]);
    set(o,'ticksmode','auto')
    set(o,'ticklabelsmode','auto')    
    colormap(pp.colormap);
else
    qmin = 0;    % assume min is processor 0 and max if NP-1
    qmax = npmax-1;
    ytick = 0:(npmax-1);
    set(o,'ytick',(0:npmax-1)+ 0.5);
    set(o,'yticklabel',ytick);
    % set(o,'ylim',[0 npmax]);
    clim([0,npmax])
    set(o,'ticklength',0)
    set(o,'fontsize',16,'fontweight','bold')
    colormap(pp.pp_colormap);
end

