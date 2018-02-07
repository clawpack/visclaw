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
        mfix = (uo.value_lower-uo.tol_lower) <= q & q <= uo.value_lower;
        q(mfix) = uo.value_lower;
        mfix = uo.value_upper <= q & q <= (uo.value_upper + uo.tol_upper);
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
        m_under = q <= uo.value_lower-uo.tol_lower;
        idx(m_under) = 1;   % first index in cm_extended
        
        m_over = q >= (uo.value_upper + uo.tol_upper);
        idx(m_over) = nmax + 2*cm_buff;   % last index of cm_extended
        
        m_leftover = ~(m0 | m_under | m_over);
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
        
    case 'parallelpartitions'
        
        pp = parallelpartitions(q);
        npmax = pp.npmax;
        
        % Seed to use for random processor colormap.
        if (~isfield(pp,'pp_colormap'))
            s = pp.seed;
            ppcm = ppcolors(npmax,s);
        else
            ppcm = pp.pp_colormap;
            if (size(ppcm,1) ~= pp.npmax)
                error('set_colors: length(ppcm) ~= npmax')
            end
        end

        mpirank = getmpirank();  % mpirank for this patch        
        if (~isfield(pp,'plotq'))
            pp.plotq = ~isempty(pp.qcolors);
        end
        
        if (~pp.plotq)
            cm_extended = [ppcm; [1 1 1]];
            qcolors = mpirank+1 + zeros(size(q));            
            m = isnan(q);
            qcolors(m) = length(cm_extended);
        else
            % == NAN where processor colors should be used. 
            qcolors = pp.qcolors;  
            m = ~isnan(qcolors);
                        
            n = size(pp.colormap,1);
            
            qmin = pp.qmin;
            qmax = pp.qmax;            
            
            qm = qcolors(m);
            cidx = zeros(size(qm));
                        
            % Everything less than qmin will take processor color
            m1 = qm < qmin;
            cidx(m1) = mpirank + 1;
            
            % Everything between qmin and qmax, map linearly into 
            % pp.colormap.
            m2 = qmin <= qm & qm <= qmax;
            if (~isempty(qm))
                cidx(m2) = floor((n-1)/(qmax-qmin)*(qm(m2) - qmin)) + 1;
            end
            cidx(m2) = cidx(m2) + npmax;
            
            % Everything larger than qmax is a processor color
            m3 = qm > qmax;
            cidx(m3) = mpirank + 1;
            
            qcolors(m) = cidx;
            % qcolors(~m) = mpirank + 1;
            
            % NANs are colored white.
            qcolors(~m) = npmax + n + 1;

            
            w = [1 1 1]; 
            cm_extended = [ppcm;pp.colormap;w];

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
        end;
        
        % Hardwire colors for the patch
        % set(p,'FaceVertexCData',cm_extended(fv_idx,:));
        set(p,'FaceVertexCData',fv_idx);
        set(p,'cdatamapping','direct');
        
        % Use 'flat' so that each mesh cell has single identifing color
        set(p,'FaceColor','flat');
            
        set(gca,'clim',[pp.qmin, pp.qmax]);
        setopengl;
                        
    case 'usercolormapping'
        setcolors(p,x,y,z,q);
        
    case other
        error('set_colors : No valid color mapping choice was set');
end % end switch
