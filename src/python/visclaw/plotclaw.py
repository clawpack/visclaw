
"""
Generic code for plotting Clawpack results.

Execute from unix by
    $ python $CLAW/visclaw/src/python/visclaw/plotclaw.py
from a directory that contains a file setplot.py that sets other
parameters to specify the desired plots, location of data, etc.

If a different file is to be used to define the function setplot, this can
be given as an argument, e.g.
    $ python $CLAW/visclaw/src/python/visclaw/plotclaw.py setplot_alternative.py

From most Clawpack applications directories the command
    $ make .plots
will call the plotclaw function from this module.

"""

import matplotlib
matplotlib.use('Agg') 

import sys
import os
import subprocess

import clawpack.visclaw.frametools as frametools

if sys.platform in ['win32','cygwin']:
    pypath = 'C:/cygwin' + os.environ['CLAW'] + '/python'
    sys.path.append(pypath)


def plotclaw(outdir='.', plotdir='_plots', setplot = 'setplot.py',
             format='ascii', msgfile='', frames=None):
    """
    Create html and/or latex versions of plots.

    INPUT:
        setplot is a module containing a function setplot that will be called
                to set various plotting parameters.
        format specifies the format of the files output from Clawpack
    """

    from clawpack.visclaw.data import ClawPlotData
    from clawpack.visclaw import plotpages

    plotdata = ClawPlotData()
    plotdata.outdir = outdir
    plotdata.plotdir = plotdir
    plotdata.setplot = setplot
    plotdata.format = format
    plotdata.msgfile = msgfile

    frametools.call_setplot(plotdata.setplot, plotdata)

    if plotdata.parallel:

        # If this is the original call then we need to split up the work and 
        # call this function again
        if frames is None:
            if plotdata.num_procs is None:
                plotdata.num_procs = os.environ.get("OMP_NUM_THREADS", 1)


            frames = [[] for n in xrange(plotdata.num_procs)]
            framenos = frametools.only_most_recent(plotdata.print_framenos,
                                                   outdir)
            for (n, frame) in enumerate(framenos):
                frames[n%plotdata.num_procs].append(frame)

            # Create subprocesses to work on each
            plotclaw_cmd = "python $CLAW/visclaw/src/python/visclaw/plotclaw.py"
            process_queue = []
            for n in xrange(plotdata.num_procs):
                plot_cmd = "%s %s %s %s" % (plotclaw_cmd, 
                                            outdir,
                                            plotdir, 
                                            setplot)
                plot_cmd = plot_cmd + " " + " ".join([str(i) for i in frames[n]])
                process_queue.append(subprocess.Popen(plot_cmd, shell=True))


            wait = True
            poll_interval = 1
            if wait:
                import time
                while len(process_queue) > 0:
                    time.sleep(poll_interval)
                    for process in process_queue:
                        if process.poll() is not None:
                            process_queue.remove(process)
                    print "Number of processes currently:",len(process_queue)
            sys.exit(0)

        else:
            plotdata.print_framenos = frames

    plotpages.plotclaw_driver(plotdata, verbose=False, format=format)


if __name__=='__main__':
    """
    If executed at command line prompt, simply call the function, with
    any arguments passed in.
    """

    if len(sys.argv) > 4:
        frames = [int(frame) for frame in sys.argv[4:]]
        plotclaw(sys.argv[1], sys.argv[2], sys.argv[3], frames=frames)
    elif len(sys.argv) == 4:
        plotclaw(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        plotclaw(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        plotclaw(sys.argv[1])
    else:
        plotclaw()
