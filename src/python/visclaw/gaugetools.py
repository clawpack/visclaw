"""
Tools for plotting data from gauges, gauge locations, etc.
"""

import os,sys,glob
import traceback
import warnings

import numpy as np

import clawpack.clawutil.data as clawdata

from clawpack.visclaw.frametools import set_show

plotter = 'matplotlib'
if plotter == 'matplotlib':
    if 'matplotlib' not in sys.modules:
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use an image backend
        except:
            print("*** Error: problem importing matplotlib")

try:
    import pylab
except:
    print("*** Error: problem importing pylab")

# Gauge solution class
class GaugeSolution(object):
    r"""Object representing a single gauge"""

    def t1():
        doc = "(float) - Beginning of gauge recording time interval."
        def fget(self):
            if self.t is not None:
                return np.min(self.t)
            else:
                return None
        def fset(self, value):
            if self.q is None:
                if self.t is not None:
                    self.t[0] = value
                else:
                    self.t = [-np.infty,value]
            else:
                raise ValueError('Time interval already set.')
        return locals()
    t1 = property(**t1())

    def t2():
        doc = "(float) - End of gauge recording time interval."
        def fget(self):
            if self.t is not None:
                return np.max(self.t)
            else:
                return None
        def fset(self, value):
            if self.q is None:
                if self.t is not None:
                    self.t[1] = value
                else:
                    self.t = [-np.infty,value]
            else:
                raise ValueError('Time interval already set.')
        return locals()
    t2 = property(**t2())

    def location():
        doc = "(tuple) - Location of this gauge."
        def fget(self):
            if self._location is None:
                return ("Unknown","Unknown")
            return self._location
        def fset(self, value):
            if isinstance(value,tuple) or isinstance(value,list):
                self._location = value
            else:
                raise ValueError("Location information must be a list or tuple.")
        return locals()
    location = property(**location())

    def __init__(self, number, location=None):
        
        warnings.warn("This version of GaugeSolution is deprecated, use the ",
                      "class definition in clawpack.pyclaw.gauges instead.")

        # Gauge descriptors
        self.number = number
        self._location = None
        if location is not None:
            self.location = location

        # Data written out (usually)
        self.level = None
        self.t = None
        self.q = None

    def __repr__(self):
        # Make sure all necessary data has been set
        if self._location is None or self.t1 is None or self.t2 is None:
            output = None
        else:
            output = "%4i" % self.number
            for j in range(len(self.location)):
                output = " ".join((output,"%17.10e" % self.location[j]))
            output = " ".join((output,"%13.6e" % self.t1))
            output = " ".join((output,"%13.6e\n" % self.t2))
        return output

    def __str__(self):
        return ("Gauge %s: location = %s, t = [%s,%s]" % 
                                    (self.number,self.location,self.t1,self.t2))


