function [linestyle,linecolors,markerstyle] = get_plotstyle(pstyle,len)

% Internal Matlab routine for Clawpack graphics

lstyle = {};
mstyle = {};
lcolors = {};
for i = 1:length(pstyle),
  [l,c,m,msg] = colstyle(pstyle{i});
  if (~isempty(msg))
    error(msg);
  end;
  if (isempty(l))
    lstyle{i} = 'none';
  else
    lstyle{i} = l;
  end;
  if (isempty(m))
    mstyle{i} = 'none';
  else
    mstyle{i} = m;
  end;

  % This is in case the user has set the plotstyle to just a color,
  % say 'b' or 'r', thinking that this will draw a line (as is the
  % default with the PLOT command.
  if (strcmp(lstyle{i},'none') & strcmp(mstyle{i},'none'))
    lstyle{i} = '-';
  end;

  if (isempty(c))
    lcolors{end+1} = 'b';
  else
    lcolors{end+1} = c;
  end;
end;

linestyle = set_length(lstyle,len);
markerstyle = set_length(mstyle,len);
linecolors = set_length(lcolors,len);
