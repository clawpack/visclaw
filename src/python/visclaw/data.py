"""
Plotting Data Module

Contains the general class definition and the subclasses of the Clawpack
data objects specific to plotting.
"""
from __future__ import absolute_import
from __future__ import print_function
import os
import copy
import numpy as np
import re
import logging
import clawpack.clawutil.data as clawdata
import time

import clawpack.pyclaw.controller

# ============================================================================
#  Subclass ClawPlotData containing data for plotting results
# ============================================================================
class ClawPlotData(clawdata.ClawData):
    """ClawPlotData class

    Data subclass containing plot data.

    """

    # ========== Initialization routine ======================================
    def __init__(self, controller=None, file_format="ascii"):
        """Initialize a PlotData object

        """

        # Initialize the data object and read the data files
        super(ClawPlotData,self).__init__()

        # default values of attributes:

        if controller:
            controller.plotdata = self
            # inherit some values from controller
            self.add_attribute('rundir',copy.copy(controller.rundir))
            self.add_attribute('outdir',copy.copy(controller.outdir))
            if len(controller.frames)>0:
                for i,frame in enumerate(controller.frames):
                    self.framesoln_dict[str(i)] = frame
            self.add_attribute('format',copy.copy(controller.output_format))
            self.add_attribute('file_prefix',copy.copy(controller.output_file_prefix))
        else:
            self.add_attribute('rundir',os.getcwd())     # uses *.data from rundir
            self.add_attribute('outdir',os.getcwd())     # where to find fort.* files
            self.add_attribute('format',file_format)
            if file_format == "petsc":
                self.add_attribute('file_prefix','claw')
            else:
                self.add_attribute('file_prefix','fort')

        # This should eventually replace all need for recording the above
        # information
        self.add_attribute('output_controller', None)
        self.output_controller = clawpack.pyclaw.controller.OutputController(
                                           self.outdir, file_format=self.format)


        self.add_attribute('plotdir',os.getcwd())      # directory for plots *.png, *.html
        self.add_attribute('overwrite',True)           # ok to overwrite old plotdir?
        self.add_attribute('plotter','matplotlib')     # backend for plots
        self.add_attribute('msgfile','')               # where to write error messages
        self.add_attribute('verbose',True)             # verbose output?

        self.add_attribute('ion',False)                # call ion() or ioff()?

        self.add_attribute('printfigs',True)
        self.add_attribute('print_format','png')
        self.add_attribute('print_framenos','all')  # which frames to plot
        self.add_attribute('print_gaugenos','all')  # which gauges to plot
        self.add_attribute('print_fignos','all')    # which figures to plot each frame

        self.add_attribute('iplotclaw_fignos','all')    # which figures to plot interactively

        self.add_attribute('latex',True)                # make latex files for figures
        self.add_attribute('latex_fname','plots')       # name of latex file
        self.add_attribute('latex_title','Clawpack Results')
        self.add_attribute('latex_framesperpage','all') # number of frames on each page
        self.add_attribute('latex_framesperline',2)     # number of frames on each line
        self.add_attribute('latex_figsperline','all')   # number of figures on each line
        self.add_attribute('latex_makepdf',False)       # run pdflatex on latex file

        self.add_attribute('html',True)                # make html files for figures
        self.add_attribute('html_index_fname','_PlotIndex.html')   # name of html index file
        self.add_attribute('html_index_title','Plot Index')   # title at top of index page
        self.add_attribute('html_homelink',None)       # link to here from top of _PlotIndex.html
        self.add_attribute('html_movie','JSAnimation') # make html with java script for movie
        self.add_attribute('html_movie_width', 500)    # width of movie (not used?)
        self.add_attribute('html_movie_dpi', 100)      # dpi of movie

        self.add_attribute('html_eagle',False)         # use EagleClaw titles on html pages?

        self.add_attribute('kml',False)                # make kml plots and a kml file for figures
        self.add_attribute('kml_index_fname','_GoogleEarth')   # name of html index file
        self.add_attribute('kml_publish',None)
        self.add_attribute('kml_name',"GeoClaw")
        self.add_attribute('kml_starttime',None)
        self.add_attribute('kml_tz_offset',None)
        self.add_attribute('kml_time_scale',1.0) # Multiply by factor to get seconds
        self.add_attribute('kml_map_topo_to_latlong',None)
        self.add_attribute('kml_user_files',[])

        self.add_attribute('gif_movie',False)          # make animated gif movie of frames

        self.add_attribute('mp4_movie',False)         # make animated mp4 movie of frames
        self.add_attribute('movie_name_prefix', 'movie_')
        self.add_attribute('setplot',False)            # Execute setplot.py in plot routine

        self.add_attribute('mapc2p',None)              # function to map computational
                                        # points to physical


        self.add_attribute('beforeframe',None)         # function called before all plots
                                        # in each frame are done
        self.add_attribute('afterframe',None)          # function called after all plots
                                        # in each frame are done

        self.add_attribute('plotfigure_dict',{})
        try:
            from collections import OrderedDict   # new in Python 2.7
            d = OrderedDict()
        except:
            d = {}
        self.add_attribute('otherfigure_dict',d)

        self.add_attribute('framesoln_dict',{})        # dictionary for holding framesoln
                                        # objects associated with plots

        self.add_attribute('gaugesoln_dict',{})        # dictionary for holding gaugesoln
                                        # objects associated with plots

        self.add_attribute('save_frames',True)         # True ==> Keep a copy of any frame
                                        # read in.  False ==> Clear the frame
                                        # solution dictionary before adding
                                        # another solution

        self.add_attribute('save_figures',True)        # True ==> Keep a copy of and figure
                                        # created.  False ==> Clear the
                                        # figure dictionary before adding
                                        # another solution

        self.add_attribute('refresh_gauges',False)     # False ==> don't re-read gaugesoln if
                                        # already in gaugesoln_dict

        self.add_attribute('timeframes_framenos',None)
        self.add_attribute('timeframes_frametimes',None)
        self.add_attribute('timeframes_fignos',None)
        self.add_attribute('timeframes_fignames',None)



        self.add_attribute('gauges_gaugenos',None)
        self.add_attribute('gauges_fignos',None)
        self.add_attribute('gauges_fignames',None)

        # Parallel capabilities
        # Run multiple processess dividing up the frames that need to be plotted
        self.add_attribute('parallel', False)
        # Default to OMP_NUM_THREADS available if defined
        self.add_attribute('num_procs', None)
        self.add_attribute('proc_frames', None)
        self.add_attribute('_parallel_todo', None)


        self._next_FIG = 1000
        self._fignames = []
        self._fignos = []
        self._mode = 'unknown'
        self._figname_from_num = {}
        self._otherfignames = []


    def new_plotfigure(self, name=None, figno=None, type='each_frame'):
        """
        Create a new figure for Clawpack plots.
        If type='each_frame' it is a figure that will be plotted
        for each time frame.
        If type='multi_frame' it is a figure that will be plotted based on
        all the frames, such as x-t plots or time series. (Not yet implemented)
        """
        if (self._mode != 'iplotclaw') and (name in self._fignames):
            print('*** Warning, figure named %s has already been created' % name)
        if (self._mode != 'iplotclaw') and (figno in self._fignos):
            print('*** Warning, figure number %s has already been created' % figno)
        if figno is None:
            self._next_FIG += 1
            figno = self._next_FIG
        if name is None:
            name = "FIG%s" % figno
        if name in self._fignames:
            print("*** Error in new_plotfigure: Figure name already used... ",name)
            raise Exception("Figure name already used")
        elif figno in self._fignos:
            print("*** Error in new_plotfigure: Figure number already used... ",figno)
            raise Exception("Figure number already used")

        self._fignames.append(name)
        self._fignos.append(figno)
        plotfigure = ClawPlotFigure(name, figno, type, self)
        if not self.save_figures:
            self.plotfigure_dict.clear()
        self.plotfigure_dict[name] = plotfigure
        self._figname_from_num[figno] = name
        return plotfigure


    def getframe(self,frameno,outdir=None,refresh=False):
        """
        ClawPlotData.getframe:
        Return an object of class Solution containing the solution
        for frame number frameno.

        If refresh == True then this frame is read from the fort
        files, otherwise it is read from the fort files only if the
        the dictionary self.framesoln_dict has no key frameno.  If it does, the
        frame has previously been read and the dictionary value is returned.
        """

        from clawpack.pyclaw import solution

        framesoln_dict = self.framesoln_dict

        if 0:
            if outdir:
                key = (frameno, outdir)
            else:
                key = frameno
                outdir = self.outdir

        if outdir is None:
            outdir = self.outdir
        outdir = os.path.abspath(outdir)
        key = (frameno, outdir)

        if refresh or (key not in framesoln_dict):
            framesoln = solution.Solution(frameno,path=outdir,
                                          file_prefix=self.file_prefix,
                                          file_format=self.format)
            if not self.save_frames:
                framesoln_dict.clear()
            framesoln_dict[key] = framesoln
            if key != frameno:
                print('    Reading  Frame %s at t = %g  from outdir = %s' \
                    % (frameno,framesoln.t,outdir))
            else:
                print('    Reading  Frame %s at t = %g  ' \
                    % (frameno,framesoln.t))
        else:
            framesoln = self.framesoln_dict[key]

        return framesoln


    def clearfigures(self):
        """
        Clear all plot parameters specifying figures, axes, items.
        Does not clear the frames of solution data already read in.
        For that use clearframes.
        """

        self.plotfigure_dict.clear()
        self._fignames = []
        self._fignos = []
        self._next_FIG = 1000
        self._otherfignames = []


    def clearframes(self, framenos='all'):
        """
        Clear one or more frames from self.framesoln_dict.
        Need to add outdir option!
        """

        if isinstance(framenos, int):
            framenos = [framenos]  # turn into a list

        if framenos=='all':
            self.framesoln_dict.clear()
            print('Cleared all frames')
        else:
            for frameno in framenos:
                xxx = self.plotdata.framesoln_dict.pop(frameno,None)
                if xxx is None:
                   print('No frame data to clear for frame ',frameno)
                else:
                   print('Cleared data for frame ',frameno)


    def getgauge(self, gauge_id, outdir=None, verbose=True):
        r"""Read in the gauge labeled with `gaugeno` in path `outdir`

        :Note:
        The behavior of this function has changed to actually only read in the
        requested gauge id rather than all of the gauges.  The dictionary
        `gaugesoln_dict` remains the same.

        :Input:
         - *gauge_id* - (int) The gauge id of the gauge to be read in.
         - *outdir* - (path) Path to output directory containing gauge files.
           Defaults to this data object's `self.outdir`.
         - *verbose* - (bool) Verbose console output, default is `False`.

        :Output:
         - (clawpack.amrclaw.GaugeSolution) The read in gauge solution either
           from the `gaugeson_dict` or from file.  If something went wrong then
           the routine prints a warning and returns `None`.
        """

        # Construct path to file
        if outdir is None:
            outdir = self.outdir
        outdir = os.path.abspath(outdir)

        # Reread gauge data file
        key = (gauge_id, outdir)
        if self.refresh_gauges or (key not in self.gaugesoln_dict):

            try:

                # Read gauge solution:
                import clawpack.pyclaw.gauges as gauges

                self.gaugesoln_dict[key] = gauges.GaugeSolution(
                                           gauge_id=gauge_id, path=outdir)

                if verbose:
                    print("Read in gauge %s." % gauge_id)

            except Exception as e:
                import warnings
                warnings.warn(str(e))
                return None

        return self.gaugesoln_dict[key]


    def plotframe(self, frameno):
        from clawpack.visclaw import frametools
        frametools.plotframe(frameno, self)

    def printframes(self, verbose=True):
        #from clawpack.visclaw import frametools
        #frametools.printframes(self, verbose)
        print("*** printframes is deprecated.  Use plotpages.plotclaw_driver")
        print("*** for added capabilities.")
        raise DeprecationWarning("The method 'printframes' is deprecated.")

    def fignos(self):
        """
        Return a list of the figure numbers actually used.
        Useful in afterframe function for example to loop over all
        figures and do something.
        """
        return self._fignos

    def mode(self):
        """
        Return self._mode, which is set internally to
           'iplotclaw' if Iplotclaw is in use,
           'printframes' if printframes is being used
        Useful in afterframe function if you want to do different things
           for interactive or print modes.
        """
        return self._mode

    def iplotclaw(self):
        """
        Return True if interactive plotting with iplotclaw is being done.
        """
        return (self._mode == 'iplotclaw')


    def getfigure(self,figname):
        try:
            plotfigure = self.plotfigure_dict[figname]
        except:
            raise Exception('Error accessing plotfigure_dict[%s]' % figname)

        return plotfigure

    def getaxes(self,axesname,figname=None):
        found = True
        if not figname:
            found = False
            for fig in self._fignames:
                plotfigure = self.getfigure(fig)
                if axesname in plotfigure._axesnames:
                    if found == True: # already found!
                        print('*** Ambiguous... must specify figname')
                        print('    try getaxes(axesname, figname)')
                        return None
                    figname = fig
                    found = True
        if not found:
            print('*** No axes found with name = ',axesname)
            return None
        try:
            plotfigure = self.getfigure(figname)
            plotaxes = plotfigure.plotaxes_dict[axesname]
        except:
            print('*** Error accessing plotaxes[%s]' % axesname)
            print('*** figname = %s' % figname)
            return None
        return plotaxes

    def getitem(self,itemname,axesname=None,figname=None):
        found = True
        if not figname:
            # search over all figures looking for the item
            found = False
            for fign in self._fignames:
                plotfigure = self.getfigure(fign)
                if not axesname:
                    # search over all axes looking for the item
                    for axesn in plotfigure._axesnames:
                        plotaxes = self.getaxes(axesn,fign)
                        if itemname in plotaxes._itemnames:
                            if found == True: # already found!
                                print('*** Ambiguous... must specify figname and/or axesname')
                                print('    try getitem(itemname, axesname, figname)')
                                return None
                            axesname = axesn
                            figname = fign
                            found = True
                else:
                    # axesname was specified (but not figname)
                    plotaxes = self.getaxes(axesname,fign)
                    if itemname in plotaxes._itemnames:
                        if found == True: # already found!
                            print('*** Ambiguous... must specify figname and/or axesname')
                            print('    try getitem(itemname, axesname, figname)')
                            return None
                        figname = fign
                        found = True

        elif not axesname:
            # figname was specified but not axesname.
            # search over all axes looking for the item
            found = False
            plotfigure = self.getfigure(figname)
            for axesn in plotfigure._axesnames:
                plotaxes = self.getaxes(axesn,figname)
                if itemname in plotaxes._itemnames:
                    if found == True: # already found!
                        print('*** Ambiguous... must specify axesname')
                        print('    try getitem(itemname, axesname, figname)')
                        return None
                    axesname = axesn
                    found = True

        if not found:
            print('*** No item found with name = ',itemname)
            return None
        try:
            plotaxes = self.getaxes(axesname,figname)
            plotitem = plotaxes.plotitem_dict[itemname]
        except:
            print('*** Error accessing plotitem[%s]' % itemname)
            print('*** figname = ',figname)
            print('*** axesname = ',axesname)
            return None
        return plotitem


    def showitems(self):
        fignames = self._fignames
        print("\n\nCurrent plot figures, axes, and items:")
        print("---------------------------------------")
        for figname in fignames:
            plotfigure = self.getfigure(figname)
            s =  "  figname = %s, figno = %s" % (figname, plotfigure.figno)
            if not plotfigure._show:
                s = s + "  [Not showing]"
            print(s)
            axesnames = plotfigure._axesnames
            for axesname in axesnames:
                plotaxes = self.getaxes(axesname,figname)
                s =  "     axesname = %s, axescmd = %s" \
                       % (axesname, plotaxes.axescmd)
                if not plotaxes._show:
                    s = s + "  [Not showing]"
                print(s)
                for itemname in plotaxes._itemnames:
                    plotitem = self.getitem(itemname,axesname,figname)
                    plot_type = plotitem.plot_type
                    s =  "        itemname = %s,  plot_type = %s" \
                          % (itemname,plot_type)
                    if not plotitem._show:
                        s = s + "  [Not showing]"
                    print(s)
            print(" ")


    def getq(self,frameno):
        solution = self.getframe(frameno)
        patches = solution.patches
        if len(patches) > 1:
            print('*** Warning: more than 1 patch, q on patch[0] is returned')
        q = patches[0].q
        return q


    def new_otherfigure(self, name=None, fname=None):
        """
        Create a new figure for Clawpack plots.
        For figures not repeated each frame.
        """
        if (self._mode != 'iplotclaw') and (name in self._fignames):
            print('*** Warning, figure named %s has already been created' % name)

        if name is None:
            if fname is None:
                raise Exception("Need to provide name in new_otherfigure")
            else:
                name = fname
        if name in self._otherfignames:
            print("*** Error in new_otherfigure: Figure name already used... ",name)
            raise Exception("Figure name already used")

        self._otherfignames.append(name)
        otherfigure = ClawOtherFigure(name,self)
        self.otherfigure_dict[name] = otherfigure
        otherfigure.fname = fname
        return otherfigure

    def set_outdirs(self):
        """
        Make a list of all outdir's for all plotitem's in the order they
        are first used.
        """

        outdir_list = []
        for figname in self._fignames:
            plotfigure = self.plotfigure_dict[figname]
            if not plotfigure._show:
                continue  # skip to next figure
            for axesname in plotfigure._axesnames:
                plotaxes = plotfigure.plotaxes_dict[axesname]
                if not plotaxes._show:
                    continue  # skip to next axes
                for itemname in plotaxes._itemnames:
                    plotitem = plotaxes.plotitem_dict[itemname]
                    if not plotitem._show:
                        continue  # skip to next item
                    if plotitem.outdir is not None:
                        outdir = plotitem.outdir
                    else:
                        outdir = self.outdir
                    if outdir not in outdir_list:
                        outdir_list.append(outdir)

        self._outdirs = outdir_list
        return self