#==========================================
def plotgauge(gaugeno, plotdata, verbose=False):
#==========================================

    """
    Plot all requested plots for a single gauge from the computation.
    The plots are requested by setting attributes of plotdata
    to ClawPlotFigure objects with plot_type="each_gauge".

    """

    if verbose:  
        gaugesoln = plotdata.getgauge(gaugeno)
        print('    Plotting gauge %s  at x = %s, y = %s ... '  \
                 % (gaugeno, gaugesoln.location[0], gaugesoln.location[1]))

    if plotdata.mode() == 'iplotclaw':
        pylab.ion()

        
    try:
        plotfigure_dict = plotdata.plotfigure_dict
    except:
        print('*** Error in plotgauge: plotdata missing plotfigure_dict')
        print('*** This should not happen')
        return None

    if len(plotfigure_dict) == 0:
        print('*** Warning in plotgauge: plotdata has empty plotfigure_dict')
        print('*** Apparently no figures to plot')




    # initialize current_data containing data that will be passed
    # to beforegauge, aftergauge, afteraxes commands
    current_data = clawdata.ClawData()
    current_data.add_attribute("user",{})   # for user specified attributes
                                           # to avoid potential conflicts
    current_data.add_attribute('plotdata',plotdata)
    current_data.add_attribute('gaugeno',gaugeno)

    # call beforegauge if present, which might define additional 
    # attributes in current_data or otherwise set up plotting for this
    # gauge.

    beforegauge =  getattr(plotdata, 'beforegauge', None)
    if beforegauge:
        if isinstance(beforegauge, str):
            # a string to be executed
            exec(beforegauge)
        else:
            # assume it's a function
            try:
                output = beforegauge(current_data)
                if output: current_data = output
            except:
                print('*** Error in beforegauge ***')
                raise



    # iterate over each single plot that makes up this gauge:
    # -------------------------------------------------------
 
    if plotdata._mode == 'iplotclaw':
        gaugesoln = plotdata.getgauge(gaugeno)
        gaugeloc = gaugesoln.location
        if len(gaugeloc) == 2:
            print('    Plotting Gauge %s  at x = %s, y = %s ... '  \
                     % (gaugeno, gaugeloc[0], gaugeloc[1]))
        elif len(gaugeloc) == 3:
            print('    Plotting Gauge %s  at x = %s, y = %s, z = %s ... '  \
                     % (gaugeno, gaugeloc[0], gaugeloc[1], gaugeloc[2]))
        requested_fignos = plotdata.iplotclaw_fignos
    else:
        requested_fignos = plotdata.print_fignos
    plotted_fignos = []

    plotdata = set_show(plotdata)   # set _show attributes for which figures
                                    # and axes should be shown.

    # loop over figures to appear for this gauge: 
    # -------------------------------------------

    for figname in plotdata._fignames:
        plotfigure = plotdata.plotfigure_dict[figname]
        if (not plotfigure._show) or (plotfigure.type != 'each_gauge'):
            continue  # skip to next figure 

        figno = plotfigure.figno
        if requested_fignos != 'all':
            if figno not in requested_fignos:
                continue # skip to next figure

        plotted_fignos.append(figno)


        if 'facecolor' not in plotfigure.kwargs:
            # Use white as default starting in v5.10.0
            # To use old default Clawpack tan, in setplot.py set:
            #     plotfigure.facecolor = \
            #           clawpack.visclaw.colormaps.clawpack_tan
            plotfigure.kwargs['facecolor'] = 'w'

        if plotfigure.figsize is not None:
            plotfigure.kwargs['figsize'] = plotfigure.figsize

        # create figure and set handle:
        plotfigure._handle = pylab.figure(num=figno, **plotfigure.kwargs)

        pylab.ioff()
        if plotfigure.clf_each_gauge:
            pylab.clf()

        try:
            plotaxes_dict = plotfigure.plotaxes_dict
        except:
            print('*** Error in plotgauge: plotdata missing plotaxes_dict')
            print('*** This should not happen')
            return  None

        if (len(plotaxes_dict) == 0) or (len(plotfigure._axesnames) == 0):
            print('*** Warning in plotgauge: plotdata has empty plotaxes_dict')
            print('*** Apparently no axes to plot in figno ',figno)

        # loop over axes to appear on this figure:
        # ----------------------------------------

        for axesname in plotfigure._axesnames:
            plotaxes = plotaxes_dict[axesname]
            if not plotaxes._show:
                continue   # skip this axes if no items show

            # create the axes:
            axescmd = getattr(plotaxes,'axescmd','subplot(1,1,1)')
            axescmd = 'plotaxes._handle = pylab.%s' % axescmd
            exec(axescmd)

            # loop over items:
            # ----------------

            for itemname in plotaxes._itemnames:
                
                plotitem = plotaxes.plotitem_dict[itemname]
                outdir = plotitem.outdir
                if outdir is None:
                    outdir = plotdata.outdir
                gaugesoln = plotdata.getgauge(gaugeno, outdir)

                current_data.add_attribute('gaugesoln',gaugesoln)
                current_data.add_attribute('q',gaugesoln.q)
                current_data.add_attribute('t',gaugesoln.t)

                if plotitem._show:
                    try:
                        output = plotgauge1(gaugesoln,plotitem,current_data)
                        if output: current_data = output
                        if verbose:  
                                print('      Plotted  plotitem ', itemname)
                    except:
                        print('*** Error in plotgauge: problem calling plotgauge1')
                        traceback.print_exc()
                        return None

            # end of loop over plotitems

    
            title_str = "%s at gauge %s" % (plotaxes.title,gaugeno)
            if plotaxes.title_fontsize is not None:
                plotaxes.title_kwargs['fontsize'] = plotaxes.title_fontsize
            pylab.title(title_str, **plotaxes.title_kwargs)
    
            if plotaxes.time_label is not None:
                if plotaxes.time_label_fontsize is not None:
                    plotaxes.time_label_kwargs['fontsize'] = \
                                    plotaxes.time_label_fontsize
                pylab.xlabel(plotaxes.time_label, **plotaxes.time_label_kwargs)
    
    
            # call an afteraxes function if present:
            afteraxes =  getattr(plotaxes, 'afteraxes', None)
            if afteraxes:
                if isinstance(afteraxes, str):
                    # a string to be executed
                    exec(afteraxes)
                else:
                    # assume it's a function
                    try:
                        current_data.add_attribute("plotaxes",plotaxes)
                        current_data.add_attribute("plotfigure",plotaxes._plotfigure)
                        output = afteraxes(current_data)
                        if output: current_data = output
                    except:
                        print('*** Error in afteraxes ***')
                        raise
    
            if plotaxes.scaled:
                pylab.axis('scaled')
    
            # set axes limits:
            if (plotaxes.xlimits is not None) & (type(plotaxes.xlimits) is not str):
                try:
                    pylab.xlim(plotaxes.xlimits[0], plotaxes.xlimits[1])
                except:
                    pass  # let axis be set automatically
            if (plotaxes.ylimits is not None) & (type(plotaxes.ylimits) is not str):
                try:
                    pylab.ylim(plotaxes.ylimits[0], plotaxes.ylimits[1])
                except:
                    pass  # let axis be set automatically
    
            if plotaxes.grid:
                pylab.grid(**plotaxes.grid_kwargs)
 
            if plotaxes.xticks_kwargs is not None:
                pylab.xticks(**plotaxes.xticks_kwargs)
            if plotaxes.yticks_kwargs is not None:
                pylab.yticks(**plotaxes.yticks_kwargs)

            if plotaxes.ylabel is not None:
                if plotaxes.ylabel_fontsize is not None:
                    plotaxes.ylabel_kwargs['fontsize'] = plotaxes.ylabel_fontsize
                pylab.ylabel(plotaxes.ylabel, **plotaxes.ylabel_kwargs)

            # end of loop over plotaxes
            
        # end of loop over plotfigures


    # call an aftergauge function if present:
    aftergauge =  getattr(plotdata, 'aftergauge', None)
    if aftergauge:
        if isinstance(aftergauge, str):
            # a string to be executed
            exec(aftergauge)
        else:
            # assume it's a function
            try:
                output = aftergauge(current_data)
                if output: current_data = output
            except:
                print('*** Error in aftergauge ***')
                raise


    if plotdata.mode() == 'iplotclaw':
        pylab.ion()
    for figno in plotted_fignos:
        pylab.figure(figno)
        pylab.draw()

    if verbose:
        print('    Done with plotgauge for gauge %i' % (gaugeno))

    
    # print the figure(s) to file(s) if requested:
    if (plotdata.mode() != 'iplotclaw') & plotdata.printfigs:
        # iterate over all figures that are to be printed:
        for figno in plotted_fignos:
            printfig(gaugeno=gaugeno, figno=figno, \
                    format=plotdata.print_format, plotdir=plotdata.plotdir,\
                    verbose=verbose)

    return current_data

    # end of plotgauge

    
