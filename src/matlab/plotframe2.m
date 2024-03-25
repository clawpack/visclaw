%
% PLOTFRAME2 plots data from a single Clawpack output file.
%
%    PLOTFRAME2 is called from PLOTCLAW2, the driver script for Clawpack
%    graphics.  PLOTFRAME2 uses parameters, defined in the user's
%    workspace, usually in the SETPLOT2 script, to determine what kind of
%    plot to create, and various other plotting options.
%
%    See SETPLOT for a complete list of the parameters that the user can
%    set.
%
%    There are two basic types of plots available.  These are
%
%         Surface plots : 2d plots of the data.  This data may be viewed as
%         a manifold, if desired.
%
%         Scatter plots : Spherically symmetric data is plotted as a
%         function of a 1d variable, usually the distance from a fixed point
%         (x0,y0).  The result is a line-type plot of points representing the
%         data.
%
%    See SETPLOT, PLOTCLAW2, MANIFOLD.

if (~exist('amrdata','var'))
    error('*** plotframe2 : ''amrdata'' does not exist;  Call readamrdata or plotclaw2');
end

if isempty(amrdata)
    fprintf('\n');
    fprintf('Frame %d (%s) does not exist\n',Frame,outputflag);
    fprintf('\n');
    return;
end

fprintf('\n');
fprintf('Frame %d at time = %g\n',Frame,t);

if exist('beforeframe','file')
    % make an m-file with this name for any other commands you
    % want executed before drawing each frame, for example
    % if you want to use axes to specify exactly where the
    % plot will be in the window, aspect ratio, etc.
    beforeframe;
end

set_value('forestclaw','ForestClaw',0);

% Do some checking to make sure input is right..
if (PlotType <= 3)
    
    set_value('mappedgrid','MappedGrid',0);
    if (mappedgrid == 1 && ~exist('mapc2p','file'))
        error('*** MappedGrid = 1 but no ''mapc2p'' function was found.');
    end
    
    set_value('manifold','Manifold',0);
    if (manifold == 1 && ~exist('mapc2m','file'))
        error('*** Manifold = 1, but no ''mapc2m'' function was found.');
    end
    
    if (manifold == 1)
        set_value('view_arg','UserView',3);
    else
        set_value('view_arg','UserView',2);
    end
    
    set_value('underoverflag','ShowUnderOverShoots',0);
    if (underoverflag == 1 && ~exist('underover','file'))
        error(['*** ShowUnderOverShoots = 1, but no ''underover'' ',...
            'function was found.']);
    end
    
    set_value('plotparallelpartitions','PlotParallelPartitions',0);
    set_value('plotblockcolors','PlotBlockColors',0);

    set_value('usercolormapping','UserColorMapping',0);
    if (usercolormapping == 1 && ~exist('setcolors','file'))
        error(['*** UserColorMapping = 1, but no ''setcolors'' ',...
            'function was found.']);
    end
    
    if underoverflag == 1
        colormapping = 'underover';
    elseif plotparallelpartitions == 1
        colormapping = 'parallelpartitions';
    elseif plotblockcolors == 1
        colormapping = 'blockcolors';
    elseif (usercolormapping == 1)
        colormapping = 'usercolormapping';
    else
        colormapping = 'default';
    end
    
    set_value('cvalues','ContourValues',[]);
    if (length(cvalues) == 1 && length(amrdata) > 1)
        fprintf('\n');
        fprintf(' *** Warning: Contour values will be chosen independently\n');
        disp(' *** on each mesh patch. Set ContourValues to a vector of values');
        disp(' *** to insure contour lines match across mesh boundaries.');
    end
    
    
    if (PlotType == 2)
        if (isempty(cvalues))
            disp(' ');
            disp(' *** Warning : You have specified PlotType == 2, but have');
            disp(' *** not set any contour values. Set ContourValues to a ');
            disp(' *** vector of values or integer (number of contour lines). ');
        end
    end
    
    
    if (PlotType == 3)
        % Change color map for schlieren plot
        % colormap(flipud(gray(2048)).^5)
        colormap(flipud(gray(2048)).^10)
        
        if (~isempty(cvalues))
            fprintf('\n');
            fprintf(' *** Warning : ContourValues is set to a non-empty matrix.\n');
            fprintf(' *** Schlieren data will be contoured.\n');
        end
    end
    
    xscoords = [];
    yscoords = [];
    zscoords = 0;
    
    sliceCoords = {xscoords, yscoords, zscoords};
    sdir = {'x','y','z'};
    
    % Stored in UserData of current figure (i.e. gcf);
    clear_amrplot;
    create_amrplot(MaxLevels,xscoords, yscoords, zscoords);
    newplot;  % Use this to deal with any hold on/ hold off issues.
    