# ============================================================================
#  Subclass ClawPlotFigure containing data for plotting a figure
# ============================================================================
class ClawPlotFigure(clawdata.ClawData):
    """

    Data subclass containing plot data needed to plot a single figure.
    This may consist of several ClawPlotAxes objects.

    """

    # ========================================================================
    #  Initialization routine
    # ========================================================================
    def __init__(self, name, figno, fig_type, plotdata):
        """
        Initialize a ClawPlotFigure object
        """

        super(ClawPlotFigure, self).__init__()

        self._plotdata = plotdata           # parent ClawPlotData object
        self.add_attribute('name',name)
        self.add_attribute('figno',figno)
        self.add_attribute('figsize',None)
        self.add_attribute('facecolor',None)
        self.add_attribute('kwargs',{})
        self.add_attribute('clf_each_frame',True)
        self.add_attribute('clf_each_gauge',True)
        self._axesnames = []
        self.add_attribute('show',True)
        self._show = True
        self.add_attribute('plotaxes_dict', {})
        self.add_attribute('type',fig_type)   # = 'each_frame' or 'each_run' or 'each_gauge'
        self.add_attribute('use_for_kml',False)
        self.add_attribute('kml_gauge_name','Gauge')
        self.add_attribute('kml_dpi',200)
        self.add_attribute('kml_xlimits',None)
        self.add_attribute('kml_ylimits',None)
        self.add_attribute('kml_use_figure_limits',True)
        self.add_attribute('kml_tile_images',False)
        self.add_attribute('kml_colorbar',None)
        self.add_attribute('kml_use_for_initial_view',False)
        self.add_attribute('kml_show_figure',False)
        self.add_attribute('kml_maxlevel',20)
        self.add_attribute('kml_figsize',None)    # Figure size;  specify to get rid of aliasing
        self._next_AXES = 0

    def new_plotaxes(self, name=None, type='each_frame'):
        """
        Create a new axes that will be plotted in this figure.
        If type='each_frame' it is an axes that will be plotted
        for each time frame.
        If type='multi_frame' it is an axes that will be plotted based on
        all the frames, such as x-t plots or time series. (Not yet implemented)
        If type='empty' it is created without doing any plots using the
        pyclaw tools.  Presumably the user will create a plot within an
        afteraxes command, for example.
        """
        if name is None:
            self._next_AXES += 1
            name = "AXES%s" % self._next_AXES
        if name in self._axesnames:
            print('*** Warning, axes named %s has already been created' % name)

        if name not in self._axesnames:
            self._axesnames.append(name)
        plotaxes = ClawPlotAxes(name, self)
        self.plotaxes_dict[name] = plotaxes
        plotaxes.type = type
        return plotaxes

    def gethandle(self):
        _handle = getattr(self,'_handle',None)
        return _handle


