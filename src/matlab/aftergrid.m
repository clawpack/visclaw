%AFTERGRID
% 
% The commands in this file will be executed after each grid of data is
% plotted.  For single grid calculations, this is equivalent to the
% AFTERFRAME file.  When plotting AMR results, this will be called after
% each grid is plotted, whereas AFTERFRAME is only called once the entire
% plot is complete. 
% 
% Example:
% % To pause after plotting each grid to manipulate the data 
% keyboard;
% 
% Example:
% % To label each grid with its gridnumber:
% 
% text(mean(xcenter),mean(ycenter),num2str(gridno))
%
% See also AFTERFRAME.
