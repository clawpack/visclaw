"""
Plotting Data Module

Contains the general class definition and the subclasses of the Clawpack 
data objects specific to plotting.
"""
import os
import copy
import re
import logging
from clawdata import Data, ClawData


# ============================================================================
#  Subclass ClawPlotData containing data for plotting results
# ============================================================================
class ClawPlotData(Data):
    """ClawPlotData class
    
    Data subclass containing plot data.

    """

    # ========== Initialization routine ======================================
    def __init__(self, data_files=[], controller=None):
        """Initialize a PlotData object
        
        Accepts a list of data_files to be read into and instantiate into one
        ClawPlotData object.  An empty object can be created by not passing 
        anything in for the data_file_list
        """
        plot_attrs = ['rundir','plotdir','outdir','overwrite','plotter',
                           'msgfile','printfig_format','afterframe',
                           'beforeframe','mapc2p',
                           'html_framenos','html_fignos','html_fignames',
                           'ndim','clear_figs', 'setplot', 'eagle',
                           'plotitem_dict', 'html_movies', 'params']

        # Initialize the data object and read the data files
        super(ClawPlotData,self).__init__(plot_attrs)

        # default values of attributes:

        if controller:
            controller.plotdata = self
            # inherit some values from controller
            self.rundir = copy.copy(controller.rundir)
            self.outdir = copy.copy(controller.outdir)
        else:
            self.rundir = os.getcwd()     # uses *.data from rundir
            self.outdir = os.getcwd()     # where to find fort.* files

        self.format = 'ascii'

        self.plotdir = os.getcwd()      # directory for plots *.png, *.html
        self.overwrite = True           # ok to overwrite old plotdir?
        self.plotter = 'matplotlib'     # backend for plots
        self.msgfile = ''               # where to write error messages
        self.verbose = True             # verbose output?

        self.ion = False                # call ion() or ioff()?

        self.user = Data()              # for user to pass things into
                                        # afterframe, for example
					# Deprecated.

        self.printfigs = True 
        self.print_format = 'png'     
        self.print_framenos = 'all'  # which frames to plot
        self.print_gaugenos = 'all'  # which gauges to plot
        self.print_fignos = 'all'    # which figures to plot each frame

        self.iplotclaw_fignos = 'all'    # which figures to plot interactively

        self.latex = True                # make latex files for figures
        self.latex_fname = 'plots'       # name of latex file
        self.latex_title = 'Clawpack Results'       
        self.latex_framesperpage = 'all' # number of frames on each page
        self.latex_framesperline = 2     # number of frames on each line
        self.latex_figsperline = 'all'   # number of figures on each line
        self.latex_makepdf = False       # run pdflatex on latex file

        self.html = True                # make html files for figures
        self.html_index_fname = '_PlotIndex.html'   # name of html index file
        self.html_index_title = 'Plot Index'   # title at top of index page
        self.html_homelink = None       # link to here from top of _PlotIndex.html
        self.html_movie = True          # make html with java script for movie
        self.html_eagle = False         # use EagleClaw titles on html pages?

        self.gif_movie = False          # make animated gif movie of frames


    #    self.clear_figs = True          # give clf() command in each figure
                                        # before plotting each frame

        self.setplot = False            # Execute setplot.py in plot routine
    #    self.setplot_caller = None      # Set before calling setplot

        self.mapc2p = None              # function to map computational
	                                # points to physical


        self.beforeframe = None         # function called before all plots 
                                        # in each frame are done
        self.afterframe = None          # function called after all plots 
                                        # in each frame are done

        self.plotfigure_dict = {}  
        self.otherfigure_dict = {}  

        self.framesoln_dict = {}        # dictionary for holding framesoln
                                        # objects associated with plots

        self.gaugesoln_dict = {}        # dictionary for holding gaugesoln
                                        # objects associated with plots
                                        
        self.save_frames = True         # True ==> Keep a copy of any frame
                                        # read in.  False ==> Clear the frame
                                        # solution dictionary before adding
                                        # another solution

        self.save_figures = True        # True ==> Keep a copy of and figure
                                        # created.  False ==> Clear the 
                                        # figure dictionary before adding
                                        # another solution

        self.refresh_frames = False     # False ==> don't re-read framesoln if 
                                        # already in framesoln_dict

        self.refresh_gauges = False     # False ==> don't re-read gaugesoln if 
                                        # already in gaugesoln_dict


        self._next_FIG = 1000
        self._fignames = []
        self._fignos = []
        self._mode = 'unknown'
        self._figname_from_num = {}
        self._otherfignames = []

        #if data_file_list is not None:
        if len(data_files) > 0:
            # values in data files may overwrite some default values
            # or set parameter values in params dictionary
            for data_file in data_files:
                self.read(data_file)

    def new_plotfigure(self, name=None, figno=None, type='each_frame'):
        """
        Create a new figure for Clawpack plots.  
        If type='each_frame' it is a figure that will be plotted 
	for each time frame.
        If type='multi_frame' it is a figure that will be plotted based on
	all the frames, such as x-t plots or time series. (Not yet implemented)
        """
        if (self._mode != 'iplotclaw') and (name in self._fignames):
            print '*** Warning, figure named %s has already been created' % name
        if (self._mode != 'iplotclaw') and (figno in self._fignos):
            print '*** Warning, figure number %s has already been created' % figno
        if figno is None:
            self._next_FIG += 1
            figno = self._next_FIG
        if name is None:
            name = "FIG%s" % figno
        if name in self._fignames:
            print "*** Error in new_plotfigure: Figure name already used... ",name
            raise Exception("Figure name already used")
        elif figno in self._fignos:
            print "*** Error in new_plotfigure: Figure number already used... ",figno
            raise Exception("Figure number already used")

        self._fignames.append(name)
        self._fignos.append(figno)
        plotfigure = ClawPlotFigure(name, figno, type, self)
        if not self.save_figures:
            self.plotfigure_dict.clear()
        self.plotfigure_dict[name] = plotfigure
        self._figname_from_num[figno] = name
        return plotfigure


    def getframe(self,frameno,outdir=None):
        """
        ClawPlotData.getframe:
        Return an object of class Solution containing the solution
        for frame number frameno.

        If self.refresh_frames == True then this frame is read from the fort
        files, otherwise it is read from the fort files only if the
        the dictionary self.framesoln_dict has no key frameno.  If it does, the
        frame has previously been read and the dictionary value is returned.
        """

        from pyclaw import solution

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

        if self.refresh_frames or (not framesoln_dict.has_key(key)):
            try:
                framesoln = solution.Solution(frameno,path=outdir,format=self.format)
            except:
                print '*** Error reading frame in ClawPlotData.getframe'
                raise
                return
            if not self.save_frames:
                framesoln_dict.clear()
            framesoln_dict[key] = framesoln
            if key != frameno:
                print '    Reading  Frame %s at t = %g  from outdir = %s' \
                    % (frameno,framesoln.t,outdir)
            else:
                print '    Reading  Frame %s at t = %g  ' \
                    % (frameno,framesoln.t)
        else:
            framesoln = self.framesoln_dict[key]

        return framesoln
        
    def gettime(self,frameno,outdir='./',format='ascii'):
        r"""Fetch time from solution corresponding to frame number in outdir
        
        This method only works for ascii and petsc formatted files
        """

        if format=='petsc':
            format_module = __import__('petclaw.io.%s' % format, fromlist=['petclaw','io'])
        else:
            format_module = __import__('pyclaw.io.%s' % format, fromlist=['pyclaw','io'])
        format_read_t = getattr(format_module, 'read_%s_t' % format)
        t,meqn,ngrids,maux,ndim = format_read_t(frameno,path=outdir)
        return t

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


    def clearframes(self, framenos='all'):
        """
        Clear one or more frames from self.framesoln_dict.
        Need to add outdir option!
        """

        if isinstance(framenos, int):
            framenos = [framenos]  # turn into a list

        if framenos=='all':
            self.framesoln_dict.clear()
            print 'Cleared all frames'
        else:
            for frameno in framenos:
                xxx = self.plotdata.framesoln_dict.pop(frameno,None)
                if xxx is None:
                   print 'No frame data to clear for frame ',frameno
                else:
                   print 'Cleared data for frame ',frameno


    def getgauge(self, gaugeno, outdir=None):
        """
        ClawPlotData.getgauge:
        Return an object of class GaugeSolution containing the solution
        for gauge number gaugeno.

        If self.refresh_gauges == True then this gauge is read from the
        fort.gauge file, otherwise it is read only if the
        the dictionary self.gaugesoln_dict has no key gaugeno.  If it does, the
        gauge has previously been read and the dictionary value is returned.
        """

        gaugesoln_dict = self.gaugesoln_dict

        if outdir is None:
            outdir = self.outdir
        outdir = os.path.abspath(outdir)
        key = (gaugeno, outdir)

        if self.refresh_gauges or (not gaugesoln_dict.has_key(key)):
            try:
                gauges = self.read_gauges(outdir)
            except:
                print '*** Error reading gauges in ClawPlotData.getgauge'
                print '*** outdir = ', outdir
                print '*** thisdir = ', thisdir
                raise
                return

            try:
                for (k,v) in gauges.iteritems():
                    gaugesoln_dict[(k, outdir)] = v
            except:
                raise("*** Problem setting gaugesoln_dict in getgauge")

            #print '    Read all gauge data from %s/fort.gauge' % outdir

        try:
            gaugesoln = gaugesoln_dict[key]
        except:
            print "*** Cannot find key = ",key
            print "***   in gaugesoln_dict = ",gaugesoln_dict
            raise("*** Problem getting gaugesoln in getgauge")
                

        return gaugesoln

    def read_gauges(self, outdir='.'):
        """
        Read the gauge output in file fort.gauge in the directory specified by
        outdir.
    
        Returns a dictionary *gauges* with an entry for each gauge number.
        Each entry is an object of class GaugeSolution
    
        """
    
        import os
        import numpy as np
        from matplotlib.mlab import find
        from visclaw import gaugetools
        from StringIO import StringIO
    
        fname = outdir + '/fort.gauge'
        if not os.path.isfile(fname):
            print "*** Gauge file not found: ",fname
            gauges = {}

        print '    Reading gauge data from ',fname
        try:
            gdata = np.loadtxt(fname)
        except:
            try:
                print "*** Warning: incomplete last line, computation may "
                print "*** still be in progress "
                gdata_lines = open(fname,'r').read()
                gdata_end = gdata_lines.rfind('\n',-200,-1)
                gdata_file = StringIO(gdata_lines[:gdata_end+1])
                gdata = np.loadtxt(gdata_file)
            except:
                print "*** Problem reading file ",fname
                #print "*** Possibly an incomplete last line if computation is still in progress"
                raise Exception("Problem reading fort.gauge")
                gauges = {}

        gaugeno = np.array(gdata[:,0], dtype=int)
        level = np.array(gdata[:,1], dtype=int)
        t = gdata[:,2]
        q = gdata[:,3:]  # all remaining columns are stored in q
    
        
        setgauges = gaugetools.read_setgauges(datadir=outdir)
    
        gauges = {}
        gaugenos = set(gaugeno)   # reduces to unique elements
        for n in gaugenos:
            n = int(n)
            gauges[n] = GaugeSolution()
            gauges[n].gaugeno = n
            nn = find(gaugeno==n)
            gauges[n].level = level[nn]
            gauges[n].t = t[nn]
            gauges[n].q = q[nn,:]
    
            # Locations:
            try:
                gauges[n].x = setgauges.x[n]
                gauges[n].y = setgauges.y[n]
                gauges[n].t1 = setgauges.t1[n]
                gauges[n].t2 = setgauges.t2[n]
            except:
                print "*** Could not extract gauge locations for gaugeno = ",n
    
        print '    Found gauge numbers: ',gauges.keys()
        return gauges
    


    def plotframe(self, frameno):
        from visclaw import frametools
        frametools.plotframe(frameno, self)
        
    def printframes(self, verbose=True):
        #from visclaw import frametools
        #frametools.printframes(self, verbose)
        print "*** printframes is deprecated.  Use plotpages.plotclaw_driver"
        print "*** for added capabilities."
        
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
            print '*** Error accessing plotfigure_dict[%s]' % figname
            return None
        return plotfigure

    def getaxes(self,axesname,figname=None):
        found = True
        if not figname:
            found = False
            for fig in self._fignames:
                plotfigure = self.getfigure(fig)
                if axesname in plotfigure._axesnames:
                    if found == True: # already found!
                        print '*** Ambiguous... must specify figname'
                        print '    try getaxes(axesname, figname)'
                        return None
                    figname = fig
                    found = True
        if not found:
            print '*** No axes found with name = ',axesname
            return None
        try:
            plotfigure = self.getfigure(figname)
            plotaxes = plotfigure.plotaxes_dict[axesname]
        except:
            print '*** Error accessing plotaxes[%s]' % axesname
            print '*** figname = %s' % figname
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
                                print '*** Ambiguous... must specify figname and/or axesname'
                                print '    try getitem(itemname, axesname, figname)'
                                return None
                            axesname = axesn
                            figname = fign
                            found = True
                else:
                    # axesname was specified (but not figname)
                    plotaxes = self.getaxes(axesname,fign)
                    if itemname in plotaxes._itemnames:
                        if found == True: # already found!
                            print '*** Ambiguous... must specify figname and/or axesname'
                            print '    try getitem(itemname, axesname, figname)'
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
                        print '*** Ambiguous... must specify axesname'
                        print '    try getitem(itemname, axesname, figname)'
                        return None
                    axesname = axesn
                    found = True

        if not found:
            print '*** No item found with name = ',itemname
            return None
        try:
            plotaxes = self.getaxes(axesname,figname)
            plotitem = plotaxes.plotitem_dict[itemname]
        except:
            print '*** Error accessing plotitem[%s]' % itemname
            print '*** figname = ',figname
            print '*** axesname = ',axesname
            return None
        return plotitem


    def showitems(self):
        fignames = self._fignames
        print "\n\nCurrent plot figures, axes, and items:"
        print "---------------------------------------"
        for figname in fignames:
            plotfigure = self.getfigure(figname)
            s =  "  figname = %s, figno = %s" % (figname, plotfigure.figno)
            if not plotfigure._show: 
                s = s + "  [Not showing]"
            print s
            axesnames = plotfigure._axesnames
            for axesname in axesnames:
                plotaxes = self.getaxes(axesname,figname)
                s =  "     axesname = %s, axescmd = %s" \
                       % (axesname, plotaxes.axescmd)
                if not plotaxes._show: 
                    s = s + "  [Not showing]"
                print s
                for itemname in plotaxes._itemnames:
                    plotitem = self.getitem(itemname,axesname,figname)
                    plot_type = plotitem.plot_type
                    s =  "        itemname = %s,  plot_type = %s" \
                          % (itemname,plot_type)
                    if not plotitem._show: 
                        s = s + "  [Not showing]"
                    print s
            print " "


    def getq(self,frameno):
        solution = self.getframe(frameno)
        grids = solution.grids
        if len(grids) > 1:
            print '*** Warning: more than 1 grid, q on grid[0] is returned'
        q = grids[0].q
        return q


    def new_otherfigure(self, name=None, fname=None):
        """
        Create a new figure for Clawpack plots.  
        For figures not repeated each frame.
        """
        if (self._mode != 'iplotclaw') and (name in self._fignames):
            print '*** Warning, figure named %s has already been created' % name

        if name is None:
            if fname is None:
                raise Exception("Need to provide name in new_otherfigure")
            else:
                name = fname
        if name in self._otherfignames:
            print "*** Error in new_otherfigure: Figure name already used... ",name
            raise Exception("Figure name already used")

        self._otherfignames.append(name)
        otherfigure = ClawOtherFigure(name,self)
        self.otherfigure_dict[name] = otherfigure
        return otherfigure



