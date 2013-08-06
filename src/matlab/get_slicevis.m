function [vis_slices] = get_slicevis(sdir)

% Internal Matlab routine for Clawpack graphics

slices = get_slices(sdir);

% If any patch, at any level is 'on', then this is a visible slice.

vis_slices = zeros(length(slices),1);
for n = 1:length(slices),
  slice = slices{n};
  vis_levels = zeros(length(slice),1);
  for level = 1:length(slice),
    pvec = slice{level};
    vis = false;
    for k = 1:length(pvec),
      p = pvec(k);
      vis = vis | strcmp(get(p,'Visible'),'on');
    end;
    vis_levels(level) = vis;
  end;
  vis_slices(n) = any(vis_levels);
end;

vis_slices = find(vis_slices);
