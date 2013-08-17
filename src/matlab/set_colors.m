function set_colors(p,x,y,z,q,colormapping)

% Internal Clawgraphics routine that is used to do the color mapping from
% q values to mesh cell colors in patches.

% ---------------------------------------------------------------------
switch  colormapping

% -------------------------------------------------------------
case 'default'

     % -------------------------------------------------------------
     % Scale into color map in usual way
     % -------------------------------------------------------------

     set(p,'CData',q);                % Data to use for coloring.
     set(p,'CDataMapping','scaled');  % Scale into current color map.
     set(p,'FaceColor','flat');       % Single color per cell


% -------------------------------------------------------------
case 'underover'

     % -------------------------------------------------------------
     % Color under/over shoots.
     % The user should set 'ShowUnderOverShoots' in setplot2.m or
     % setplot3.m and define function 'underover.m'
     % -------------------------------------------------------------

     cm_buff = 3;        % Number of buffer under/over color entries

     uo = underover();   % User-defined function

     nmax = length(uo.colormap);
     cm_extended = [kron(ones(cm_buff,1),uo.color_under(:)'); ...
                    uo.colormap; ...
		    kron(ones(cm_buff,1),uo.color_over(:)')];

     % Fix q so that floor for indexing works.  This also clamps
     % values in [qlo-tol,qlo] to qlo, and values in [qhi,qhi+tol]
     % to qhi.
     mfix = (uo.value_lower-uo.tol) <= q & q <= uo.value_lower;
     q(mfix) = uo.value_lower;
     mfix = uo.value_upper <= q & q <= (uo.value_upper + uo.tol);
     q(mfix) = uo.value_upper-1e-8; % So floor works

     % ----------------------------------------------------
     % Create index values in range [qlo,qhi] into
     % user-specified colormap
     % ----------------------------------------------------

     idx = 0*q + nan;     % This will replace the 'cdata' property
                          % in the patch handle 'p'.

     % Mask for values in the range [qlo, qhi].
     m0 = uo.value_lower <= q & q <= uo.value_upper;

     % map value_lower to 2 and value_upper to nmax+1
     slope = (q(m0) - uo.value_lower)/(uo.value_upper-uo.value_lower);
     idx(m0) = cm_buff + floor(1 + slope*(nmax-1));

     % Set under shoots to 1 and over shoots to nmax+2
     m_under = q <= uo.value_lower-uo.tol;
     idx(m_under) = 1;   % first index in cm_extended

     m_over = q >= (uo.value_upper + uo.tol);
     idx(m_over) = nmax + 2*cm_buff;   % last index of cm_extended

     % -----------------------
     % Modify patch handle
     % -----------------------

     % Color by indexing directly into the color map
     set(p,'CData',idx);

     % Retrieve FaceVertex data so we can set rgb triples directly
     fv_idx = get(p,'FaceVertexCData');

     if (sum(isnan(fv_idx)) > 0)
       error('setcolors : nans remain in index used for colormap');
     end;

     % Hardwire colors for the patch
     set(p,'FaceVertexCData',cm_extended(fv_idx,:));

     % Use 'flat' so that each mesh cell has single identifing color
     set(p,'FaceColor','flat');

case 'usercolormapping'
     setcolors(p,x,y,z,q);

case other
     error('set_colors : No valid color mapping choice was set');
end % end switch