# ============================================================================
#  Subclass ClawPlotAxes containing data for plotting axes within a figure
# ============================================================================
class ClawPlotAxes(clawdata.ClawData):
    """

    Data subclass containing plot data needed to plot a single axes.
    This may consist of several ClawPlotItem objects.

    """

    # ========================================================================
    #  Initialization routine
    # ========================================================================
    def __init__(self, name, plotfigure):
        """
        Initialize a ClawPlotAxes object
        """

        super(ClawPlotAxes, self).__init__()

        self._plotfigure = plotfigure                   # figure this item is on
        self._plotdata = plotfigure._plotdata           # parent ClawPlotData object

        self.add_attribute('name',name)
        self.add_attribute('title',name)
        self.add_attribute('title_with_t',True)  # creates title of form 'title at time t = ...'
        self.add_attribute('axescmd','subplot(1,1,1)')

        self.add_attribute('beforeaxes',None)
        self.add_attribute('afteraxes',None)
        self.add_attribute('xlimits',None)
        self.add_attribute('ylimits',None)
        self.add_attribute('skip_patches_outside_xylimits',None)
        self.add_attribute('scaled',False)   # true so x- and y-axis scaled same
        self.add_attribute('image',False)    # true so x- and y-axis scaled same
                                             # and plot bounds tight
        self.add_attribute('plotitem_dict', {})
        self.add_attribute('type','each_frame')
        self._itemnames = []
        self.add_attribute('show',True)
        self._show = True
        self._handle = None
        self._next_ITEM = 0
        self.add_attribute('figno', self._plotfigure.figno)

        # attributes for gauge plots
        self.add_attribute('time_label', 'time')  # for time axis in gauges
        self.add_attribute('time_label_fontsize', None)
        self.add_attribute('time_label_kwargs', {})  # kwargs for xlabel cmd
        self.add_attribute('time_scale', 1)  # multiplicative factor to rescale t
                                             # e.g. 1/3600. from sec to hours

        # recently added attributes:
        self.add_attribute('kwargs', {})
        self.add_attribute('grid', None) # True to add grid() command
        self.add_attribute('grid_kwargs', {}) # argument to grid() command
        self.add_attribute('title_fontsize', None)
        self.add_attribute('title_kwargs', {}) # e.g. to set color
        self.add_attribute('title_t_format', None) # format for t in title
        self.add_attribute('xticks_fontsize', None)
        self.add_attribute('xticks_kwargs', {}) # e.g. to set ticks,rotation
        self.add_attribute('yticks_fontsize', None)
        self.add_attribute('yticks_kwargs', {}) # e.g. to set ticks
        self.add_attribute('xlabel', None) # label for x-axis
        self.add_attribute('ylabel', None) # label for y-axis
        self.add_attribute('xlabel_fontsize', None)
        self.add_attribute('ylabel_fontsize', None)
        self.add_attribute('xlabel_kwargs', {})
        self.add_attribute('ylabel_kwargs', {})
        self.add_attribute('aspect', None)
        self.add_attribute('aspect_latitude', None)
        self.add_attribute('useOffset', None)


    def new_plotitem(self, name=None, plot_type=None):
        # Create a new entry in self.plotitem_dict

        if name is None:
            self._next_ITEM += 1
            name = "ITEM%s" % self._next_ITEM

        if name not in self._itemnames:
            self._itemnames.append(name)

        plotitem = ClawPlotItem(name, plot_type, plotaxes=self)

        self.plotitem_dict[name] = plotitem

        return plotitem

    def get_plotdata(self):
        plotdata = getattr(self,'_plotdata',None)
        return self._plotdata

    def get_plotfigure(self):
        plotfigure = getattr(self,'_plotfigure',None)
        return self._plotfigure

    def gethandle(self):
        _handle = getattr(self,'_handle',None)
        return self._handle