#==================================================================
def plotgauge1(gaugesoln, plotitem, current_data):
#==================================================================
    """
    Make a 1d plot for a single plot item for the gauge solution in
    gaugesoln.

    The current_data object holds data that should be passed into
    afterpatch or afteraxes if these functions are defined.  The functions
    may add to this object, so this function should return the possibly
    modified current_data for use in other plotitems or in afteraxes or
    afterframe.

    """

    if not gaugesoln.is_valid():
        import warnings
        warnings.warn("Gauge has not been initialized properly.")
        return

    plotdata = plotitem._plotdata
    plotfigure = plotitem._plotfigure
    plotaxes = plotitem._plotaxes


    # the following plot parameters may be set, depending on what
    # plot_type was requested:

    plot_params = """
             plot_var  afterpatch  plotstyle color kwargs 
             plot_var2 fill_where map_2d_to_1d 
             """.split()

    # No amr_ parameters for gauge data.

    plot_var = plotitem.plot_var
    plot_type = plotitem.plot_type
    kwargs = plotitem.kwargs
    color = plotitem.color
    plotstyle = plotitem.plotstyle

    t = gaugesoln.t * plotaxes.time_scale

    if type(plot_var) is int:
        var = gaugesoln.q[plot_var,:]
    else:
        try:
            var = plot_var(current_data)
        except:
            print('Applying plot_var to current_data failed, try gaugesoln')
            try:
                var = plot_var(gaugesoln)
            except:
                raise Exception("Problem applying plot_var to gaugesoln")
    tmax = t.max()
    varmax = var.max()


    if (plot_type in ['1d_plot']) and (plotstyle != ''):
        if color:
            kwargs['color'] = color

        pobj = pylab.plot(t,var,plotstyle,**kwargs)


    elif plot_type == '1d_empty':
        # no plot to create (user might make one in afteritem or
        # afteraxes)
        pass

    else:
        raise ValueError("Unrecognized plot_type: %s" % plot_type)
        return None

    return current_data
    
