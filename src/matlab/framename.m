function fstr = framename(Frame,filename,ext,plotdir)
%FRAMENAME creates a filename based on Frame number and format
%
% FSTR = FRAMENAME(FRAME,FILENAME,PRTFORMAT) returns a string with the
% <filename>.<prtformat>.  It is assumed that FILENAME is a string with
% several trailing '000' that will be replaced with the integer FRAME.
%
% FSTR = FRAMENAME(...,PLOTDIR) passes in an optional argument specifying an
% output directory which is pre-pended to the file name.
%
% This file name can be then passed to the PRINT command to print a figure
% window.
%
% Example :
% 
% Frame = 4;
% fname = 'spiral0000';
% ext = 'png';
% plotdir = 'plots';
% fstr = framename(Frame,fname,ext,dir);
% print('-dpng',fstr);
%
% See also PRINT.
%

if (nargin < 4)
  plotdir = './';
end

% add a trailing backslash to PLOTDIR
if (strcmp(plotdir(end),'/') == 0)
  plotdir = sprintf('%s/',plotdir);
end;

str = num2str(Frame);
n1 = length(str);
n2 = length(filename);
filename(n2-n1+1:n2) = str;

fstr = sprintf('%s%s.%s',plotdir,filename,ext);
