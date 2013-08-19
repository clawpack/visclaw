%  SETPLOT2 sets user defined plotting parameters
%
%      User defined Matlab script for setting various Clawpack plotting
%      parameters.  This script is called by PLOTCLAW2.  A default
%      version of this script can be found in claw/matlab/setplot2.m and
%      copied to users working directory and modifed to set things up
%      differently.
%
%      Parameters that can be set with SETPLOT2
%
%        OutputFlag        - set to 'ascii' (default) to read ascii output
%                                from files fort.qXXXX where XXXX is Frame #
%                            or to 'hdf' to read hdf output files.
%                                from files fort.qXXXX.hdf
%                            set to 'aux' to read aux array values from
%                                fort.aXXXX instead of q from fort.qXXXX
%                                These files are created only if
%                                outaux = .true.  in out2.f
%
%        OutputDir         - set to '.' to read data from current working
%                                directory (default) or set to path
%                                to output directory.
%
%        PlotType          - type of plot to produce:
% 			    - 1 = pcolor on slices (with optional contours)
% 			    - 2 = contour lines in 2d on white slices
% 			    - 3 = Schlieren plot on slices
% 			    - 4 = scatter plot of q vs. r
%
%        mq                  - which component of q to plot
%        UserVariable        - Set to 1 to specify a user defined variable.
%        UserVariableFile    - name of m-file mapping data to q
%        MappedGrid          - set to 1 if mapc2p.m exists for nonuniform
%                              grid
%        Manifold            - set to 1 if mapc2m.m exists for manifold plot.
%        MaxFrames           - max number of frames
%        MaxLevels           - max number of AMR levels
%        PlotData            - Data on refinement level k is plotted only if
%                              PlotData(k) == 1
%        PlotGrid            - Plot grid lines on level k is PlotGrid(k) ~= 0
%        PlotGridEdges       - Plot 2d patch borders if PlotGridEdges(k) ~= 0
%        ContourValues       - Set to desired contour values, or [] for none
%        x0,y0               - center for scatter plots.
%        ScatterStyle        - symbols for scatter plot.
%        LineStyle           - same as ScatterStyle.
%        UserMap1d           - set to 1 if 'map1d' file exists.
%        UserColorMapping    - Use user-defined 'setcolors' function
%        ShowUnderOverShoots - Visualization for over/undershoots.
%
%      All parameters can be modified by typing 'k' at the PLOTCLAW2 prompt.
%
%      See also PLOTCLAW2, SetPlotGrid, setPlotGridEdges.


PlotType = 1;                % type of plot to produce:
			     % 1 = pseudo-color (pcolor)
			     % 2 = contour
			     % 3 = Schlieren
			     % 4 = scatter plot of q vs. r

mq = 1;                      % which component of q to plot
UserVariable = 0;            % set to 1 to specify a user-defined variable
UserVariableFile = ' ';      % name of m-file mapping data to q
MappedGrid = 0;              % set to 1 if mapc2p.m exists for nonuniform grid
Manifold = 0;
MaxFrames = 1000;            % max number of frames to loop over
MaxLevels = 6;               % increase if using amrclaw with more levels
PlotData =  [1 1 1 1 1 1];   % Data on refinement level k is plotted only if
			     % k'th component is nonzero
PlotGrid =  [0 0 0 0 0 0];   % Plot grid lines on each level?

PlotGridEdges =  [1 1 1 1 1 1];  % Plot edges of patches of each grid at
                                 % this level?

% ---------------------------------------------------------------------
% ContourValues is a vector of values used to draw contour lines.
% The valid settings for this parameter are identical to those used by the
% Matlab contour plotting routine.  See also CONTOUR.  In particular:
%   If ContourValues is the empty matrix, no contour lines will be drawn.
%   If ContourValues is a vector, these values will be used for contours.
%   If ContourValues is an integer, this number of levels will be drawn,
%        with values chosen based on the data.  (May not work well with
%        AMR data since different levels may be chosen on different grids.

ContourValues = [];

%---------------------------------

% for scatter plot (PlotType==4):
% The default is to plot q(i,j) vs. r(i,j) = (x(i,j)-x0)^2 + (y(i,j)-y0)^2
x0 = 0;
y0 = 0;

UserMap1d = 0;  % set to 1 and provide map1d.m file to specify a different
                % mapping of (x,y,q) to (r,q) for scatter plots.

ScatterStyle = setplotstyle('ro','bx','k.','rs','bv','k^');
%               determines symbol and color for plotting scatter data on
%               each refinement level.