def read_setgauges(outdir):
    """
    Read the info from gauges.data.
    """

    try:
        import clawpack.amrclaw.data as amrclaw
    except ImportError as e:
        print("You must have AMRClaw installed to plot gauges.")
        print("continuing...")
        return None

    setgauges = amrclaw.GaugeData()
    try:
        setgauges.read(outdir)
    except IOError as e:
        # No gauges.data file was found, ignore this exception
        pass

    return setgauges


def plot_gauge_locations(plotdata, gaugenos='all', mapc2p=None, \
                format_string='ko',add_labels=True, \
                markersize=5, fontsize=15, xoffset=0, yoffset=0):
    """
    Plot gauge locations on current axes.
    format_string specifies the symbol to be plotted.
    If add_labels==True then labels will also be added (gauge number).
    This routine determines locations from the file gauges.data in
    directory plotdata.rundir.  It does not require reading in the fort.gauge file
    produced by running the code.
    """

    from pylab import figure, plot, clf, title, text

    datadir = plotdata.rundir  # this should contain gauges.data

    try:
        setgauges = read_setgauges(plotdata.outdir)
    except:
        return

    if len(setgauges.gauges) == 0:
        print("*** plot_gauge_locations: No gauges specified in gauges.data")
        return

    if gaugenos=='all':
        gaugenos = setgauges.gauge_numbers
        gauges = setgauges.gauges
    else:
        gauges = []
        for gauge_num in gaugenos:
            for gauge in setgauges.gauges:
                if gauge_num == gauge[0]:
                    gauges.append(gauge)

    for gauge in gauges:
        try:
            xn,yn = gauge[1:3]
            if mapc2p:
                xn,yn = mapc2p(xn,yn)
            plot([xn], [yn], format_string, markersize=markersize)
            if add_labels: 
                xn = xn + xoffset
                yn = yn + yoffset
                text(xn,yn,'  %s' % gauge[0], fontsize=fontsize)
        except:
            print("*** plot_gauge_locations: warning: did not find x,y data for gauge ",gauge[0])


#------------------------------------------------------------------------
def printfig(fname='',gaugeno='', figno='', format='png', plotdir='.', \
             verbose=True):
#------------------------------------------------------------------------
    """
    Save the current plot to file fname or standard name from gauge/fig.
.  
    If fname is nonempty it is used as the filename, with extension
    determined by format if it does not already have a valid extension.

    If fname=='' then save to file gauge000NfigJ.ext  where N is the gauge
    number gaugeno passed in, J is the figure number figno passed in,
    and the extension ext is determined by format.  
    If figno='' then the figJ part is omitted.
    """

    if fname == '':
        fname = 'gauge' + str(gaugeno).rjust(4,'0') 
        if isinstance(figno,int):
            fname = fname + 'fig%s' % figno
    splitfname = os.path.splitext(fname)
    if splitfname[1] not in ('.png','.emf','.eps','.pdf'):
        fname = splitfname[0] + '.%s' % format
    if figno=='':
        figno = 1
    pylab.figure(figno)
    if plotdir != '.':
       fname = os.path.join(plotdir,fname)
    if verbose:  print('    Saving plot to file ', fname)
    pylab.savefig(fname)


