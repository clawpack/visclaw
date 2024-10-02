"""
Module Iplotclaw for interactive plotting of Clawpack results.

For more instructions see the Usage notes in class Iplotclaw below. 

For options during looping type:
  >>> ip = Iplotclaw()
  >>> ip.plotloop()
  PLOTCLAW> help

"""

import sys
from pathlib import Path

import matplotlib
matplotlib.rc('text', usetex=False)
matplotlib.interactive(True)
import matplotlib.pyplot as plt
import clawpack.visclaw.frametools as frametools
from .iplot import Iplot

#------------------------
class Iplotclaw(Iplot):
#------------------------
    """
    Class for interactively stepping through Clawpack plots.
    Uses frametools.plotframe to actually plot each frame.

    Usage:
    ------
    >>> from clawpack.visclaw.Iplotclaw import Iplotclaw 
    >>> ip = Iplotclaw()             # new instantiation
    >>> ip.plotloop()                # to start looping
    PLOTCLAW > help                  # for list of available commands
    PLOTCLAW > q                     # to quit looping and return to python
    >>> ip.plotloop()                # to restart looping at previous frame,
                                     #    with data, outdir, etc. preserved.
    Arguments:
    ----------
    The defaults are:
       Iplotclaw(setplot='setplot.py', outdir=None) 
    The setplot argument gives the file providing the setplot function.
    The outdir argument gives the directory providing the fort.* files.
      If outdir==None, the file .output created by 'make .output' is
      examined to determine where the most recent output might be found.
      If .output does not exist, outdir defaults to '.', the current directory.
    Other arguments of Iplotclaw rarely need to be changed:
       completekey='tab', stdin=None, stdout=None
    """

    # initialization:
    # ---------------

    prompt = 'PLOTCLAW > '
    lastcmd = 'n'             # initialize so <return> advances frame'

    def __init__(self, setplot='setplot.py', outdir=None, \
                 completekey='tab', stdin=None, stdout=None, simple=False,
                 controller=None, fname=None, fps=None):
        """Instantiate a line-oriented interpreter framework.


        The optional argument 'completekey' is the readline name of a
        completion key; it defaults to the Tab key. If completekey is
        not None and the readline module is available, command completion
        is done automatically. The optional arguments stdin and stdout
        specify alternate input and output file objects; if not specified,
        sys.stdin and sys.stdout are used.

        """
        from clawpack.visclaw import data

        self.simple = simple

        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin
        if stdout is not None:
            self.stdout = stdout
        else:
            self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = completekey
 
        self.setplot = setplot
        plotdata = data.ClawPlotData(controller)
        plotdata.setplot = self.setplot
        plotdata._mode = 'iplotclaw'

        if outdir is None:
            try:
                # possibly set by 'make .output' and stored in .output:
                dot_output = open('.output','r')    
                outdir = dot_output.readline().strip()
                dot_output.close()
            except:
                outdir = '.'
        plotdata.outdir = outdir
        # Note also that outdir might be reset by setplot!

        if not simple:
            try:
                plotdata = frametools.call_setplot(self.setplot,plotdata)
            except:
                print('*** Problem executing setplot in Iplotclaw')
                print('    setplot = ', self.setplot)
                print('*** Either this file does not exist or ')
                print('    there is a problem executing the function setplot in this file.')
                print('*** PLOT PARAMETERS MAY NOT BE SET! ***')
                raise

        self.plotdata = plotdata
        self.prevplotdata = plotdata
        self.restart = False
        self.prevframeno = 0
        self.num_frames = len(list(Path(plotdata.outdir).glob("fort.q*")))

        if fps or fname:
            import matplotlib.animation as animation
            fname = fname or "movie.gif"
            fps = fps or 2
            def update(i):
                frametools.plotframe(i, self.plotdata, simple=self.simple, refresh=True)
            update(0)
            anim = animation.FuncAnimation(plt.gcf(), update, frames=self.num_frames, interval=1e3/fps)
            anim.save(fname)
            plt.close("all")

        self.mapped_keys = dict(right="n", left="p", up="n", down="p", q="quit")  # Corresponding do_ command
        self.frameno_input = ""
        self.frames = {}

    def plot_and_cache(self,frameno):
        try:
            if frameno not in list(self.frames.keys()):
                frametools.plotframe(self.frameno, self.plotdata, simple=self.simple, refresh=True)
                self.frames[str(frameno)] = ''
                for fn in plt.get_fignums():
                    plt.figure(fn).canvas.mpl_connect('key_press_event', self.on_key_press_event)
            else:
                frametools.plotframe(self.frameno, self.plotdata, simple=self.simple, refresh=False)
        except IOError as e:
            print(str(e))
    def help_n(self):
        print('n: advance to next frame\n')

    def load_frame(self,frameno):
        frame = self.plotdata.getframe(frameno, self.plotdata.outdir)
        return frame


    # Commands that can be typed at the PLOTCLAW> prompt:
    # ---------------------------------------------------

    # call setplot again
    # --------------------
    def do_resetplot(self, rest):
        if rest:
            self.setplot = rest
            print('*** Resetting setplot to: ',rest)
            self.plotdata.setplot = self.setplot
        print('Executing setplot from ',self.setplot)
        try:
            frametools.call_setplot(self.setplot,self.plotdata)
        except:
            print('*** Problem re-executing setplot')
            raise

    def help_resetplot(self):
        print('resetplot: re-execute the function setplot')
        print('           The easiest way to change plotting parameters')
        print('           is to modify setplot.py and then do resetplot.')
        print(' ')
        print('resetplot <new>: switch to a different setplot function')
        print('           as specified by <new>, which is a function or')
        print('           a string specifying the module containing setplot.')

    # show plot parameters:
    # ---------------------
    def do_show(self, rest):
        self.plotdata.showitems()

    def help_show(self):
        print('show: show the current plot items')


    # cleargauges
    # ---------
    def do_cleargauges(self, rest):
        if rest=='':
            self.plotdata.gaugesoln_dict.clear()
            print('Cleared all gauges')
        else:
            print('Not implemented: try cleargauges')

    def help_cleargauges(self):
        print('cleargauges: delete gauge data from cache to replot')
        print('    use if you have rerun the code and want to plot the')
        print('    latest results')


    # plotgauge commands:
    # --------------
    def do_plotgauge(self, rest):
        from clawpack.visclaw import gaugetools
        import os
        outdir = os.path.abspath(self.plotdata.outdir)

        # Construct gaugeno list
        if rest in ['','all']:
            try:
                import clawpack.amrclaw.data as amrclaw
            except ImportError as e:
                print("You must have AMRClaw installed to plot gauges.")
                print("continuing...")
                return
            
            gaugedata = amrclaw.GaugeData()
            gaugedata.read(self.plotdata.outdir)
            gaugenos = gaugedata.gauge_numbers
        else:
            gaugenos = [int(rest)]

        # Loop through requested gauges and read in if not in gaugesoln_dict
        for (n,gaugeno) in enumerate(gaugenos):
            # Is the next line necessary or can we delete it?
            gauge = self.plotdata.getgauge(gaugeno,outdir)
            
            gaugetools.plotgauge(gaugeno,self.plotdata)

            if n < len(gaugenos) - 1:
                ans = input("      Hit return for next gauge or q to quit ")
                if ans == "q":
                    break


    def help_plotgauge(self):
        print('plotgauge n  : plot figure for gauge number n, if found')
        print('plotgauge all: loop through plots of all gauges')
        print('plotgauge    : loop through plots of all gauges')
        
        
    # Convenience functions for examining solution or making additional
    # plots from the ipython command line:
    # -----------------------------------------------------------------

    def get_frame(self, frameno=None):
        """
        Return the framesoln for Frame for frameno.  
        If frameno is not specified, use the most recently plotted frameno.
        """
        if frameno is None:
            frameno = self.frameno

        return self.plotdata.getframe(frameno)

    def get_t(self, frameno=None):
        """
        Return the time for Frame for frameno.  
        If frameno is not specified, use the most recently plotted frameno.
        """
        if frameno is None:
            frameno = self.frameno

        return self.plotdata.getframe(frameno).t


    def get_patches(self, frameno=None):
        """
        Return the list of patches for frameno.  
        If frameno is not specified, use the most recently plotted frameno.
        """
        if frameno is None:
            frameno = self.frameno

        return self.plotdata.getframe(frameno).patches

    def get_patch(self, frameno=None):
        """
        Return the final patch for frameno.  
        If frameno is not specified, use the most recently plotted frameno.  
        If AMR is not used and there is only one patch, then return this one 
        (rather than a list with one element, as get_patches would return).  
        If AMR is used, then the final patch plotted is returned, 
        similar to claw/matlab/plotclaw behavior where only the final patch 
        is easily available after the plots are made.
        """
        if frameno is None:
            frameno = self.frameno
        
        return self.plotdata.getframe(frameno).patches[-1]

    def otherfigures(self):
        """
        Create any other figures specified in plotdata.otherfigure_dict.
        """
        
        plotdata = self.plotdata
        if len(plotdata.otherfigure_dict)==0:
            print("No other figures specified.")
        else:
            for name in plotdata.otherfigure_dict.keys():
                otherfigure = plotdata.otherfigure_dict[name]
                fname = otherfigure.fname
                makefig = otherfigure.makefig
                if makefig:
                    if type(makefig)==str:
                        try:
                            exec(makefig)
                        except:
                            print("*** Problem executing makefig ")
                            print("    for otherfigure ",name)
                            import pdb; pdb.set_trace()
                    else:
                        try:
                            makefig(plotdata)
                        except:
                            print("*** Problem executing makefig function")
                            print("    for otherfigure ",name)
                else:
                    print("No makefig function specified for ",name)

    def on_key_press_event(self, event):
        k = event.key

        if k.isnumeric():
            self.frameno_input += k
            return None
        elif k == "enter":
            self.stdout.write("\n")
            self.frameno = min(int(self.frameno_input or self.frameno),
                               self.num_frames-1)
            self.onecmd(f"j {self.frameno} \n")
            self.frameno_input = ""
        elif k in self.mapped_keys:
            self.stdout.write("\n")
            self.onecmd(self.mapped_keys[k])
        else:
            return None

        self.stdout.write(self.prompt)
        self.stdout.flush()
        self.lastcmd = "n"
        

# end of Iplotclaw.
#----------------------------------------------------------------------
