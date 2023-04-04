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
        if ~isfield(uo,'tol_lower')
            uo.tol_lower = uo.tol;
        end
        if ~isfield(uo,'tol_upper')
            uo.tol_upper = uo.tol;
        end
        
        nmax = length(uo.colormap);
        cm_extended = [kron(ones(cm_buff,1),uo.color_under(:)'); ...
            uo.colormap; ...
            kron(ones(cm_buff,1),uo.color_over(:)')];
        
        % Fix q so that floor for indexing works.  This also clamps
        % values in [qlo-tol,qlo] to qlo, and values in [qhi,qhi+tol]
        % to qhi.
        mfix = (uo.value_lower-uo.tol_lower) <= q & q <= uo.value_lower;
        q(mfix) = uo.value_lower;
        mfix = uo.value_upper <= q & q <= (uo.value_upper + uo.tol_upper);
        q(mfix) = uo.value_upper-0.0*uo.tol_upper; % So floor works
        
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
        m_under = q < (uo.value_lower-uo.tol_lower);
        idx(m_under) = 1;   % first index in cm_extended
        
        m_over = q > (uo.value_upper + uo.tol_upper);
        idx(m_over) = nmax + 2*cm_buff;   % last index of cm_extended
        
        m_leftover = ~m0 & ~m_under & ~m_over;
        idx(m_leftover) = -1;
        
        % -----------------------
        % Modify patch handle
        % -----------------------
        
        % Color by indexing directly into the color map
        set(p,'CData',idx);
        
        % Retrieve FaceVertex data so we can set rgb triples directly
        fv_idx = get(p,'FaceVertexCData');
        
        if (~isfield(uo,'color_nan'))
            color_nan = [1 1 1]*0.9;   % Should allow background to show through
        else
            color_nan = uo.color_nan;
        end
        cm_extended = [cm_extended; color_nan];

        % Set index to last entry in the colormap.
        fv_idx(fv_idx < 0) = length(cm_extended);        
                
        % Hardwire colors for the patch
        set(p,'FaceVertexCData',cm_extended(fv_idx,:));
        
        % Use 'flat' so that each mesh cell has single identifing color
        set(p,'FaceColor','flat');
        
    case {'parallelpartitions', 'blockcolors'}
        
        pp = parallelpartitions(q);
        npmax = pp.npmax;
        
        % Seed to use for random processor colormap.
        if (~isfield(pp,'pp_colormap'))
            error(['parallelpartitions : Supply pp color map ',...
                'field pp_colormap. Hint : use pp_colors']);
        end           
        ppcm = pp.pp_colormap;
        if (size(ppcm,1) ~= pp.npmax)
            error('set_colors: length(ppcm) ~= npmax')
        end

        % 'mpirank' should be renamed to something more generic
        % since we will use it for both parallel partitions
        % and block partitions.
        if strcmp(colormapping,'parallelpartitions') == 1
            mpirank = getmpirank();  % mpirank for this patch        
        elseif strcmp(colormapping,'blockcolors') == 1
            mpirank = getblocknumber();
        end

        % Does the user want to plot true colors for q within a range? 
        if (~isfield(pp,'plotq'))
            error('Parallelpartition : Supply plotq field (T/F)')
        end
        
        if (~pp.plotq)
            % Just show parallel partitions - no q values.
            % use white for any nan values
            cm_extended = [ppcm; [1 1 1]];

            % Color index has to start at 0
            qcolors = mpirank + 1 + zeros(size(q));            
            m = isnan(q);
            qcolors(m) = length(cm_extended);
        else
            % Show q in colormap within a range.
                        
            % Dimensions mx x my
            qcolors = pp.qcolors;
            m = ~isnan(qcolors);

            % Dimensions mx*my x 1
            qm = qcolors(m);
            cidx = zeros(size(qm));

            qmin = pp.qmin;
            qmax = pp.qmax;
            if pp.invert
                qm(qm < qmin(1)) = qmin(1);
                qm(qm > qmax(2)) = qmax(2);
                m_proc_color = qmin(2) < qm & qm < qmax(1);
                m_q{1} = qmin(1) <= qm & qm <= qmin(2);
                m_q{2} = qmax(1) <= qm & qm <= qmax(2);
            else
                qmin = pp.qmin;
                qmax = pp.qmax;
                m_proc_color = qmin <= qm & qm <= qmax;
                m_q = qm < qmin | qm > qmax;
            end

            % Indices that should use proc colormap
            cidx(m_proc_color) = mpirank + 1;

            % Color map to be used for Q
            n = size(pp.colormap,1);
            
            % Indices that use  q colormap
            if (~isempty(qm))
                if ~pp.invert
                    cidx(m_q) = floor((n-1)/(qmax-qmin)*(qm(m_q) - qmin)) + 1;
                    cidx(m_q) = cidx(m_q) + npmax;
                else
                    cidx(m_q{1}) = floor((n-1)/(qmin(2)-qmin(1))*(qm(m_q{1}) - qmin(1))) + 1;
                    cidx(m_q{2}) = floor((n-1)/(qmax(2)-qmax(1))*(qm(m_q{2}) - qmax(1))) + 1;
                    for i = 1:2
                        cidx(m_q{i}) = cidx(m_q{i}) + npmax;
                    end
                end
            end

            if sum(cidx == 0) > 0
                fprintf("Found %d zeros out of %d in cidx\n",sum(cidx == 0),length(cidx));
                error('set_colors : Missing indices in cidx')
            end

               
            % Set colors to direct index into colormap.
            qcolors(m) = cidx;

                        
            % NANs are colored white.
            qcolors(~m) = npmax + n + 1;

            w = [1 1 1]; 
            cm_extended = [ppcm;...
                           pp.colormap;...
                           w];
        end
        
        % -----------------------
        % Modify patch handle
        % -----------------------
        
        % Color by indexing directly into the color map
        set(p,'CData',qcolors);
        
        % Retrieve FaceVertex data so we can set rgb triples directly
        fv_idx = get(p,'FaceVertexCData');
        
        if (sum(isnan(fv_idx)) > 0)
            error('setcolors : nans remain in index used for colormap');
        end
        
        % Hardwire colors for the patch
        if min(fv_idx(:)) < 1 || max(fv_idx(:)) > length(cm_extended)
            error("set_colors : fv_idx is too large");
        end
        set(p,'FaceVertexCData',cm_extended(fv_idx,:));
        set(p,'cdatamapping','direct');
        
        % Use 'flat' so that each mesh cell has single identifing color
        set(p,'FaceColor','flat');
           
        setopengl;
                        
    case 'usercolormapping'
        setcolors(p,x,y,z,q);
        
    case other
        error('set_colors : No valid color mapping choice was set');
end % end switch