#======================================================================
def printgauges(plotdata=None, verbose=True):
#======================================================================

    """
    Produce a set of png files for all the figures specified by plotdata.
    Also produce a set of html files for viewing the figures and navigating
    between them.  These will all be in directorey plotdata.plotdir.

    The ClawPlotData object plotdata will be initialized by a call to
    function setplot unless plotdata.setplot=False.  

    If plotdata.setplot=True then it is assumed that the current directory
    contains a module setplot.py that defines this function.

    If plotdata.setplot is a string then it is assumed this is the name of
    a module to import that contains the function setplot.

    If plotdata.setplot is a function then this function will be used.
    """

    import glob
    from clawpack.visclaw.data import ClawPlotData

    from clawpack.visclaw import plotpages


    if 'matplotlib' not in sys.modules:
        print('*** Error: matplotlib not found, no plots will be done')
        return plotdata
        
    if not isinstance(plotdata,ClawPlotData):
        print('*** Error, plotdata must be an object of type ClawPlotData')
        return plotdata

    plotdata._mode = 'printframes'

    plotdata = call_setplot(plotdata.setplot, plotdata)

    try:
        plotdata.rundir = os.path.abspath(plotdata.rundir)
        plotdata.outdir = os.path.abspath(plotdata.outdir)
        plotdata.plotdir = os.path.abspath(plotdata.plotdir)

        framenos = plotdata.print_framenos # frames to plot
        framenos = plotdata.print_framenos # frames to plot
        fignos = plotdata.print_fignos     # figures to plot at each frame
        fignames = {}                      # names to use in html files

        rundir = plotdata.rundir       # directory containing *.data files
        outdir = plotdata.outdir       # directory containing fort.* files
        plotdir = plotdata.plotdir     # where to put png and html files
        overwrite = plotdata.overwrite # ok to overwrite?
        msgfile = plotdata.msgfile     # where to write error messages
    except:
        print('*** Error in printframes: plotdata missing attribute')
        print('  *** plotdata = ',plotdata)
        return plotdata

    if fignos == 'all':
        fignos = plotdata._fignos
        #for (figname,plotfigure) in plotdata.plotfigure_dict.iteritems():
        #    fignos.append(plotfigure.figno)


    # filter out the fignos that will be empty, i.e.  plotfigure._show=False.
    plotdata = set_show(plotdata)
    fignos_to_show = []
    for figname in plotdata._fignames:
        figno = plotdata.plotfigure_dict[figname].figno
        if (figno in fignos) and plotdata.plotfigure_dict[figname]._show:
            fignos_to_show.append(figno)
    fignos = fignos_to_show
        
    # figure out what type each figure is:
    fignos_each_frame = []
    fignos_each_gauge = []
    fignos_each_run = []
    for figno in fignos:
        figname = plotdata._figname_from_num[figno]
        if plotdata.plotfigure_dict[figname].type == 'each_frame':
            fignos_each_frame.append(figno)
        if plotdata.plotfigure_dict[figname].type == 'each_gauge':
            fignos_each_gauge.append(figno)
        if plotdata.plotfigure_dict[figname].type == 'each_run':
            fignos_each_run.append(figno)
        

    rootdir = os.getcwd()

    try:
        os.chdir(rundir)
    except:
        print('*** Error: cannot move to run directory ',rundir)
        print('rootdir = ',rootdir)
        return plotdata


    if msgfile != '':
        sys.stdout = open(msgfile, 'w')
        sys.stderr = sys.stdout


    try:
        plotpages.cd_plotdir(plotdata)
    except:
        print("*** Error, aborting plotframes")
        return plotdata


    framefiles = glob.glob(os.path.join(plotdir,'frame*.png')) + \
                    glob.glob(os.path.join(plotdir,'frame*.html'))
    if overwrite:
        # remove any old versions:
        for file in framefiles:
            os.remove(file)
    else:
        if len(framefiles) > 1:
            print("*** Remove frame*.png and frame*.html and try again,")
            print("  or use overwrite=True in call to printframes")
            return plotdata

    
    # Create each of the figures
    #---------------------------

    try:
        os.chdir(outdir)
    except:
        print('*** Error printframes: cannot move to outdir = ',outdir)
        return plotdata


    fortfile = {}
    pngfile = {}
    frametimes = {}

    import glob
    for file in glob.glob('fort.q*'):
        frameno = int(file[7:10])
        fortfile[frameno] = file
        for figno in fignos_each_frame:
            pngfile[frameno,figno] = 'frame' + file[-4:] + 'fig%s.png' % figno
    
    if len(fortfile) == 0:
        print('*** No fort.q files found in directory ', os.getcwd())
        return plotdata
    
    # Discard frames that are not from latest run, based on
    # file modification time:
    framenos = only_most_recent(framenos, plotdata.outdir)

    numframes = len(framenos)

    print("Will plot %i frames numbered:" % numframes, framenos)
    print('Will make %i figure(s) for each frame, numbered: ' \
          % len(fignos_each_frame), fignos_each_frame)

    #fignames = {}
    #for figname in plotdata._fignames:
        #figno = plotdata.plotfigure_dict[figname].figno
        #fignames[figno] = figname
    # use new attribute:
    fignames = plotdata._figname_from_num


    for frameno in framenos:
        frametimes[frameno] = plotdata.getframe(frameno, plotdata.outdir).t

    plotdata.timeframes_framenos = framenos
    plotdata.timeframes_frametimes = frametimes
    plotdata.timeframes_fignos = fignos_each_frame
    plotdata.timeframes_fignames = fignames

    # Gauges:
    gaugenos = plotdata.print_gaugenos

    # Make html files for time frame figures:
    # ---------------------------------------

    os.chdir(plotdir)

    if plotdata.html:
        plotpages.timeframes2html(plotdata)
    
    # Make png files for all frames and gauges:
    # -----------------------------------------

    if not plotdata.printfigs:
        print("Using previously printed figure files")
    else:
        print("Now making png files for all figures...")
        for frameno in framenos:
            plotframe(frameno, plotdata, verbose)
            print('Frame %i at time t = %s' % (frameno, frametimes[frameno]))
        for gaugeno in gaugenos:
            plotgauge(gaugeno, plotdata, verbose)
            print('Gauge %i ' % gaugeno)


    if plotdata.latex:
        plotpages.timeframes2latex(plotdata)
    

    # Movie:
    #-------
    
    if plotdata.gif_movie:
        print('Making gif movies.  This may take some time....')
        for figno in fignos_each_frame:
            try:
                os.system('convert -delay 20 frame*fig%s.png moviefig%s.gif' \
                   % (figno,figno))
                print('    Created moviefig%s.gif' % figno)
            except:
                print('*** Error creating moviefig%s.gif' % figno)
    
    os.chdir(rootdir)

    # print out pointers to html index page:
    path_to_html_index = os.path.join(os.path.abspath(plotdata.plotdir), \
                               plotdata.html_index_fname)
    plotpages.print_html_pointers(path_to_html_index)

    # reset stdout for future print statements
    sys.stdout = sys.__stdout__

    return plotdata
    # end of printframes