end % end of input checking for PlotType <= 3

if PlotType == 4
    % -------------
    % Scatter plots
    % -------------
    
    view_arg = 2;
    
    set_value('usermap1d','UserMap1d',0);
    if (usermap1d == 1)
        if (~exist('map1d','file'))
            error('*** You have set UserMap1d=1, but no ''map1d'' function was found');
        end
    else
        if ((~exist('x0','var') || ~exist('y0','var')))
            error(['*** plotframe2 : (x0,y0) must be defined before you\n',...
                '*** can do a line or scatter plot, or set UserMap1d and create\n',...
                '*** a function ''map1d''.']);
        end
    end
    
    set_value('mappedgrid','MappedGrid',0);
    
    if (exist('ScatterStyle','var'))
        pstyle = ScatterStyle;
    elseif (exist('LineStyle','var'))
        pstyle = LineStyle;
    else
        error([' *** plotframe2 : Set either ''ScatterStyle'' or ',...
            '''LineStyle''.']);
    end
    
    if (~iscell(pstyle))
        error(['*** plotframe2 : ScatterStyle or LineStyle must be',...
            'cell matrices.  Use ''setplotstyle'' to set either of these ',...
            'variables']);
    end
    
    [linestyle,linecolors,markerstyle] = get_plotstyle(pstyle,MaxLevels);
    
    clear_amrplot;
    create_amrplot(MaxLevels);
    newplot;   % deals with some hold on/off issues...
    
end  % end of input checking for PlotType == 4

if (PlotType == 5)
    set_value('mappedgrid','MappedGrid',0);
    if (mappedgrid == 1 && ~exist('mapc2p','file'))
        error('*** MappedGrid = 1 but no ''mapc2p'' function was found.');
    end
    
    set_value('manifold','Manifold',0);
    if (manifold == 1 && ~exist('mapc2m','file'))
        error('*** Manifold = 1, but no ''mapc2m'' function was found.');
    end
    set_value('view_arg','UserView',3);
end

qmin = [];
qmax = [];
ncells = zeros(maxlevels,1);

%=============================================
% MAIN LOOP ON GRIDS FOR THIS FRAME:
%=============================================

ngrids = length(amrdata);  % length of structure array
for ng = 1:ngrids
    
    gridno = amrdata(ng).gridno;
    blockno = amrdata(ng).blockno;   % == 0 if there is only one block
    level = amrdata(ng).level;
    if (forestclaw)
        level = level + 1;   % ForestClaw levels start at 0
    end
    
    % if we're not plotting data at this level, skip to next grid
    if (PlotData(level) == 0)
        continue;
    end
    
    % Set block number for multi-block calculations.
    set_blocknumber(blockno);
    if (forestclaw)
        mpirank = amrdata(ng).mpirank;
        set_mpirank(mpirank);
    else
        set_mpirank(0);
    end
    
    mx = amrdata(ng).mx;
    my = amrdata(ng).my;
    
    xlow = amrdata(ng).xlow;
    ylow = amrdata(ng).ylow;
    
    dx = amrdata(ng).dx;
    dy = amrdata(ng).dy;
    
    xedge = xlow + (0:mx)*dx;
    yedge = ylow + (0:my)*dy;
    
    xcenter = xedge(1:mx) + dx/2;
    ycenter = yedge(1:my) + dy/2;
    
    % for compatibility with old matlab41/plotframe2 convention:
    x = xcenter;
    y = ycenter;
    
    % read q data:
    data = amrdata(ng).data;
    
    
    data = data';
    
    if (UserVariable == 1)
        % User has supplied a function to convert original q variables to
        % the variable which is to be plotted, e.g. Mach number, entropy.
        qdata = feval(UserVariableFile,data);
        q = reshape(qdata,mx,my);
    else
        q = reshape(data(:,mq),mx,my);
    end
    
    amrdata(ng).q = q;
    
    % q must be permuted so that it matches the dimensions of xcm,ycm,zcm
    % created by meshgrid.
    if (PlotType == 3)
        % Scheieren plot;  we plot the gradient, not the values.
        [qx,qy] = gradient(q,dx,dy);
        qs = sqrt(qx.^2 + qy.^2);
        qmesh = qs';
    else
        qmesh = q';
    end
    
    % minimum over all grids at this time, but not necessarily on slice
    % shown.
    qmin = min([qmin,min(q(:))]);
    qmax = max([qmax,max(q(:))]);
    
    % keep count of how many cells at this refinement level:
    if length(ncells) < level
        ncells(level) = 0;
    end
    ncells(level) = ncells(level) + mx*my;
    
    % -----------------------------------------------
    % plot commands go here
    if PlotType <= 3
        
        % Add amr patch of manifold into current plot.
        if (forestclaw)
            sval = -level + 1;  % Subtract one so that levels correspond to levels
        else
            sval = level;
        end
        zedge = [sval sval];
        zcenter = [sval sval];
        sdir = 'z';
        snum = 1;   % only one slice in 2d plot
        % only mask patches underneath if we are plotting a Manifold, or
        % using ForestClaw
        if (forestclaw)
            maskflag = 0;
        else
            maskflag = (manifold == 1);
        end
        add_patch2slice(sdir,sval,snum,xcenter,ycenter,zcenter, ...
            xedge,yedge,zedge,qmesh,level,cvalues,mappedgrid,manifold,...
            maskflag,ng,blockno,colormapping);
    end  % end of plotting for PlotType == 3
    
    if (PlotType == 4)
        % 1d Line plots
        
        [xcm,ycm] = meshgrid(xcenter,ycenter);
        
        if (usermap1d == 1)
            % Users should call mapc2p from inside of map1d.
            [rvec,qvec] = map1d(xcm,ycm,qmesh);
            [rs,cs] = size(rvec);
            [rq,cq] = size(qvec);
            if (cs > 1 || cq > 1)
                error(['plotframe2 : map1d can only return single columns vectors ',...
                    'for s or q']);
            end
        else
            if (mappedgrid == 1)
                [xpm,ypm] = mapc2p(xcm,ycm);
                r = sqrt((xpm - x0).^2 + (ypm - y0).^2);
            else
                r = sqrt((xcm-x0).^2 + (ycm - y0).^2);
            end
            rvec = reshape(r,numel(r),1);
            qvec = reshape(qmesh,numel(r),1);
        end
        
        add_line2plot(rvec,qvec,level,markerstyle{level},...
            linecolors{level},linestyle{level});
        
    end % end of plotting for PlotType == 4
    
    if (PlotType == 5)
        if (manifold == 1)
            [xpcenter,ypcenter] = mapc2m(xcenter,ycenter);
        else
            xpcenter = xcenter;
            ypcenter = ycenter;
        end
        h = surf(xpcenter,ypcenter,q);
    end
    
    if exist('aftergrid','file')
        % make an m-file with this name for any other commands you
        % want executed at the end of drawing each grid
        aftergrid;
    end
    
end % loop on ng (plot commands for each grid)
%=============================================

% Set user-defined variables from setplot2.m :

% add title and labels:
if UserVariable == 1
    str = sprintf('%s at time %8.4f',UserVariableFile,t);
    title(str,'fontsize',15);
else
    str = sprintf('q(%d) at time %8.4f',mq,t);
    title(str,'fontsize',15);
end

if (PlotType <= 3)
    setPlotGrid(PlotGrid);
    setPlotGridEdges(PlotGridEdges);
    if (PlotType == 2)
        setslicecolor('w');
    end
    if (manifold == 0 && view_arg == 2)
        % To really make sure we get a 2d view and can see all levels.
        set(gca,'ZLimMode','auto');
        zlim = get(gca,'zlim');
        % Increase it sligtly to make sure that we can see all the patches
        % plotted at the different z levels. 
        % Also, make sure the zero level is visible (so user can add
        % curves, etc to plot).
        zlim = [min(zlim)-0.001 0+0.001];
        set(gca,'zlim',[-maxlevels-1,0]);
    end
    xlabel('x')
    ylabel('y')
end

% Set view point
view(view_arg);

afterframe_default;

if exist('afterframe','file')
    % make an m-file with this name for any other commands you
    % want executed at the end of drawing each frame
    % for example to change the axes, or add a curve for a
    % boundary
    
    afterframe;
end
