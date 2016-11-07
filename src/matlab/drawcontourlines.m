function drawcontourlines(v,varargin)

% DRAWCONTOURLINES draws contour lines.
%
%
%     DRAWCONTOURLINES(V,MBLOCK,SDIR,SNUM) draw contour lines at levels V
%     on slices xSliceCoords(SNUM), ySliceCoords(SNUM)
%     or zSliceCoords(SNUM), depending on value SDIR ('x','y',or 'z').
%     Set MBLOCK == TRUE
%
%     DRAWCONTOURLINES(V,MBLOCK,SDIR) draws contour lines on all slices in
%     direction SDIR.
%
%     DRAWCONTOURLINES(V), draws contour lines on all slices in all
%     directions.
%
%     V is anything that is valid for Matlab's contour plotter. If
%     V is a scalar, then V contour lines will be automically chosen
%     and drawn on each specified slice.  Note that the values of the
%     contour lines in this case will be independently chosen, and
%     so will not match up across AMR patches, or at slice intersections.
%     If V is a vector of length N, then N contour levels at levels
%     specified in V will be chosen.  To plot a single contour line
%     at level C, set V = [C C].
%
%     DRAWCONTOURLINES(...,MBLOCK) assumes that we are in a multi-block
%     situation and so should not mask coordinates that overlap in 
%     computational space.  
% 
%     DRAWCONTOURLINES(...) removes any existing contour lines on specified
%     slices before plotting new lines specified in V.
%
%     See also SHOWCONTOURLINES, HIDECONTOURLINES.

% This logic needs some work ...
if (length(varargin) == 0)
    sdirs = {'x', 'y','z'};
    mblock = false;
else
    if (islogical(varargin{1}))
        % Assume the format is : 
        % drawcontourlines(cv,mblock);
        mblock = varargin{1};
        if (length(varargin) == 1)
            sdirs = {'x','y','z'};
            snum_in = [];
        else
            sdirs = {varargin{2}};
            if (length(varargin) == 3)
                snum_in = varargin{3};
            else
                snum_in = [];
            end
        end
    else        
        sdirs = {varargin{1}};
        if (length(varargin) == 2)
            snum_in = varargin{2};
        else
            snum_in = [];
        end
    end
end
    

for idir = 1:length(sdirs),
    sdir = sdirs{idir};
    slices = get_slices(sdir);
    if (isempty(snum_in))
        snum = 1:length(slices);
    end
    for ns = 1:length(snum),
        n = snum(ns);
        if (n < 1 || n > length(slices))
            continue
        end
        slice = slices{n};
        for level = 1:length(slice),
            pvec = slice{level};
            for k = 1:length(pvec);
                p = pvec(k);
                udata = get(p,'UserData');
                delete(udata.contourLines);
                [xc_like, yc_like, zc_like] = ...
                    get_xyzlike(udata.xc,udata.yc,udata.zc,sdir);
                c = contourc(yc_like,zc_like,udata.q,v);
                udata.contourLines = create_clines(c,udata.sval,...
                    sdir,udata.mappedgrid,udata.manifold,udata.blockno);
                set(p,'UserData',udata);
                set_cline_visibility(p);
            end
        end
        % This is called here separately because this routine might
        % be called directly by the user and not while patches are 
        % being added. 
        if (~mblock)
            mask_patches_all(slice);  % To mask any contourlines.
        end
    end
end
