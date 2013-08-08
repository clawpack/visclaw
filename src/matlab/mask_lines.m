function add_lines(level,slow,shigh)

% Internal Matlab routine for Clawpack graphics.

amrlines = get_lines;

if (level == 1)
  % Nothing to mask
  return;
end;

mask_level = level - 1;
while (isempty(amrlines{mask_level})) % no lines have been plotted at this level
  mask_level = mask_level-1;
  if (mask_level == 0)
    % There are no lines under this one to mask
    return;
  end;
end;

tol = 1e-6;
lines_to_mask = amrlines{mask_level};
for k = 1:length(lines_to_mask),
  ln = lines_to_mask(k);
  udata = get(ln,'UserData');
  sv = udata.s;
  nan_mask = sv > slow + tol & sv < shigh - tol;
  xdata = get(ln,'XData');
  xdata(nan_mask) = nan;
  set(ln,'XData',xdata);
end;
