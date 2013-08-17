function underover_colorbar(under_label,over_label)
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

cm_buff = 3;

uo = underover;   % User defined routine.

% Create an extended colormap
cm_extended = [kron(ones(cm_buff,1),uo.color_under(:)'); ...
               uo.colormap; ...
	       kron(ones(cm_buff,1),uo.color_over(:)')];

colormap(cm_extended);

colorbar;

o = findobj('Tag','Colorbar');
n = length(colormap);

set(o,'ticklength',[0 0]);

if (nargin == 0)
  under_label = 'undershoot';
  over_label = 'overshoot';
end;

set(o,'ytick',linspace(0,1,n+1));
yticklabel = cell(n + 1,1);
yticklabel{1} = under_label;
yticklabel{cm_buff+1} = uo.value_lower;
yticklabel{end-cm_buff} = uo.value_upper;
yticklabel{end} = over_label;
set(o,'yticklabel',yticklabel);
set(o,'fontsize',16,'fontweight','bold')
