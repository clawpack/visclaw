function underover_colorbar()
%
% UNDEROVER_COLORBAR constructs the colorbar to show under/overshoots
%
% UNDEROVER_COLORBAR can be called from an afterframe.m file to
% produced a colorbar associated with an under/overshoot colormap.
%
% This relies on the structure created using the user-defined function
% UNDEROVER.
%
% This should be used in conjunction with SETCOLORS.
%
% See also SETCOLORS, UNDEROVER.
%

uo = underover;   % User defined routine.

% Create an extended colormap
colormap([uo.color_under(:)'; uo.colormap; uo.color_over(:)']);

colorbar;

o = findobj('Tag','Colorbar');
n = length(colormap);

set(o,'ticklength',[0 0]);

set(o,'ytick',linspace(0,1,n+1));
yticklabel = cell(n + 1,1);
yticklabel{1} = 'undershoot';
yticklabel{2} = uo.value_lower;
yticklabel{end-1} = uo.value_upper;
yticklabel{end} = 'overshoot';
set(o,'yticklabel',yticklabel);
set(o,'fontsize',16,'fontweight','bold')
