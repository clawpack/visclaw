function vis_levels = get_levelvis(slice)

% Internal Matlab routine for Clawpack graphics

vis_levels = zeros(length(slice),1);
for level = 1:length(slice),
  pvec = slice{level};
  vis = false;
  for k = 1:length(pvec),
    p = pvec(k);
    vis = vis | strcmp(get(p,'Tag'),'on');
  end;
  vis_levels(level) = vis;
end;

vis_levels = find(vis_levels > 0);
