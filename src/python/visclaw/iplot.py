"""
Module Iplotclaw for interactive plotting of Clawpack results.

For more instructions see the Usage notes in class Iplotclaw below. 

For options during looping type:
  >>> ip = iplot()
  >>> ip.plotloop()
  PLOTCLAW> help

"""

import cmd, os, sys


import matplotlib
matplotlib.rc('text', usetex=False)
matplotlib.interactive(True)

import matplotlib.pyplot as plt

import clawpack.clawutil.clawdata as clawdata
from clawpack.visclaw import data, frametools, gaugetools

#------------------------
class Iplot(cmd.Cmd):
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
    from clawpack.visclaw import frametools, data

    # initialization:
    # ---------------

    prompt = 'IPLOT > '
    lastcmd = 'n'             # initialize so <return> advances frame'

    def __init__(self, loadfun, plotfun, \
                 completekey='tab', stdin=None, stdout=None):
        """Instantiate a line-oriented interpreter framework.

        The optional argument 'completekey' is the readline name of a
        completion key; it defaults to the Tab key. If completekey is
        not None and the readline module is available, command completion
        is done automatically. The optional arguments stdin and stdout
        specify alternate input and output file objects; if not specified,
        sys.stdin and sys.stdout are used.
        """

        import sys

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
 
        self.load_frame = loadfun
        self.plot_frame = plotfun

        self.restart = False
        self.prevframeno = 0

        self.frames = {}

    def plot_and_cache(self,frameno):
        if frameno not in self.frames.keys():
            try:
                frame = self.load_frame(self.frameno)
                self.frames[str(frameno)] = frame
                self.plot_frame(frame)
            except IOError:
                print "Swallowing IOError to avoid crashing in interactive mode."
 

    def preloop(self):

        print '\nInteractive plotting... '
        print 'Type ? at IPLOT prompt for list of commands'

        startframeno = raw_input('\n    Start at which frame [default=%i] ? '\
                                % self.prevframeno)

        makeplot = True 

        if startframeno == '':
            self.frameno = self.prevframeno
            if self.restart:
                replot = raw_input('    Replot data for frame %s [no] ? ' \
                                % self.frameno)

                if replot not in ('y','yes','Y'):
                    makeplot = False

                if makeplot:
                    reload = raw_input('    Reload data for frame %s [no] ? ' \
                                    % self.frameno)
                    if reload in ('y','yes','Y'):
                        self.frames.pop(str(frameno))
        else:
            try:
                self.frameno = int(startframeno)
            except ValueError:
                print '\n    *** Error: frameno must be an integer, resetting to 0'
                self.frameno = 0

        if makeplot:
            self.plot_and_cache(self.frameno)

        self.lastcmd = 'n'
        self.restart = True 

    # end of initialization 
    # ---------------------

    def postloop(self):
        self.prevframeno = self.frameno


    # Commands that can be typed at the PLOTCLAW> prompt:
    # ---------------------------------------------------

    # help command:
    # -------------
    def help_help(self):
        print 'print this list of valid commands\n'

    # next frame:
    # -----------
    def do_n(self, rest):
        #print '    frameno = ',self.frameno
        self.frameno = self.frameno+1
        self.plot_and_cache(self.frameno)
    def help_n(self):
        print 'n: advance to next frame\n'

    # previous frame:
    # ---------------
    def do_p(self, rest):
        self.frameno = max(self.frameno-1, 0)
        self.plot_and_cache(self.frameno)
    def help_p(self):
        print 'p: go back to previous frame\n'

    # jump to arbitrary frame:
    # ------------------------
    def do_j(self, rest):
        try:
            newframeno = int(rest)
        except:
            newframeno = raw_input('\n    Jump to which frame? ')
        if newframeno == 'n': 
            self.do_n(rest)
            self.lastcmd = 'n'
        elif newframeno == 'p': 
            self.do_p(rest)
            self.lastcmd = 'p'
        else:
            try:
                newframeno = int(newframeno)
            except ValueError:
                print '\n    *** Error: frameno must be an integer, n, or p'
            self.frameno = newframeno
            self.plot_and_cache(self.frameno)
    def help_j(self):
        print 'j N: jump to frame N\n'
        print 'j:   jump to some other frame (will prompt for N)\n'

    # redraw frame:
    # -------------
    def do_r(self, rest):
        self.plot_and_cache(self.frameno)
    def help_r(self):
        print 'r: redraw the current frame,  rr: reload and redraw\n'

    def do_rr(self, rest):
        try:
            self.frames.pop(str(self.frameno))
            print 'Cleared data for frame ',self.frameno
        except KeyError:
           print 'No frame data to clear for frame ',self.frameno
        self.plot_and_cache(self.frameno)
    def help_rr(self):
        print 'r: redraw the current frame,  rr: reload and redraw\n'

    # save
    # ---------
    def do_save(self, rest):
        rest = rest.split()
        if len(rest)==2:
            try:
                figno = int(rest[0])
            except ValueError:
                print "*** Expected figure number, got: ",rest[0]
            fname = rest[1]
            plt.figure(figno)
            plt.savefig(fname)
            print "Saved figure number %s to file %s" % (figno,fname)
        else:
            print "*** save requires two arguments: figno, fname"
            print "*** got: ",rest

    def help_save(self):
        print 'save figno fname: save figure figno to file fname using savefig.'


    # print working directory:
    # ------------------------
    def do_pwd(self, rest):
        print '  now in directory: ',os.getcwd()
        print '  data from outdir: ',self.plotdata.outdir
    def help_pwd(self):
        print 'pwd: print current working directory and outdir'
        print '     fort.* files in outdir provide frame data\n'


    # print figure to a file:
    # -----------------------
    def do_print(self, rest):
        #from clawpack.visclaw import frametools
        fname = rest
        for figno in plt.get_fignums():
            if len(fname)>0:
                # doesn't work properly!
                plt.figure(figno)
                name = fname.split('.')[0]+string.zfill(figno,4)+'.'+fname.split('.')[1]
                plt.savefig(name)
            else:
                print 'You must specify a file name.'

    def help_print(self):
        print 'print: print all figures for this frame to files of the form'
        print '      frame000NfigJ.png'
        print 'To print a single figure or with different style, try e.g.'
        print '     PLOTCLAW > q'
        print '     figure(2)'
        print '     savefig("myname.jpg")\n'
        

    # use vi e.g. to edit setplot.py:
    # -------------------------------
    def do_vi(self, rest):
        exitcode = os.system('vi %s' % rest)
        if exitcode != 0:
            print '*** System vi command failed.  Try "help edit"'

    def help_vi(self):
        print 'Edit file using vi, for example to change the plot parameters:'
        print '    PLOTCLAW> vi setplot.py '
        print '    PLOTCLAW> resetplot '
        print 'See also "help edit" for use of other editors.\n'
        

    # edit a file using editor specified by environment variable EDITOR:
    # -----------------------------------------------------------------
    def do_edit(self, rest):
        try:
            editor = os.environ['EDITOR']
            eval("os.system('%s %s')" % (editor,rest))
        except:
            print '*** Environment variable EDITOR not set... '
            print '*** Type "help edit" for more info'

    def help_edit(self):
        print 'Edit file, for example to change the plot parameters:'
        print '    PLOTCLAW> edit setplot.py '
        print '    PLOTCLAW> resetplot '
        print 'Specify the editor by setting environment variable EDITOR'
        print '  before starting Python shell.'
        print 'If you want to use vi, see also "help vi".\n'

        
    # quit commands:
    # --------------
    def do_quit(self, rest):
        print 'quitting...'
        return True
    def help_quit(self):
        print 'q or quit: terminates the command loop\n'
        
    def do_q(self, rest):
        print 'quitting...'
        return True
    def help_q(self):
        print 'q or quit: terminates the command loop\n'
        
    def do_k(self, rest):
        print 'quitting...'
        return True
    def help_k(self):
        print 'k: terminates the command loop\n'
        
    def do_EOF(self, rest):
        print "quitting..."
        return True
    def help_EOF(self):
        print "Terminates the command loop\n"
        
    # alias plotloop = cmdloop:
    # -------------------------
    def plotloop(self):
        self.cmdloop()


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

        return self.frames[str(frameno)]


# end of Iplotclaw.
#----------------------------------------------------------------------

