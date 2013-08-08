function hout = makelegend(varargin)

% MAKELEGEND makes a legend for amr scatter and line plots.
%
%   MAKELEGEND, by itself, adds legend to the current plot, using symbols
%   specified in the ScatterStyle or LineStyle parameters.  Legend labels
%   will be 'Level 1', 'Level 2', etc.
%
%   MAKELEGEND(LEVEL_LABELS) takes labels from the cell array LABELS instead of
%   using the default 'Level 1', 'Level 2', or 'Level 3' labels.
%
%   MAKELEGEND(LEVEL_LABELS,OTHER_HANDLES,OTHER_LABELS) add legend entries
%   for additional line plots whose handles are in vector OTHER_HANDLES and
%   whose labels are in OTHER_LABELS.
%
%   MAKELEGEND(OTHER_HANDLES,OTHER_LABELS) uses default labels for level
%   data.
%
%   H = MAKELEGEND(....) returns a handle to the legend axis.
%
%   Example :
%
%   % In afterframe.m, with PlotType = 4 (2d/3d scatter plot)
%
%        % Plot 1d data from directory results1d.
%        [amrdata1d,t1d] = readamrdata(1,Frame,'./results1d/');
%        [q1d,x1d,p1] = plotframe1ez(amrdata1d,mq,'b-');
%        hold off;
%
%        labels = {'2d data (level 1)', '2d data (level 2)', '2d data (level 3)'};
%        makelegend(labels,p1,{'1d results'});
%
%   See also LEGEND.

level_labels_in = {};
other_labels = {};
other_hdls = [];
args_read = 1;
if (nargin > 0)
  tok = varargin{args_read};
  if (iscell(tok))
    tok1 = tok{1};
  else
    tok1 = tok;
  end;
  if (ischar(tok1))
    if (iscell(tok))
      level_labels_in = tok;
    else
      level_labels_in = {tok};
    end;
  end;
  args_read = args_read + 1;
  if (args_read <= nargin)
    tok = varargin{args_read};
    keyboard;
    if (iscell(tok))
      other_hdls = tok;
    else
      other_hdls = {tok};
    end;
    args_read = args_read + 1;
    tok = varargin{args_read};
    if (iscell(tok))
      other_labels = tok;
    else
      other_labels = {tok};
    end;
  end;
end;

% Okay, we have all the arguments...

amrlines = get_lines;

phdl = [];
for level = 1:length(amrlines),
  svec = amrlines{level};
  if (~isempty(svec))
    if (level <= length(level_labels_in))
      level_labels{level} = level_labels_in{level};
    else
      level_labels{level} = sprintf('Level %d',level);
    end;
    phdl(end+1) = svec(1);
  end;
end;
phdl = [phdl,other_hdls{:}];

labels = {level_labels{:},other_labels{:}};

h = legend(phdl,labels);

if (nargout == 1)
  hout = h;
end;
