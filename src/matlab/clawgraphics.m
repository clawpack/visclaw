% Routines for plotting data output from Clawpack package
%
% Basic Clawpack plotting routines and options.
%
%      plotclaw1              - plot 1d results
%      plotclaw2              - plot 2d results
%      plotclaw3              - plot 3d results
%      setplot1               - script for setting parameters for 1d plots
%      setplot2               - script for setting parameters for 2d plots
%      setplot3               - script for setting parameters for 3d plots
%      setplot                - help on using SETPLOT<N>
%      readamrdata            - reads output files produced by Clawpack.
%      plotframe1ez           - functional form of plotframe1.
%      setplotstyle           - sets symbols and colors for line/scatter plots
%      queryframe             - queries user for next frame information
%      getlegendinfo          - returns legend information on line plots.
%      printgif               - prints a gif file from current figure
%      printjpg               - prints a jpg file from current figure
%      makeframegif           - print current figure to file frame0000N.gif
%      makeframejpg           - print current figure to file frame0000N.jpg
%
% Data analysis routines (for use with UserVariable = 1)
%      pressure               - returns pressure given input data (gamma law)
%      xvelocity              - returns x velocity
%      yvelocity              - returns y velocity
%      zvelocity              - returns z velocity
%      mach                   - return mach number.
%
% General graph properties for 2d and 3d plots.
%
%      Contourlines
%      ------------
%      drawcontourlines       - draws contour lines on slices.
%      showcontourlines       - shows contour lines
%      hidecontourlines       - hides contour lines
%      setcontourlineprops    - sets properties for contour lines
%
%      Gridlines
%      ---------
%      showgridlines          - shows computational grid
%      hidegridlines          - hides computational grid
%      setgridlinecolor       - sets color of grid lines
%
%      Patchborders
%      ------------
%      showpatchborders       - shows patch borders
%      hidepatchborders       - hide patch borders
%      setpatchbordercolor    - sets color of patch borders.
%      setpatchborderprops    - set patch border line properties
%
%      Mesh
%      ----
%      showmesh               - shows a coarsened mesh on specified levels
%      hidemesh               - hides a coarsened mesh on specified levels
%
%      Slices
%      ------
%      showslices             - shows slices/manifold
%      hideslices             - hides slices/manifold
%      setslicecolor          - sets color of slice/manifold
%      setslicealpha          - set transparency value of slice/manifold
%
%      Mapped grids
%      ------------
%      getblocknumber         - get block number for multi-block calculations.
%
%      Colormaps
%      ---------
%      setcolors              - gives user control over how colors are set
%      yrbcolormap            - yellow/red/blue colormap
%      redwhite               - red/white colormap
%      rybcolormap            - red/yellow/blue colormap
%      underover              - Modify colormap to visualize under/over shoots
%      colorbar_underover     - Colorbar for visualzing under/over shoots in data
%
%      Misc
%      ------
%      chombo                 - help for graphing using Chombo hdf5 output.
%      setopengl              - Sets OpenGL renderer needed for alpha < 1.
%
% 2d specific graphics routines
%
%      showlevels             - shows specified levels (2d only)
%      hidelevels             - hides specified levels (2d only)
%      projectcontours        - projects contour lines to user-specified plane.
%
% 3d specific graphics routines
%
%      Slices
%      ------
%      sliceloop              - loop over slices on 3d plots.
%
%      Iso-surfaces
%      ------------
%      surfloop               - loop over isosurfaces
%      showsurfs              - shows isosurfaces created with ISOSURFVALUES
%      hidesurfs              - hides isosurfaces created with ISOSURFVALUES
%      showsurflevels         - show isosurfaces at specified AMR levels
%      hidesurflevels         - hide isosurfaces at specified AMR levels
%      reducesurf             - reduces number of faces on isosurface.
%      showsurfmesh           - shows isosurface mesh
%      hidesurfmesh           - hides isosurface mesh
%      setsurfalpha           - sets isosurface transparency value
%      setsurfcolor           - sets isosurface color
%
%      Cubes (3d patch borders)
%      ------------------------
%      showcubes              - shows 3d amr patch cube borders
%      hidecubes              - hides 3d amr patch cube borders
%      setcubecolor           - sets colors of 3d patch cube borders
%
%      Misc
%      ----
%      setviews               - sets pre-defined viewing angles
%
% Type 'help' on any one of the individual topics above for more help.
%
