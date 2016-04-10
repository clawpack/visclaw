
""" 
Dummy setplot does nothing currently in 3d.
Still need to implement Python plotting in 3d.

Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 


#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of clawpack.visclaw.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    plotdata.clearfigures()  # clear any old figures,axes,items data
    
    print "**** Python plotting tools not yet implemented in 3d"
    print "**** No plots will be generated."

    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via clawpack.visclaw.frametools.printframes:

    plotdata.printfigs = False               # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = []             # list of frames to print
    plotdata.print_fignos = []               # list of figures to print
    plotdata.html = False                    # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.html_movie = 'JSAnimation'      # new style, or "4.x" for old style
    plotdata.latex = False                   # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    return plotdata

