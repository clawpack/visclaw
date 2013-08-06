%     ChomboClaw is a software framework which combines the high-level
%     adaptive mesh refinement capabilities available in Chombo with the
%     numerical integration routines of Clawpack.
%
%     For more information on Chombo, see
%
%         http://seesar.lbl.gov/anag/chombo/index.html
%
%     For more information on ChomboClaw, contact Donna Calhoun at
%     calhoun@amath.washington.edu
%
%     ChomboClaw produces output files using the HDF5 file format developed
%     the NCSA (see http://hdf.ncsa.uiuc.edu/HDF5).  The latest release of
%     Matlab, Version 6.5.1, release 13, has several routines for handling
%     HDF5 formatted files.  In the Clawpack graphics, we have added
%     routines which use these features to read the output from ChomboClaw
%     and produce data structures usuable by the Claw Graphics commands.
%
%     To plot output from a ChomboClaw run, there are only three parameters
%     that the user will need to set.  These paramters can be set in the
%     SETPLOT2 or SETPLOT3 files.  These parameters are :
%
%     OutputFlag        - set to 'Chombo' for ChomboClaw output
%
%     plot_prefix       - set to prefix of file name of ChomboClaw
%                         output. For example, if a typical ChomboClaw file is
%                         called plotNEW0010.2d.hdf5, then the prefix is
%                         OutputPrefix = 'plotNEW'. By default, this prefix
%                         is 'pltstate'.  This will typically be the
%                         same as claw.plot_prefix.
%
%     plot_interval     - set this to an integer specifying the plot
%                         interval.  This value will typically equal
%                         claw.plot_interval, set in the ChomboClaw input
%                         file.  Other useful values are multiples of the
%                         this value.
%
%
%    See also SETPLOT, SETPLOT2, SETPLOT3, PLOTCLAW2, PLOTCLAW3.
%
