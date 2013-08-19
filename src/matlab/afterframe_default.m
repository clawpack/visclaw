% This file will be called after all other plotting items are done.
% The user can undo these plotting characteristics in a local
% copy of their afterframe.m file.


% Patch borders should have thicker lines.
setpatchborderprops(1:MaxLevels,'linewidth',2);

% undo with showgridlines
hidegridlines;

%undo with showpatchborders
hidepatchborders;

% Set preset views.
setviews;
