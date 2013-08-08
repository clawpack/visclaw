function mask_patches_all(slice)

% Internal Clawpack Graphics routine.

% This routine goes through and masks all patches,
% once the slice has been setup.

% First, lets figure out which levels are visible.

vis_levels = get_levelvis(slice);

% Now, level vis_level(l+1) should mask vis_level(l)

for l = 1:length(vis_levels),
  level = vis_levels(l);
  pvecl = slice{level};
  reset_level(pvecl);
  if (l < length(vis_levels))
    pvecu = slice{vis_levels(l+1)};
    mask_patches2(pvecl,pvecu);
  end;
end;