# ============================================================================
#  Subclass ClawPlotFigure containing data for plotting a figure
# ============================================================================
class ClawPlotFigure(Data):
    """
    
    Data subclass containing plot data needed to plot a single figure.
    This may consist of several ClawPlotAxes objects.

    """

    # ========================================================================
    #  Initialization routine
    # ========================================================================
    def __init__(self, name, figno, type, plotdata):
        """
        Initialize a ClawPlotFigure object
        """

        attributes = ['name','figno','_plotdata','clf','plotaxes_dict', \
                           '_axesnames','show','_show','kwargs','_handle',\
			   '_type']

        super(ClawPlotFigure, self).__init__(attributes = attributes)    

        self._plotdata = plotdata           # parent ClawPlotData object
        self.name = name
        self.figno = figno
        self.kwargs = {}
        self.clf_each_frame = True
        self.clf_each_gauge = True
        self._axesnames = []
        self.show = True
        self._show = True
        self.plotaxes_dict  = {}
        self.type = type   # = 'each_frame' or 'each_run' or 'each_gauge'
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
            print '*** Warning, axes named %s has already been created' % name

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
class ClawPlotAxes(Data):
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

        attributes = ['name','type','figno','plotdata','plotfigure','title',\
                           'axescmd','xlimits','ylimits','plotitem_dict', 'user',\
                           'afteraxes','_itemnames','show','_show','_handle', \
                           '_plotfigure','_plotdata', 'scaled']
        super(ClawPlotAxes, self).__init__(attributes = attributes)    

        self._plotfigure = plotfigure                   # figure this item is on
        self._plotdata = plotfigure._plotdata           # parent ClawPlotData object

        self.name = name
        self.title = name
        self.title_with_t = True        # creates title of form 'title at time t = ...'
        self.axescmd = 'subplot(1,1,1)'
        self.user = Data()          # for user to pass things into
                                        # afteraxes, for example
					# Deprecated.
        self.afteraxes = None
        self.xlimits = None
        self.ylimits = None
        self.scaled = False              # true so x- and y-axis scaled same
        self.plotitem_dict  = {}
        self.type = 'each_frame'
        self._itemnames = []
        self.show = True
        self._show = True
        self._handle = None
        self._next_ITEM = 0
        self.figno = self._plotfigure.figno

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
class ClawPlotItem(ClawData):
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
        attributes = ['ndim','outdir','refresh_frames',\
                           'plot_var','plot_var_title', \
                           'MappedGrid', 'mapc2p', \
                           'figno', 'handle', 'params', \
                           'aftergrid','afteritem','framesoln_dict', \
                           '_pobjs','name','plot_type','plot_show','user','show']  

        super(ClawPlotItem, self).__init__(attributes = attributes)    


        self._plotaxes = plotaxes                       # axes this item is on
        self._plotfigure = plotaxes._plotfigure         # figure this item is on
        self._plotdata = plotaxes._plotfigure._plotdata           # parent ClawPlotData object

        try:
            ndim = int(plot_type[0])   # first character of plot_type should be ndim
        except:
            print '*** Error: could not determine ndim from plot_type = ',plot_type

        self.ndim = ndim
        self.name = name
        self.figno = plotaxes.figno

        self.outdir = None              # indicates data comes from 
                                        #   self._plotdata.outdir

        self.plot_type = plot_type
        self.plot_var = 0
        self.plot_show = True

        self.MappedGrid = None          # False to plot on comput. grid even
                                        # if _plotdata.mapc2p is not None.

        self.mapc2p = None              # function to map computational
	                                # points to physical (over-rides
	                                # plotdata.mapc2p if set for item


        self.aftergrid = None           # function called after each grid is
                                        # plotted within each single plotitem.
        self.afteritem = None           # function called after the item is
                                        # plotted for each frame

        self.user = Data()              # for user to pass things into
                                        # aftergrid, for example
                                        # Deprecated.

        self.show = True                # False => suppress showing this item
        self._show = True               # Internal

        self._current_pobj = None


        if ndim == 1:
            self.add_attribute('plotstyle','-')
            self.add_attribute('color',None)
            self.add_attribute('kwargs',{})
            amr_attributes = """show color kwargs""".split()
            for a in amr_attributes:
                self.add_attribute('amr_%s' % a, [])

            if plot_type == '1d_fill_between':
                zero_function = lambda current_data: 0.
                self.add_attribute('plot_var2',zero_function)
                self.add_attribute('fill_where',None)

            if plot_type == '1d_from_2d_data':
                self.add_attribute('map2d_to_1d',None)

        elif ndim == 2:

            # default values specifying this single plot:
            self.add_attribute('plot_type',plot_type)
            self.add_attribute('gridlines_show',0)
            self.add_attribute('gridlines_color','k')
            self.add_attribute('grid_bgcolor','w')
            self.add_attribute('gridedges_show',0)
            self.add_attribute('gridedges_color','k')
            self.add_attribute('kwargs',{})
            amr_attributes = """gridlines_show gridlines_color grid_bgcolor
                     gridedges_show gridedges_color kwargs""".split()
            for a in amr_attributes:
                self.add_attribute('amr_%s' % a, [])

            if plot_type == '2d_pcolor':
                from visclaw import colormaps
                self.add_attribute('pcolor_cmap',colormaps.yellow_red_blue)
                self.add_attribute('pcolor_cmin',None)
                self.add_attribute('pcolor_cmax',None)
                self.add_attribute('add_colorbar',True)

            elif plot_type == '2d_imshow':
                from visclaw import colormaps
                self.add_attribute('imshow_cmap',colormaps.yellow_red_blue)
                self.add_attribute('imshow_cmin',None)
                self.add_attribute('imshow_cmax',None)
                self.add_attribute('add_colorbar',True)


            elif plot_type == '2d_contour':
                self.add_attribute('contour_nlevels',20)
                self.add_attribute('contour_levels',None)
                self.add_attribute('contour_min',None)
                self.add_attribute('contour_max',None)
                self.add_attribute('contour_show',1)
                self.add_attribute('contour_colors','k')
                self.add_attribute('contour_cmap',None)
                self.add_attribute('add_colorbar',False)
                amr_attributes = """show colors cmap""".split()
                for a in amr_attributes:
                    self.add_attribute('amr_contour_%s' % a, [])

            elif plot_type == '2d_schlieren':
                from visclaw import colormaps
                self.add_attribute('schlieren_cmap',colormaps.schlieren_grays)
                self.add_attribute('schlieren_cmin',None)
                self.add_attribute('schlieren_cmax',None)
                self.add_attribute('add_colorbar',False)

            elif plot_type == '2d_grid':
                self.add_attribute('max_density',None)
                self.gridlines_show = True
                
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
                         key_scale key_kwargs""".split()
                for a in amr_attributes:
                    self.add_attribute('amr_quiver_%s' % a, [])

            else:
                 print '*** Warning 2d plot type %s not recognized' % plot_type


        elif ndim == 3:
            print '*** Warning- ClawPlotItem not yet set up for ndim = 3'
    
        else:
            print '*** Warning- Unrecognized plot_type in ClawPlotItem'

        self.params = {}  # dictionary to hold optional parameters
        

    def getframe(self,frameno):
        """
        ClawPlotItem.getframe:
        Return an object of class Solution containing the solution
        for frame number frameno.

        If self.refresh_frames == True then this frame is read from the fort
        files, otherwise it is read from the fort files only if the
        the dictionary self.framesoln_dict has key frameno.  If it does, the
        frame has previously been read and the dictionary value is returned.
        """

        plotdata = self._plotdata
        outdir = self.outdir
        framesoln = plotdata.getframe(frameno, outdir)

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


class GaugeSolution(Data):
    """
    Holds gaugeno, t, q, x, y, t1, t2 for a single gauge.
    """

    def __init__(self):

        data_files = []
        gauge_attrs = 'gaugeno level t q x y t1 t2'.split()

        # Initialize the data object and read the data files
        super(GaugeSolution,self).__init__(data_files,gauge_attrs)

        # default values of attributes:
        # none.


# ============================================================================
#  Subclass ClawOtherFigure containing data for plotting a figure
# ============================================================================
class ClawOtherFigure(Data):
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

        attributes = ['name','_plotdata','fname','makefig']

        super(ClawOtherFigure, self).__init__(attributes = attributes)    

        self._plotdata = plotdata           # parent ClawPlotData object
        self.name = name
        self.fname = None            # name of png file
        self.makefig = None          # function invoked to create figure