def compare_gauges(outdir1, outdir2, gaugenos='all', q_components='all',
                    tol=0., verbose=True, plot=False):

    """
    Compare gauge output in two output directories.

    :Input:
     - *outdir1, outdir2* -- output directories
     - *gaugenos* -- list of gauge numbers to compare, or 'all' in which case
       outdir1/gauges.data will be used to determine gauge numbers.
     - *q_components* -- list of components of q to compare.
     - *tol* -- tolerance for checking equality
     - *verbose* -- print out dt and dq for each comparison?
     - *plot* -- if True, will produce a plot for each gauge, with a
       subfigure for each component of q.


    Returns True if everything matches to tolerance *tol*, else False.
    """

    from clawpack.visclaw.data import ClawPlotData
    from matplotlib import pyplot as plt
    
    if gaugenos == 'all':
        # attempt to read from gauges.data:
        try:
            setgauges1 = read_setgauges(outdir1)
            setgauges2 = read_setgauges(outdir2)
        except:
            print('*** could not read gauges.data from one of the outdirs')
            return
        gaugenos = setgauges1.gauge_numbers
        if setgauges2.gauge_numbers != gaugenos:
            print('*** warning -- outdirs have different sets of gauges')

        if len(gaugenos)==0:
            print("*** No gauges found in gauges.data")
            return

    plotdata1 = ClawPlotData()
    plotdata1.outdir = outdir1
    plotdata2 = ClawPlotData()
    plotdata2.outdir = outdir2

    matches = True
    for gaugeno in gaugenos:
        g1 = plotdata1.getgauge(gaugeno,verbose=verbose)
        t1 = g1.t
        q1 = g1.q

        g2 = plotdata2.getgauge(gaugeno,verbose=verbose)
        t2 = g2.t
        q2 = g2.q

        dt = abs(t1-t2).max()
        if verbose:
            print("Max difference in t[:] at gauge %s is %g" % (gaugeno,dt))
        matches = matches and (dt <= tol)

        if q_components == 'all':
            q_components = list(range(q1.shape[0]))

        for m in q_components:
            dq = abs(q1[m,:]-q2[m,:]).max()
            if verbose:
                print("Max difference in q[%s] at gauge %s is %g" % (m,gaugeno,dq))
            matches = matches and (dq <= tol)

        if plot:
            plt.figure(gaugeno)
            plt.clf()
            mq = len(q_components)
            for k,m in enumerate(q_components):
                plt.subplot(mq,1,k+1)
                plt.plot(g1.t,g1.q[m,:],'b',label='outdir1')
                plt.plot(g2.t,g2.q[m,:],'r',label='outdir2')
                plt.legend()
                plt.title('q[%s] at gauge number %s' % (m,gaugeno))
        
    return matches       