# ============================================================================
#  Subclass ClawPlotItem containing data for plotting a single object
# ============================================================================
class ClawPlotItem(clawdata.ClawData):
    """

    Data subclass containing plot data needed to plot a single object.
    This may be a single curve, set of points, contour plot, etc.

    """

    # ========================================================================
    #  Initialization routine
    # ========================================================================
    def __init__(self, name, plot_type, plotaxes):
        """
        Initialize a ClawPlotItem object
        """

        super(ClawPlotItem, self).__init__()


        self._plotaxes = plotaxes                       # axes this item is on
        self._plotfigure = plotaxes._plotfigure         # figure this item is on
        self._plotdata = plotaxes._plotfigure._plotdata           # parent ClawPlotData object

        try:
            num_dim = int(plot_type[0])   # first character of plot_type should be num_dim
        except:
            print('*** Error: could not determine num_dim from plot_type = ',plot_type)

        self.add_attribute('num_dim',num_dim)
        self.add_attribute('name',name)
        self.add_attribute('figno',plotaxes.figno)

        self.add_attribute('outdir',None)              # indicates data comes from
                                        #   self._plotdata.outdir

        self.add_attribute('plot_type',plot_type)
        self.add_attribute('plot_var',0)
        self.add_attribute('data_show',True)

        self.add_attribute('MappedGrid',None)          # False to plot on comput. patch even
                                        # if _plotdata.mapc2p is not None.

        self.add_attribute('mapc2p',None)              # function to map computational
                                    # points to physical (over-rides
                                    # plotdata.mapc2p if set for item


        self.add_attribute('afterpatch',None)           # function called after each patch is
                                        # plotted within each single plotitem.
        self.add_attribute('afteritem',None)           # function called after the item is
                                        # plotted for each frame

        self.add_attribute("show",True)                # False => suppress showing this item
        self._show = True               # Internal

        self._current_pobj = None

        self.add_attribute('params',{})  # dictionary to hold optional parameters

        if num_dim == 1:
            self.add_attribute('plotstyle','-')
            self.add_attribute('color',None)
            self.add_attribute('kwargs',{})
            amr_attributes = """show color kwargs data_show plotstyle""".split()
            for a in amr_attributes:
                self.add_attribute('amr_%s' % a, [])

            if plot_type == '1d_fill_between':
                zero_function = lambda current_data: 0.
                self.add_attribute('plot_var2',zero_function)
                self.add_attribute('fill_where',None)

            if plot_type == '1d_from_2d_data':
                self.add_attribute('map_2d_to_1d',None)
                self.add_attribute('amr_plotstyle',[])

        elif num_dim == 2:

            # default values specifying this single plot:
            self.add_attribute('plot_type',plot_type)
            self.add_attribute('celledges_show',0)
            self.add_attribute('celledges_color','k')
            self.add_attribute('celledges_linewidth',0.5)
            self.add_attribute('patch_bgcolor','w')
            self.add_attribute('patchedges_show',0)
            self.add_attribute('patchedges_color','k')
            self.add_attribute('patchedges_linewidth',0.8)
            self.add_attribute('add_colorbar',False)
            self.add_attribute('colorbar_shrink',None)
            self.add_attribute('colorbar_label',None)
            self.add_attribute('colorbar_ticks', None)
            self.add_attribute('colorbar_tick_labels',None)
            self.add_attribute('colorbar_extend',None)
            self.add_attribute('colorbar_kwargs',{})
            self.add_attribute('kwargs',{})
            amr_attributes = """celledges_show celledges_color 
              celledges_linewidth data_show patch_bgcolor patchedges_show 
              patchedges_color kwargs""".split()
            for a in amr_attributes:
                self.add_attribute('amr_%s' % a, [])

            if plot_type == '2d_pcolor':
                from clawpack.visclaw import colormaps
                self.add_attribute('pcolor_cmap',colormaps.yellow_red_blue)
                self.add_attribute('pcolor_cmin',None)
                self.add_attribute('pcolor_cmax',None)

            elif plot_type == '2d_imshow':
                from clawpack.visclaw import colormaps
                self.add_attribute('imshow_cmap',colormaps.yellow_red_blue)
                self.add_attribute('imshow_cmin',None)
                self.add_attribute('imshow_cmax',None)
                self.add_attribute('imshow_norm', None)
                self.add_attribute('imshow_alpha', None)


            elif plot_type in ['2d_contour', '2d_contourf']:
                self.add_attribute('contour_nlevels',20)
                self.add_attribute('contour_levels',None)
                self.add_attribute('contour_min',None)
                self.add_attribute('contour_max',None)
                self.add_attribute('contour_show',1)
                self.add_attribute('contour_colors','k')
                self.add_attribute('contour_cmap',None)
                amr_attributes = """show colors cmap data_show""".split()
                for a in amr_attributes:
                    self.add_attribute('amr_contour_%s' % a, [])


                if plot_type == '2d_contourf':
                    self.add_attribute('fill_cmap',None)
                    self.add_attribute('fill_cmin',None)
                    self.add_attribute('fill_cmax',None)
                    self.add_attribute('fill_colors',None)
                    # Note either fill_cmap or fill_colors must be None

            elif plot_type == '2d_schlieren':
                from clawpack.visclaw import colormaps
                self.add_attribute('schlieren_cmap',colormaps.schlieren_grays)
                self.add_attribute('schlieren_cmin',None)
                self.add_attribute('schlieren_cmax',None)

            elif plot_type == '2d_patch':
                self.add_attribute('max_density',None)
                self.celledges_show = True
                self.patchedges_show = True

            elif plot_type == '2d_quiver':
                self.add_attribute('quiver_var_x',None)
                self.add_attribute('quiver_var_y',None)
                self.add_attribute('quiver_coarsening',1)
                self.add_attribute('quiver_key_show',False)
                self.add_attribute('quiver_key_label_x',0.15)
                self.add_attribute('quiver_key_label_y',0.95)
                self.add_attribute('quiver_key_units','')
                self.add_attribute('quiver_key_scale',None)
                self.add_attribute('quiver_key_kwargs',{})
                amr_attributes = """coarsening key_show key_label_x key_label_y
                         key_scale key_kwargs data_show""".split()
                for a in amr_attributes:
                    self.add_attribute('amr_quiver_%s' % a, [])

            elif plot_type == '2d_hillshade':
                self.add_attribute('hillshade_cmap','gray')
                self.add_attribute('hillshade_vertical_exaggeration',1)
                self.add_attribute('hillshade_azimuth_degree',315)
                self.add_attribute('hillshade_altitude_degree',45)
                self.add_attribute('hillshade_latlon', False)

            else:
                 print('*** Warning 2d plot type %s not recognized' % plot_type)

        elif num_dim == 3:
            raise NotImplementedError('ClawPlotItem not yet set up for num_dim = 3')

        else:
            raise Warning('Unrecognized plot_type in ClawPlotItem')


    def getframe(self,frameno,refresh=False):
        """
        ClawPlotItem.getframe:
        Return an object of class Solution containing the solution
        for frame number frameno.

        If refresh == True then this frame is read from the fort
        files, otherwise it is read from the fort files only if the
        the dictionary self.framesoln_dict has key frameno.  If it does, the
        frame has previously been read and the dictionary value is returned.
        """

        plotdata = self._plotdata
        outdir = self.outdir
        framesoln = plotdata.getframe(frameno, outdir,refresh=refresh)

        return framesoln


    def getgauge(self,gauge):
        """
        ClawPlotItem.getgauge:
        Return an object of class GaugeSolution containing the solution
        for gauge number gaugeno.

        If self.refresh_gauges == True then this gauge is read from the
        fort.gauge file, otherwise it is read only if the
        the dictionary self.gaugesoln_dict has no key gaugeno.  If it does, the
        gauge has previously been read and the dictionary value is returned.
        """

        plotdata = self._plotdata
        outdir = self.outdir
        gaugesoln = plotdata.getgauge(gauge, outdir)

        return gaugesoln


# ============================================================================
#  Subclass ClawOtherFigure containing data for plotting a figure
# ============================================================================
class ClawOtherFigure(clawdata.ClawData):
    """

    Data subclass containing plot data needed to plot a single figure.
    For figures that are not produced each frame.

    """

    # ========================================================================
    #  Initialization routine
    # ========================================================================
    def __init__(self, name, plotdata):
        """
        Initialize a ClawOtherFigure object
        """

        super(ClawOtherFigure, self).__init__()

        self._plotdata = plotdata           # parent ClawPlotData object
        self.add_attribute('name',name)
        self.add_attribute('fname',None)            # name of png file
        self.add_attribute('makefig',None)          # function invoked to create figure
