function colorbar_underover(under_label,over_label)
%
% COLORBAR_UNDEROVER constructs the colorbar to show under/overshoots
%
% COLORBAR_UNDEROVER can be called from an afterframe.m file to
% produced a colorbar associated with an under/overshoot colormap.
% Default labels 'undershoot' and 'overshoot' are used to label the
% under/overshoot regions of the colorbar.
%
% COLORBAR_UNDEROVER(under_label,over_label) uses user supplied labels.
%
% Example :  Provide labels which show the magnitude of the under/over
%            shoots :
%
%              under_label = sprintf('%3.1f - %7.1e',qlo,qlo-qmin);
%              over_label = sprintf('%3.1f + %7.1e',qhi,qmax-qhi);
%              colorbar_underover(under_label,over_label);
%
% COLORBAR_UNDEROVER makes a call to the user-defined function UNDEROVER.
%
% See also UNDEROVER.
%

% Number of bars in the color map used for the under/overshoot region.
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

set(o,'ticklength',0);

if (nargin == 0)
  under_label = 'undershoot';
  over_label = 'overshoot';
end;

% Fix the tick marks
set(o,'ytick',linspace(0,1,n+1));
yticklabel = cell(n + 1,1);
yticklabel{1} = under_label;
yticklabel{cm_buff+1} = uo.value_lower;
yticklabel{end-cm_buff} = uo.value_upper;
yticklabel{end} = over_label;
set(o,'yticklabel',yticklabel);
% set(o,'fontsize',16,'fontweight','bold')
