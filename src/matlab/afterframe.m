%AFTERFRAME
% 
% The commands in this file will be executed after each plot is created.
% 
% Example:
% axis([-1 1 -1 1]);      % Set the axis limits
% daspect([1 1 1]);       % Set the aspect ratio
% 
% colormap(jet);
% 
% showpatchborders;       % Show outlines of AMR patch borders
% showgridlines(1:2);     % Show gridlines on level 1 and 2 grids
% 
% cv = linspace(-1,1,21); % Values for contour levels
% cv(cv == 0) = [];
% drawcontourlines(cv);   % add contour lines to a plot
% 
% caxis([-1 1]);          % Set the color axis
% 
% shg;                    % Bring figure window to the front
% 
% fstr = framename(Frame,'frame0000','png','_plots');
% print('-dpng',fstr);       % Create .png file of figure.
% 
% clear afterframe;
%
% See also AFTERGRID.
