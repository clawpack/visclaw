
"""
Module plotpages

Utilities for taking a set of plot files and creating a set of html and/or
latex/pdf pages displaying the plots.
"""
import os, time, glob
import sys
from functools import wraps

# increase resolution for images in animations:
html_movie_dpi = 100
import matplotlib as mpl
mpl.rcParams['figure.dpi']= html_movie_dpi
#print('+++ backend =',  mpl.rcParams['backend'])


# Required for new animation style modified MAY 2013
import numpy as np
from matplotlib import image as Image
from matplotlib import pyplot as plt

from clawpack.visclaw import gaugetools
from clawpack.visclaw import animation_tools

# Clawpack logo... not used on plot pages currently.
clawdir = os.getenv('CLAW')
if clawdir is not None:
    logo = os.path.join(clawdir,'doc/images/clawlogo.jpg')
    if not os.path.isfile(logo):
        logo = None



#===========================
class PlotPagesData(object):
#===========================

    def __init__(self):
        self.plotdir = 'plots'
        self.overwrite = True
        self.verbose = True

        self.latex = True                # make latex files for figures
        self.latex_fname = 'plots'       # name of latex file to create
        self.latex_title = 'Plots'       # title on top of latex file
        self.latex_itemsperpage = 'all'  # number of items on each page
        self.latex_itemsperline = 2      # number of items on each line
        self.latex_framesperpage = 'all' # number of frames on each page
        self.latex_framesperline = 2     # number of frames on each line
        self.latex_figsperline = 'all'   # number of figures on each line
        self.latex_makepdf = False       # run pdflatex on latex file
        self.latex_preplots = None       # latex to for top of page before plots

        self.html = True                # make html files for figures
        self.html_index_fname = '_PlotIndex.html'   # name of html index file
        self.html_index_title = 'Plot Index'    # title on top of index file
        self.html_homelink = None       # link to here from top of index file
        self.html_itemsperline = 2      # number of items on each line
        self.html_preplots = None       # html to for top of page before plots
        self.html_movie = "JSAnimation" # make html with java script for movie
        self.html_eagle = False         # use EagleClaw titles on html pages?

        self.gif_movie = False          # make animated gif movie of frames

        self.timeframes_framenos = 'all'
        self.timeframes_frametimes = {}
        self.timeframes_fignos = 'all'
        self.timeframes_fignames = {}
        self.timeframes_prefix = 'frame'


        self.pageitem_list = []

    def new_pageitem(self):
        """
        Create a new PageItem to be printed on this page
        """
        pageitem = PageItem()
        self.pageitem_list.append(pageitem)
        return pageitem

    def make_html(self):
        plots2html(self)
        path_to_html_index = os.path.join(os.path.abspath(self.plotdir), \
                                   self.html_index_fname)
        print_html_pointers(path_to_html_index)

    def make_latex(self):
        plots2latex(self)

    def make_pages(self):
        if self.latex:
            self.make_latex()
        if self.html:
            self.make_html()

    def make_timeframes_latex(self):
        timeframes2latex(self)

    def make_timeframes_html(self):
        timeframes2html(self)
        path_to_html_index = os.path.join(os.path.abspath(self.plotdir), \
                                   self.html_index_fname)
        print_html_pointers(path_to_html_index)

#=======================
class PageItem(object):
#=======================

    def __init__(self):
        self.fname = ''  # full path to png or other figure file
        self.html_index_entry = 'Untitled figure'  # Name for link from
                                                  # html index page
        self.html_preitem = None   # any html to be inserted in file
                                   # just before this item.
        self.latex_preitem = None  # any latex to be inserted in file
                                   # just before this item.

#=======================
class HtmlIndex(object):
#=======================

    def __init__(self, fname='_Index.html', title="Index"):
        self.fname = fname
        self.file = open(fname, 'w')
        self.file.write('<html><meta http-equiv="expires" content="0">')
        self.file.write('\n<title>Index</title>')
        self.file.write('\n<body><center><h1>%s</h1></center>\n' \
                   % title)

    def add(self,text = '', link = None):
        if link:
            self.file.write("""
                <p>
                <a href="%s">%s</a>
                """ % (link,text))
        else:
            self.file.write("""
                <p>
                %s
                """ % text)

    def close(self):
        self.file.write("\n</body></html>")
        self.file.close()
        path_to_html_index = os.path.join(os.getcwd(), \
                                   self.fname)
        print_html_pointers(path_to_html_index)


#======================================================================
def plots2html(plot_pages_data):
#======================================================================
    """
    take a sequence of figure files and produce an html file to display them.
    """

    print('\n-----------------------------------\n')
    print('\nCreating html pages...\n')
    startdir = os.getcwd()
    ppd = plot_pages_data
    numitems = len(ppd.pageitem_list)   # number of page items (separate plots)

    if numitems == 0:
        print('*** Warning: 0 plots to put in html file')
        return

    ppd =plot_pages_data
    try:
        cd_with_mkdir(ppd.plotdir, ppd.overwrite, ppd.verbose)
    except:
        print("*** Error, aborting plots2html")
        raise


    creationtime = current_time()


    for pageitem in ppd.pageitem_list:
        splitname = os.path.splitext(pageitem.fname)
        pageitem.hname = splitname[0] + '.html'
        pageitem.ext = splitname[1]


    # Create the index page:
    #-----------------------

    html = open(ppd.html_index_fname,'w')

    if ppd.html_eagle:
        html.write("""
          <html><meta http-equiv="expires" content="0">
          <title>EagleClaw Plot Index</title>
          <head>
          <link type="text/css" rel="stylesheet"
                href="http://localhost:50005/eagleclaw/eagleclaw.css">
          </head>
          <eagle1>EagleClaw -- Plot Index</eagle1>
          <eagle2>Easy Access Graphical Laboratory for Exploring Conservation
          Laws</eagle2>
          <p>
          <center><eagle3>
          <a href="../eaglemenu.html">Main Menu for this run-directory
          </a></eagle3> </center><p>
        """)


    else:
        html.write('<html><meta http-equiv="expires" content="0">')
        html.write('\n<title>%s</title>' % ppd.html_index_title)
        html.write('\n<body><center><h1>%s</h1></center>\n' \
                   % ppd.html_index_title)
        homelink = getattr(ppd,'html_homelink',None)
        if homelink:
            html.write('<center><a href="%s">Back to %s</a></center>\n' \
                       % (homelink, homelink))

    html.write('<p>\n')
    html.write('<center>Plots created: %s &nbsp;&nbsp; ' % creationtime )
    html.write('</center><p>\n')

    html.write('<p>\n<table border=0 cellpadding=5 cellspacing=5>\n')



    html.write("""<p>\n<tr><td><b>All figures:</b></td>
          <td><a href="allfigures.html">html<a> &nbsp;&nbsp;&nbsp;  </td>""")
    if ppd.latex_makepdf:
        html.write('  <td><a href="%s.pdf">%s.pdf</a></td>' \
               % (ppd.latex_fname,ppd.latex_fname))
    html.write('</tr>\n')

    html.write('<p>\n<tr><td><b>Individual Figures:</b></td> </tr>\n')
    for pageitem in ppd.pageitem_list:
        html.write("""
           <td>%s</td>
           <td><a href="%s">html</a></td>
           <td><a href="%s">%s</a></td><tr>
           """ % (pageitem.html_index_entry, \
                  pageitem.hname,\
                  pageitem.fname, pageitem.fname))
    html.write('</table>\n')
    html.write('</body></html>')

    #----------------------------------------------------------------------

    # allfigures.html
    #-------------------
    html = open('allfigures.html', 'w')
    html.write("""
          <html><meta http-equiv="expires" content="0">
          <title>Plots</title>
          <p>
          <h1>All figures</h1>
          <p>
          <h3><a href=%s>Return to Plot Index</a> </h3>
          <p>
          <h3>Click on a figure to enlarge</h3>
          <p>
        """ % ppd.html_index_fname)

    for pageitem in ppd.pageitem_list:
        html.write('  <a href="%s"><img src="%s" width=400></a>\n' \
                % (pageitem.hname, pageitem.fname))

    html.write('\n<p><h3><a href=%s>Return to Plot Index</a> </h3>' \
                % ppd.html_index_fname)
    html.write('\n</center></body></html>\n')
    html.close()


    # individual html files for each figure
    #--------------------------------------

    for j in range(len(ppd.pageitem_list)):
        pageitem = ppd.pageitem_list[j]
        html = open(pageitem.hname, 'w')
        html.write("""
              <html><meta http-equiv="expires" content="0">
              <title>%s</title>
              <p>
              <h1>%s</h1>
              <p>

              <p>
            """ % (pageitem.html_index_entry,pageitem.html_index_entry))

        html.write("""
              <p><img src="%s" ><p>
              <h3><a href=%s>Return to Plot Index</a>
            """ % (pageitem.fname,ppd.html_index_fname))
        if j>0:
            html.write("&nbsp; ... &nbsp;  <a href=%s>Previous Figure</a> "\
                   % ppd.pageitem_list[j-1].hname)
        if j<len(ppd.pageitem_list)-2:
            html.write("&nbsp; ... &nbsp;  <a href=%s>Next Figure</a> "\
                   % ppd.pageitem_list[j+1].hname)
        html.write("\n</h3>")

    html.write('\n</center></body></html>\n')
    html.close()

    os.chdir(startdir)
    # end of plots2html


#======================================================================
def print_html_pointers(path_to_html_index):
#======================================================================
    #PlotPath = os.getcwd()
    #if PlotPath[0] != '/':
        #PlotPath = '/' + PlotPath
    #PlotPath.replace('\\','/') # for windows

    # check if path appears to be in format of SageMathCloud:
    smc_user = (path_to_html_index[:9] == '/projects') \
             & (path_to_html_index[18] == '-')

    if smc_user:
        # For SageMathCloud only:  modify the path to be of the form that can
        # be opened in a browser window to view the html files
        s1 = path_to_html_index.replace('/projects','https://cloud.sagemath.com')
        path_to_html_index = s1[:64] + 'raw/' + s1[64:]
    else:
        # make the URL point to a local file:
        path_to_html_index = 'file://' + path_to_html_index

    print("\n--------------------------------------------------------")
    print("\nPoint your browser to:")
    print("    %s" % path_to_html_index)

    clawdir = os.getenv('CLAW','')

    # Removed next message since clawpack server is rarely used...
    #if clawdir in path_to_html_index:
    if False:
        path_to_html_index = path_to_html_index.replace(clawdir,'')
        print("\nOr, if you have the Clawpack server running, point your browser to:")
        print("    http://localhost:50005%s"  % path_to_html_index)



#=====================================
def htmlmovie(html_index_fname,pngfile,framenos,figno):
#=====================================
    """
    Input:
     pngfile: a dictionary indexed by (frameno,figno) with value the
              corresponding png file for this figure.
     framenos: a list of frame numbers to include in movie
     figno: integer with the figure number for this movie.

    Returns:
     text for an html file that incorporates javascript to loop through the
          plots one after another.

    New 6/7/10: The html page also has buttons for controlling the movie.

    The parameter iterval below is the time interval between loading
    successive images and is in milliseconds.

    The img_width and img_height parameters do not seem to have any effect.
    """


    text = """
           <html>
           <head>
           <script language="Javascript">
           <!---
           var num_images = %s; """ % len(framenos)

    text += """
           var img_width = 800;
           var img_height = 600;
           var interval = 300;
           var images = new Array();


        function preload_images()
        {
            t = document.getElementById("progress");
            """

    i = 0
    for frameno in framenos:
        i = i+1
        text += """
        t.innerHTML = "Preloading image ";
        images[%s] = new Image(img_width, img_height);
        images[%s].src = "%s";
        """ % (i,i,pngfile[frameno,figno])
    text += """
        t.innerHTML = "";
        }

        function tick()
        {
          frame += 1;
          if (frame > num_images+1)
              frame = 1;

          document.movie.src = images[frame].src;
          tt = setTimeout("tick()", interval);
        }

        function startup()
        {
          preload_images();
          frame = 1;
          document.movie.src = images[frame].src;
        }
        function rewind()
        {
          frame = 1;
          document.movie.src = images[frame].src;
        }
        function start()
        {
          tt = setTimeout("tick()", interval);
        }
        function pause()
        {
          clearTimeout(tt);
        }
        function restart()
        {
          tt = setTimeout("tick()", interval);
        }
        function slower()
        {
          interval = interval / 0.7;
        }
        function faster()
        {
          interval = interval * 0.7;
        }

        // --->
        </script>
        </head>
        <body onLoad="startup();">

        <form>
        &nbsp;&nbsp;&nbsp;
        <input type="button" value="Start movie" onClick="start()">
        <input type="button" value="Pause" onClick="pause()">
        &nbsp;&nbsp;&nbsp;
        <input type="button" value="Rewind" onClick="rewind()">
        &nbsp;&nbsp;&nbsp;
        <input type="button" value="Slower" onClick="slower()">
        <input type="button" value="Faster" onClick="faster()">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="%s">Plot Index</a>
        </form>

        <p><div ID="progress"></div></p>
          <img src="%s" name="movie"/>

        </body>
        </html>
        """ % (html_index_fname,pngfile[framenos[0],figno])

    return text
    # end of htmlmovie


#======================================================================
def plots2latex(plot_pages_data):
#======================================================================
    """
    Take a list of figure files and produce latex file to display them.
    So far only works with time frames, not with gauges or other plots.
    """

    print('\n-----------------------------------\n')
    print('\nCreating latex file...\n')
    startdir = os.getcwd()
    ppd = plot_pages_data
    plotdir = ppd.plotdir
    numitems = len(ppd.pageitem_list)   # number of page items (separate plots)

    if numitems == 0:
        print('*** Warning: 0 plots to put in latex file')
        print('No latex file generated')
        return


    try:
        cd_with_mkdir(ppd.plotdir, ppd.overwrite, ppd.verbose)
    except:
        print("*** Error, aborting plots2latex")
        raise


    creationtime = current_time()

    latexfile = open(ppd.latex_fname + '.tex', 'w')

    # latex header
    #-------------

    latexfile.write(r"""
        \documentclass[11pt]{article}
        \usepackage{graphicx}
        \setlength{\textwidth}{7.5in}
        \setlength{\oddsidemargin}{-0.5in}
        \setlength{\evensidemargin}{-0.5in}
        \setlength{\textheight}{9.2in}
        \setlength{\voffset}{-1in}
        \setlength{\headsep}{5pt}
        \begin{document}
        \begin{center}{\Large\bf %s}\vskip 5pt
        """ % ppd.latex_title)

    latexfile.write(r"""
        \bf Plots created {\tt %s} in directory: \vskip 5pt
        \verb+%s+
        \end{center}
        \vskip 5pt
        """ % (creationtime, startdir))

    # latex layout
    #-------------

    itemsperline = ppd.latex_itemsperline
    if itemsperline == 'all': itemsperline = numitems
    itemsperpage = ppd.latex_itemsperpage
    if itemsperpage == 'all': itemsperpage = numitems

    # width each plot must be:
    fwidth = 0.95/itemsperline

    # latex for each item:
    #---------------------

    itemlinecnt = 0
    itempagecnt = 0
    for pageitem in ppd.pageitem_list:
        if itempagecnt >= itemsperpage:
            latexfile.write('\\newpage \n')
            itempagecnt = 0
            itemlinecnt = 0
        elif itemlinecnt >= itemsperline:
            latexfile.write('\\vskip 10pt \n')
            itemlinecnt = 0
        itemlinecnt += 1
        itempagecnt += 1
        if pageitem.latex_preitem:
            latexfile.write(pageitem.latex_preitem)
        latexfile.write('\\includegraphics[width=%s\\textwidth]{%s}\n' \
                            % (fwidth,pageitem.fname))
        #latexfile.write('\\vskip 10pt \n')
    latexfile.write('\\end{document}\n')
    latexfile.close()
    print("\nLatex file created:  ")
    print("  %s/%s.tex" % (plotdir, ppd.latex_fname))
    print("\nUse pdflatex to create pdf file")

    if ppd.latex_makepdf:
        try:
            os.system('pdflatex %s' % ppd.latex_fname)
            print("\nSuccessfully created pdf file:  %s/%s.pdf" \
                   % (plotdir, ppd.latex_fname))
        except:
            print('*** pdflatex command failed')

    os.chdir(startdir)
    # end of plots2latex


#======================================================================
def plotclaw2kml(plotdata):
#======================================================================
    """
    Take a list of figure files and produce kml file to display them.

    # Files that get created :

      _GoogleEarthfig?.kmz : Zipped file containing all files, including doc.kml
      _GoogleEarthfig?.kml : Network links to remote images
                gauges.kml : Gauge Placemarks
               regions.kml : Region polygons
                levels.kml : Patch border polygons


    """

    print(" ")
    print("KML ===> Creating file %s.kmz" % plotdata.kml_index_fname)

    startdir = os.getcwd()

    from lxml import etree
    from pykml.factory import KML_ElementMaker as KML
    from pykml.factory import GX_ElementMaker as GX
    from pykml.factory import ATOM_ElementMaker as ATOM
    import zipfile
    import shutil
    from copy import deepcopy
    from clawpack.geoclaw import kmltools

    if plotdata.format == 'forestclaw':
        level_base = 0
    else:
        level_base = 1

    try:
        cd_with_mkdir(plotdata.plotdir, plotdata.overwrite, plotdata.verbose)
    except:
        print("KML ===> Error, aborting plotclaw2kml (cannot create plot directory")
        raise

    gaugenos = plotdata.gauges_gaugenos
    if gaugenos is not None:
        if plotdata.gauges_fignos is not None:
            plotdata = massage_gauges_data(plotdata)
            gauge_pngfile = plotdata._gauge_pngfile

    creationtime = current_time()
    plotdata = massage_frames_data(plotdata)

    framenos = plotdata.timeframes_framenos
    frametimes = plotdata.timeframes_frametimes
    fignos = plotdata.timeframes_fignos
    fignames = plotdata.timeframes_fignames
    pngfile = plotdata._pngfile
    htmlfile = plotdata._htmlfile
    frametimef = plotdata._frametimef
    allfigsfile = plotdata._allfigsfile
    allframesfile = plotdata._allframesfile

    numframes = len(framenos)
    numfigs = len(fignos)
    creationtime = current_time()

    # ------------------- get time span ----------------------

    # Collect time spans for use in several places.
    TS = []
    event_time = plotdata.kml_starttime
    tz = plotdata.kml_tz_offset
    tscale = plotdata.kml_time_scale

    if numframes == 1:
        frameno = framenos[0]
        t1 = frametimes[frameno]
        t2 = t1 + 5  # Add time second so final figure shows up
        sbegin, send = kmltools.kml_timespan(t1,t2,event_time,tz,tscale=tscale)

        # To be used below
        TS.append(KML.TimeSpan(
            KML.begin(sbegin),
            KML.end(send)))
    else:
        for i in range(0,numframes):
            frameno = framenos[i]
            t1 = frametimes[frameno]
            if i < numframes-1:
                t2 = frametimes[framenos[i+1]]
            else:
                # We could add 1 second at the end, or more time, depending on what
                # effect is desired. In any case, the time span can't be empty or the
                # last figure won't show up.
                dt = (frametimes[framenos[numframes-1]] - frametimes[framenos[0]])/numframes
                t2 = t1 + dt   # Add enough time for looping through animations
                print("Final time in Google Earth slider set to {:6.2f}".format(t2))

            sbegin, send = kmltools.kml_timespan(t1,t2,event_time,tz,tscale=tscale)

            TS.append(KML.TimeSpan(
                KML.begin(sbegin),
                KML.end(send)))


    # Top level doc.kml file
    doc = KML.kml(
        KML.Document(
            KML.name(plotdata.kml_name),
            KML.open(1)))

    # Open main zip file
    zip = zipfile.ZipFile(plotdata.kml_index_fname + ".kmz",'w',allowZip64=True)

    # --------------------- Set initial view --------------------------
    first_found = False
    for i,figname in enumerate(plotdata._fignames):
        plotfigure = plotdata.plotfigure_dict[figname]
        figno = plotfigure.figno

        if not figno in fignos:
            continue

        if not plotfigure.use_for_kml:
            continue

        # Get a view that is used when GE first loads.
        if plotfigure.kml_use_for_initial_view or not first_found:
            x1 = plotfigure.kml_xlimits[0]
            x2 = plotfigure.kml_xlimits[1]
            y1 = plotfigure.kml_ylimits[0]
            y2 = plotfigure.kml_ylimits[1]
            ulinit = np.array([plotfigure.kml_xlimits[0], plotfigure.kml_ylimits[1]])
            urinit = np.array([plotfigure.kml_xlimits[1], plotfigure.kml_ylimits[1]])
            lrinit = np.array([plotfigure.kml_xlimits[1], plotfigure.kml_ylimits[0]])

            R = 6371.0   # radius of earth
            domain_width = R*np.cos(abs(y1+y2)*np.pi/360.0)*(x2-x1)*np.pi/180.0
            dist_factor = 2  # factor by which height should exceed width
            initial_height = min([1000*dist_factor*domain_width,9656064.0])   # <= 6000 miles

            initial_view = KML.LookAt(
                KML.longitude((ulinit[0]+urinit[0])/2),
                KML.latitude((urinit[1]+lrinit[1])/2),
                KML.tilt(0),
                KML.range(initial_height))   # in meters?

            doc.Document.append(deepcopy(initial_view))

            # we found something;  any other figures will have to have
            # 'kml_use_for_initial_view' set to override this view.
            first_found = True

    # ------------------- Loop over figures ----------------------

    fig_folder = KML.Folder(
        KML.name("Figures"),
        KML.open(1))

    for figname in plotdata._fignames:

        plotfigure = plotdata.plotfigure_dict[figname]
        figno = plotfigure.figno

        if not figno in fignos:
            continue

        if not plotfigure.use_for_kml:
            continue

        fig_dir = "fig" + str(figno)

        if plotfigure.kml_show_figure:
            fig_vis = 1
        else:
            fig_vis = 0

        shutil.rmtree(fig_dir,True)
        os.mkdir(fig_dir)

        doc_fig = KML.kml(
            KML.Document(
                KML.name(plotfigure.name),
                KML.open(0),
                KML.Folder(
                    KML.name("Frames"))))

        # Needed for each figure
        ul = np.array([plotfigure.kml_xlimits[0], plotfigure.kml_ylimits[1]])
        ur = np.array([plotfigure.kml_xlimits[1], plotfigure.kml_ylimits[1]])
        lr = np.array([plotfigure.kml_xlimits[1], plotfigure.kml_ylimits[0]])

        # Shift so plots that cross the 180 meridian, rather than the -180 Meridian
        if ul[0] < -180:
            ul[0] = ul[0] + 360
            ur[0] = ur[0] + 360
            lr[0] = lr[0] + 360

        # ------------------- Loop over frames ----------------------
        # This will get created for each figure, but I need it
        # for createing the level boxes around each patch

        for i in range(0,numframes):
            frameno = framenos[i]

            fname = 'frame' + str(frameno).rjust(4, '0')
            fname_str = fname + 'fig%s' % figno


            # ------------------- create subdirs with images ----------------------
            if (not plotfigure.kml_tile_images):
                print("KML ===> Adding %s.png to %s.kmz" \
                    " file (no tiling)" % (fname_str,plotdata.kml_index_fname))

                # The 'etree'
                doc_notile = KML.kml(KML.Document())

                c = TS[i].getchildren()
                desc = "t = %g\n" % frametimes[frameno] + c[0]

                fstr = "%s.png" % fname_str
                doc_notile.Document.append(
                    KML.GroundOverlay(
                        KML.name(fstr),
                        KML.Icon(KML.href(fstr)),
                        KML.LatLonBox(
                            KML.north(ur[1]),
                            KML.south(lr[1]),
                            KML.east(ur[0]),
                            KML.west(ul[0]))))

                # Easier to just move into this directory to construct everything
                os.chdir(fig_dir)

                shutil.rmtree(fname_str,True)  # remove directory and ignore errors
                os.mkdir(fname_str)

                # PNG file gets moved into subdirectory and will eventually be
                # zipped into KMZ file.
                if plotdata.html:
                    shutil.copy(os.path.join("..","%s.png" % fname_str),fname_str)
                else:
                    shutil.move(os.path.join("..","%s.png" % fname_str),fname_str)

                # The actual file to be written <framename>/doc.kml
                docfile = os.path.join(fname_str,'doc.kml')
                docfile_notile = open(os.path.join(fname_str,'doc.kml'),'wt')
                docfile_notile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                kml_text = etree.tostring(etree.ElementTree(doc_notile),
                                                        pretty_print=True)
                docfile_notile.write(kml_text.decode())
                docfile_notile.close()

                os.chdir("..")

            else:
                print(" ")
                print("KML ===> Tiling %s.png" % fname_str)

                os.chdir(fig_dir)
                pngfile = os.path.join("..","%s.png"% fname_str)
                shutil.copy(pngfile,".")
                im = plt.imread("%s.png" % fname_str)
                sx = im.shape[1]   # reversed?
                sy = im.shape[0]

                arg_list = ["gdal_translate", "-of", "VRT", \
                            "-a_srs", "EPSG:4326",  \
                            "-gcp", "0",         "0",        "%f"%(ul[0]),   "%f"%(ul[1]), \
                            "-gcp", "%d"%(sx),   "0",        "%f"%(ur[0]),   "%f"%(ur[1]), \
                            "-gcp", "%d"%(sx),   "%d"%(sy),  "%f"%(lr[0]),   "%f"%(lr[1]), "-90", \
                            "%s.png"%(fname_str), "%s_tmp.vrt"%(fname_str)]

                import subprocess
                retval = subprocess.call(arg_list)

                arg_list = ["gdalwarp", "-of", "VRT", "-t_srs", "EPSG:4326 ", "-overwrite", \
                            "%s_tmp.vrt"%(fname_str), "%s.vrt"%(fname_str)]
                retval = retval or subprocess.call(arg_list)

                arg_list = ["gdal2tiles.py", \
                            "--profile=geodetic", \
                            "--force-kml", \
                            "--resampling=near", \
                            "%s.vrt" % (fname_str)]

                retval = retval or subprocess.call(arg_list)

                if retval > 0:
                    print("KML ===> gdal : something went wrong!\n")
                    sys.exit(1)

                # Change back to top level directory before adding zipped files
                os.chdir("..")

                # Add the <fname>.vrt file to zipped file. Remove
                # figure PNG file
                zip.write(os.path.join(fig_dir,"%s.vrt" % fname_str))

                # Leave the PNG file in the KMZ file?
                # os.remove(os.path.join(fig_dir,"%s.png" % fname_str))

                # Clean up files
                os.remove(os.path.join(fig_dir,"%s_tmp.vrt" % fname_str))
                os.remove(os.path.join(fig_dir,"%s.vrt" % fname_str))


            # add Network link to high level doc.kml file.  This will referenece either
            # tiled files or non-tiled files.
            c = TS[i].getchildren()
            desc = "Time : t = %g\n" \
                   "UTC  : %s\n"\
                   "File : %s.png" % (frametimes[frameno],c[0],fname_str)

            # Description in Places panel
            snippet_str = "<![CDATA[<b><pre>%s</pre></b>]]>" % desc

            # Data that shows up in balloon
            desc_style = "<b><pre><font style=\"font-size:10pt\">%s</font></pre></b>" % desc
            desc_str = "<![CDATA[%s]]>" % desc_style

            lstr = os.path.join(fname_str,'doc.kml')
            doc_fig.Document.Folder.append(
                KML.NetworkLink(
                    KML.name("Frame %d" % frameno),
                    KML.Snippet(snippet_str,maxLines="2"),
                    KML.description(desc_str),
                    deepcopy(TS[i]),
                    KML.Link(KML.href(lstr))))

        # ----------------- Done with frame loop --------------------

        lstr = os.path.join(fig_dir,"doc.kml")
        fig_folder.append(
            KML.NetworkLink(
                KML.name("%s (%d)" % (figname,figno)),
                KML.visibility(fig_vis),
                KML.Link(
                    KML.href(lstr))))

        # fig_vis = 0   # All figures referenced after the first one will not be shown
                        # when first loading GE.


        # -------------- add colorbar image file -----------------
        # Build the colorbar.
        if plotfigure.kml_colorbar is not None:
            print(" ")
            print("KML ===> Building colorbar for figure %s" % plotfigure.name)
            cb_img = "images"
            cb_dir = os.path.join(fig_dir,cb_img)
            shutil.rmtree(cb_dir,True)
            os.mkdir(cb_dir)
            cb_filename = "colorbarfig%s.png" % figno
            try:
                plotfigure.kml_colorbar(cb_filename)
                shutil.move(cb_filename,cb_dir)
            except:
                print("KML ===> Warning : Something went wrong when creating colorbar")

            # add link to KML file, even if colorbar didn't get created.
            cb_str = os.path.join(cb_img,cb_filename)
            colorbar = KML.ScreenOverlay(
                KML.name("Colorbar"),
                KML.Icon(KML.href(cb_str)),
                KML.overlayXY(x="0.025", y="0.05", xunits="fraction", yunits="fraction"),
                KML.screenXY(x="0.025", y="0.05",xunits="fraction", yunits="fraction"))

            doc_fig.Document.append(colorbar)
            # -----  Done with colorbar ------

        # ------------------ done with fig<N>/doc.kml file ------------------
        fig_file = open(os.path.join(fig_dir,"doc.kml"),'wt')
        fig_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')

        # In case we used CDATA in any snippets or descriptions.  For some reason
        # <tags> get converted to &gt;tags&lt;, which balloons don't translate.
        kml_text = etree.tostring(etree.ElementTree(doc_fig),pretty_print=True).decode()
        kml_text = kml_text.replace('&gt;','>')
        kml_text = kml_text.replace('&lt;','<')
        fig_file.write(kml_text)
        fig_file.close()
        # Done with fig<n>/doc.kml file


        # Clean up everything in the figure directory
        for dirname, subdirs, files in os.walk(fig_dir):
            zip.write(dirname)
            for filename in files:
                zip.write(os.path.join(dirname, filename))
                #print('++++ writing %s' % os.path.join(dirname, filename))

        shutil.rmtree(fig_dir)


    # ---------------------- Done with figure loop ------------------

    # Add "Figures" folder to doc.kml
    doc.Document.append(deepcopy(fig_folder))


    # ---------- Create top-level resource subdirectories -----------
    kml_dir = 'kml'
    shutil.rmtree(kml_dir,True)  # remove directory and ignore errors
    os.mkdir(kml_dir)

    img_dir = 'images'
    shutil.rmtree(img_dir,True)  # remove directory and ignore errors
    os.mkdir(img_dir)

    # ------------------ Creating gauges.kml file -------------------------
    gauge_kml_file = "gauges.kml"

    print(" ")
    print("KML ===> Creating file %s" % gauge_kml_file)

    has_gauge_data = True
    try:
        setgauges = gaugetools.read_setgauges(plotdata.outdir)
    except:
        print("     File gauges.data not found - this should not happen.")
        has_gauge_data = False

    if has_gauge_data and gaugenos is not None and len(gaugenos) > 0:
        gauges = setgauges.gauges

        # Location of gauges PNG files (stored under <file>.kmz/images
        basehref = "<base href=\"%s\"/>" % os.path.join('..','..','images','')  # need trailing "/"

        # Format the text in the Placemark balloon.
        btext = \
                "<style media=\"screen\" type=\"text/css\">" \
                "pre {font-weight:bold;font-style:12pt}" + \
                "span.title {font-weight:bold;font-size:12pt} " + \
                "</style>" + \
                "%s" % basehref + \
                "<center><span class=\"title\">$[name]</span></center>" + \
                "<pre>" + \
                "Time     : t1 = $[t1], t2 = $[t2]\n" + \
                "Location : x1 = $[x1], y1 = $[y1]\n" + \
                "</pre>" + \
                "<center><img style=\"width:500\" src=\"$[pngfile]\"/></center>" + \
                "<pre><b>File : $[pngfile]</pre>"

        # the 'text' tag will replace Placemark description
        bstyle = KML.text("<![CDATA[%s]]>" % btext)

        # Start builing KML document
        doc_gauges = KML.kml(KML.Document())

        # Only one style for all of the gauges
        doc_gauges.Document.append(KML.Style(
            KML.BalloonStyle(bstyle),
            id="gauge_style"))

        # Loop over all gauges
        for gnum,gauge in enumerate(gauges):
            gaugeno = int(gauge[0])
            if plotdata.print_gaugenos != 'all':
                if gaugeno not in plotdata.print_gaugenos:
                    #print('+++ skipping gauge %i, not in print_gaugenos' % gaugeno)
                    continue # to next gauge
            t1,t2 = gauge[3:5]
            x1,y1 = gauge[1:3]
            if plotdata.kml_map_topo_to_latlong is not None:
                x1,y1 = plotdata.kml_map_topo_to_latlong(x1,y1)

            # Get proper coordinates, otherwise placemark doesn't show up.
            if x1 > 180:
                longitude = x1 - 360
            elif x1 < -180:
                longitude = x1 + 360
            else:
                longitude = x1

            print("Gauge %i: %10.6f  %10.6f  \n" % (gaugeno,x1,y1) \
                + "  t1 = %10.1f,  t2 = %10.1f" % (t1,t2))

            # plotdata.gauges_fignos
            # Not clear how to get the figure number for each gauge.   Assume that
            # there is only one figure number figno for all gauges
            # If user has set 'gaugeno=[]', gauge files will not be added to the KMLfile. 
            
            if plotdata.gauges_fignos is not None:
                figno = plotdata.gauges_fignos[0] # use just the first
                
            figname = gauge_pngfile[gaugeno,figno]

            elev = 0
            coords = "%10.4f %10.4f %10.4f" % (longitude,y1,elev)

            # Text for 'Places' panel
            snippet = "t1 = %g, t2 = %g\n" % (t1,t2) + \
                      "x1 = %g, y1 = %g\n" % (x1,y1)
            snippet_str = "<![CDATA[<pre><b>%s</b></pre>]]>" % snippet

            # ExtendedData is used in BalloonStyle.text() fields.
            placemark = KML.Placemark(
                KML.name("%s %d" % (plotfigure.kml_gauge_name,gaugeno)),
                KML.Snippet(snippet_str),
                KML.styleUrl(chr(35) + "gauge_style"),
                KML.ExtendedData(
                    KML.Data(KML.value(figname),name="pngfile"),
                    KML.Data(KML.value("%g" % t1),name="t1"),
                    KML.Data(KML.value("%g" % t2),name="t2"),
                    KML.Data(KML.value("%g" % x1),name="x1"),
                    KML.Data(KML.value("%g" % y1),name="y1")),
                KML.Point(
                    KML.coordinates(coords)))

            doc_gauges.Document.append(placemark)

        kml_file = open(gauge_kml_file,'wt')
        kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')

        kml_text = etree.tostring(etree.ElementTree(doc_gauges),
                                  pretty_print=True).decode()
        kml_text = kml_text.replace('&gt;','>')   # Needed for CDATA blocks
        kml_text = kml_text.replace('&lt;','<')

        kml_file.write(kml_text)
        kml_file.close()

    # -------------- add gauge image and KML files -----------------
    if plotdata.gauges_fignos is None:
        gauge_vis = 0
    else:
        gauge_vis = 1
    doc.Document.append(
        KML.NetworkLink(
            KML.name("Gauges"),
            KML.visibility(gauge_vis),
            KML.Link(KML.href(os.path.join(kml_dir,
                                           gauge_kml_file)))))

    if os.path.isfile(gauge_kml_file):
            shutil.move(gauge_kml_file,kml_dir)

    # Add any gauge PNG files to images directory.
    if plotdata.gauges_fignos is not None:
        for k in gauge_pngfile.keys():
            if os.path.isfile(gauge_pngfile[k]):
                shutil.copy(gauge_pngfile[k],img_dir)


    # ----------------- Add a region for the computational domain ----------

    # Top level regions.kml file
    doc_regions = KML.kml(KML.Document())
    region_kml_file = "regions.kml"

    # collect all the placemarks in a folder and append later
    placemark_folder = []

    # Read claw.data to get computational domain
    print(" ")
    print("KML ===> Creating file %s" % region_kml_file)
    try:
        f = open(os.path.join(plotdata.outdir,"claw.data"),'r')
    except:
        # We don't have the dimensions of the full domain
        print("     Cannot find claw.data. Region for the computational domain will not be created.")
    else:
        # Read past comments;  last 'l' is blank line
        l = f.readline()
        while (l.startswith('#')):
            l = f.readline()

        # read line containing number of gauges
        l = f.readline()
        # read lower
        c = f.readline()
        lower = np.fromstring(c.strip(),sep=' ')
        c = f.readline()
        upper = np.fromstring(c.strip(),sep=' ')
        if plotdata.kml_map_topo_to_latlong is not None:
            x1,y1 = plotdata.kml_map_topo_to_latlong(lower[0],lower[1])
            x2,y2 = plotdata.kml_map_topo_to_latlong(upper[0],upper[1])
        else:
            x1 = lower[0]
            x2 = upper[0]
            y1 = lower[1]
            y2 = upper[1]

        bcomp_domain = \
                       "<style media=\"screen\" type=\"text/css\">" \
                       "pre {font-weight:bold;font-style:12pt}" + \
                       "span.title {font-weight:bold;font-size:12pt} " + \
                       "</style>" + \
                       "<center><span class=\"title\">Computational Domain</span></center>" + \
                       "<pre>" + \
                       "Location : x1 = $[x1], x2 = $[x2]\n" + \
                       "           y1 = $[y1], y2 = $[y2]\n" + \
                       "</pre>"

        domain_text =  KML.text("<![CDATA[%s]]>" % bcomp_domain)


        print("Computational domain : %10.6f  %10.6f  %10.6f  %10.6f" \
            % (x1,x2,y1,y2))
        snippet_str = \
                  "x1 = %g, x2 = %g\n" % (x1,x2) + \
                  "y1 = %g, y2 = %g\n" % (y1,y2)
        snippet = "<![CDATA[<b><pre>%s</pre></b>]]>" % snippet_str

        # Style for this region
        doc_regions.Document.append(
            KML.Style(
                KML.PolyStyle(
                    KML.color("FF98644E"),   # light blue 4E6498
                    KML.fill(1),
                    KML.outline(0)),
                KML.BalloonStyle(deepcopy(domain_text)),
                id="comp_domain"))
        lv = []
        if x1 > 180 and x2 > 180:
            for x in [x1,x2]:
                lv.append(x - 360)
        elif x1 < -180 and x2 < -180:
            for x in [x1,x2]:
                lv.append(x + 360)
        else:
            lv = [x1,x2]   # Doesn't work for regions that straddle +/- 180.

        longitude = lv

        # rectangle with 2 corners specified
        mapping = {}
        mapping['x1'] = longitude[0]
        mapping['x2'] = longitude[1]
        mapping['y1'] = y1
        mapping['y2'] = y2
        mapping['elev'] = 0

        # The polygons tend to disappear when zooming.  One fix might be to
        # add more points to the edges of the polygon
        coords = """\
                 {x1:10.4f},{y1:10.4f},{elev:10.4f}
                 {x2:10.4f},{y1:10.4f},{elev:10.4f}
                 {x2:10.4f},{y2:10.4f},{elev:10.4f}
                 {x1:10.4f},{y2:10.4f},{elev:10.4f}
                 {x1:10.4f},{y1:10.4f},{elev:10.4f}
                 """.format(**mapping).replace(' ','')

                    # ExtendedData is used in BalloonStyle.text() fields.
        placemark = KML.Placemark(
            KML.name("Computational Domain"),
            KML.visibility(0),
            KML.Snippet(snippet,maxLines="2"),
            KML.styleUrl(chr(35) + "comp_domain"),
            KML.ExtendedData(
                KML.Data(KML.value("%g"% x1),name="x1"),
                KML.Data(KML.value("%g"% y1),name="y1"),
                KML.Data(KML.value("%g"% x2),name="x2"),
                KML.Data(KML.value("%g"% y2),name="y2")),
            KML.Polygon(
                KML.tessellate(1),
                KML.altitudeMode("clampToGround"),
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates(coords)))))

        placemark_folder.append(placemark)

    print(" ")
    # Create regions for remaining regions specifed in regions.data
    try:
        f = open(os.path.join(plotdata.outdir,"regions.data"),'r')
    except:
        print("     No regions.data file found.")
    else:
        # Read past comments;  last 'l' is blank line
        l = f.readline()
        while (l.startswith('#')):
            l = f.readline()

        # read line containing number of gauges
        l = f.readline()

        # Read the data lines containing gauge information
        regions = []
        for r in f.readlines():
            regions.append(np.fromstring(r.strip(),sep=' '))

        # Format the text in the Placemark balloon.
        btext = \
                "<style media=\"screen\" type=\"text/css\">" \
                "pre {font-weight:bold;font-style:12pt}" + \
                "span.title {font-weight:bold;font-size:12pt} " + \
                "</style>" + \
                "<center><span class=\"title\">$[name]</span></center>" + \
                "<pre>" + \
                "Levels   : minlevel = $[minlevel], maxlevel = $[maxlevel]\n" + \
                "Time     : t1 = $[t1], t2 = $[t2]\n" + \
                "Location : x1 = $[x1], x2 = $[x2]\n" + \
                "           y1 = $[y1], y2 = $[y2]\n" + \
                "\n" + \
                "From (UTC) : $[tsbegin]\n" + \
                "To   (UTC) : $[tsend]" + \
                "</pre>"

        # the 'text' tag will replace Placemark description
        balloon_text = KML.text("<![CDATA[%s]]>" % btext)

        width = 2
        box_color = "FFFFFFFF"

        # Now start creating real regions.
        for rnum,region in enumerate(regions):
            minlevel,maxlevel = region[0:2]
            t1,t2 = region[2:4]
            x1,x2,y1,y2 = region[4:]

            print("Region %i: %10.6f  %10.6f  %10.6f  %10.6f" \
                % (rnum,x1,x2,y1,y2))
            print("           minlevel = %i,  maxlevel = %i" \
                % (minlevel,maxlevel) \
                + "  t1 = %10.1f,  t2 = %10.1f" % (t1,t2))

            # get TimeSpan for region
            event_time = plotdata.kml_starttime
            tz = plotdata.kml_tz_offset
            frameno = framenos[-1]
            t2_slider = min([t2,frametimes[frameno]])   # Don't show times like 1e+9
            sbegin, send = kmltools.kml_timespan(t1,t2_slider,event_time,tz)
            TS_region = KML.TimeSpan(
                KML.begin(sbegin),
                KML.end(send))
            c = TS_region.getchildren()
            tsbegin = c[0]
            tsend = c[1]

            # Style for this region
            pathstr = "Path_region_%02d" % rnum
            doc_regions.Document.append(
                KML.Style(
                    KML.LineStyle(
                        KML.color(box_color),
                        KML.width(width)),
                    KML.PolyStyle(KML.color("000000")),
                    KML.BalloonStyle(deepcopy(balloon_text)),
                    id=pathstr))

            # Description for Places panel
            snippet_str = \
                "<b><pre>" + \
                "minlevel = %i, maxlevel = %i\n" % (minlevel,maxlevel) + \
                "t1 = %g, t2 = %g\n" % (t1,t2) +\
                "\n" + \
                "From (UTC) : %s\n" % tsbegin + \
                "To   (UTC) : %s\n" % tsend + \
                "</pre></b>"

            snippet = "<![CDATA[%s]]>" % snippet_str

            # Get x coordinates in longitude (-180 to 180).  Otherwise, the
            # polygons don't show up after zooming.
            lv = []
            if x1 > 180 and x2 > 180:
                for x in [x1,x2]:
                    lv.append(x - 360)
            elif x1 < -180 and x2 < -180:
                for x in [x1,x2]:
                    lv.append(x + 360)
            else:
                lv = [x1,x2]   # Also okay if [x1,x2] straddle 180 or -180

            longitude = lv

            # rectangle with 2 corners specified
            mapping = {}
            mapping['x1'] = longitude[0]
            mapping['x2'] = longitude[1]
            mapping['y1'] = y1
            mapping['y2'] = y2
            mapping['elev'] = 0

            # The polygons tend to disappear when zooming.  One fix might be to
            # add more points to the edges of the polygon
            coords = """\
                     {x1:10.4f},{y1:10.4f},{elev:10.4f}
                     {x2:10.4f},{y1:10.4f},{elev:10.4f}
                     {x2:10.4f},{y2:10.4f},{elev:10.4f}
                     {x1:10.4f},{y2:10.4f},{elev:10.4f}
                     {x1:10.4f},{y1:10.4f},{elev:10.4f}
                     """.format(**mapping).replace(' ','')

            # ExtendedData is used in BalloonStyle.text() fields.
            placemark = KML.Placemark(
                KML.name("Region %d" % rnum),
                KML.visibility(0),
                KML.Snippet(snippet,maxLines="2"),
                TS_region,
                KML.styleUrl(chr(35) + pathstr),
                KML.ExtendedData(
                    KML.Data(KML.value("%g"% minlevel),name="minlevel"),
                    KML.Data(KML.value("%g"% maxlevel),name="maxlevel"),
                    KML.Data(KML.value("%g"% t1),name="t1"),
                    KML.Data(KML.value("%g"% t2),name="t2"),
                    KML.Data(KML.value("%g"% x1),name="x1"),
                    KML.Data(KML.value("%g"% y1),name="y1"),
                    KML.Data(KML.value("%g"% x2),name="x2"),
                    KML.Data(KML.value("%g"% y2),name="y2"),
                    KML.Data(KML.value("%s"% tsbegin),name="tsbegin"),
                    KML.Data(KML.value("%s"% tsend),name="tsend")),
                KML.Polygon(
                    KML.tessellate(1),
                    KML.altitudeMode("clampToGround"),
                    KML.outerBoundaryIs(
                        KML.LinearRing(
                            KML.coordinates(coords)))))


            placemark_folder.append(placemark)

    # Do we have any regions (either computational (from claw.data) or from regions.data?
    for p in placemark_folder:
        doc_regions.Document.append(p)

    kml_file = open(region_kml_file,'wt')
    kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    kml_text = etree.tostring(etree.ElementTree(doc_regions),
                              pretty_print=True).decode()
    kml_text = kml_text.replace('&gt;','>')  # needed for CDATA blocks
    kml_text = kml_text.replace('&lt;','<')
    kml_file.write(kml_text)

    kml_file.close()

    # -------------------- Add link to regions.kml file to top level doc.kml
    # Note that we do this, even if a regions.kml file wasn't created.
    doc.Document.append(
        KML.NetworkLink(
            KML.name("Regions"),
            KML.visibility(0),
            KML.Link(KML.href(os.path.join(kml_dir,
                                           region_kml_file)))))

    if os.path.isfile(region_kml_file):
            shutil.move(region_kml_file,kml_dir)

    # --------------- Create polygons for AMR patch borders --------------
    level_kml_file = "levels.kml"
    print(" ")
    print("KML ===> Creating file %s" % level_kml_file)

    try:
        # set maxlevels by reading amr_levels_max from amr.data
        from clawpack.clawutil.data import ClawData
        amrdata = ClawData()
        amrdata.read(os.path.join(plotdata.outdir, "amr.data"), force=True)
        maxlevels = amrdata.amr_levels_max
    except:
        print('*** failed to read amrdata for maxlevels')
        # Nothing terrible happens;  we just set maxlevels to some large value
        maxlevels = 20


    # set _outdirs attribute to be list of all outdirs for all items
    plotdata.set_outdirs()

    level_dir = "levels"
    shutil.rmtree(level_dir,True)
    os.mkdir(os.path.join(kml_dir,level_dir))

    # Level colors, in (alpha, blue, green, red)
    black = ["FF000000"]
    white = ["FFFFFFFF"]
    ge_theme = ["FFCEC0C4", "FF476653", "FF9C5E4D", "#FF536F92",
                "#FF9CC2CC", "FF935B47","FF000000"]
    colorcube = ["FF0000FF", "FF00FF00","FFFFFFFF","FF000000","FFFFFF00",
              "FFFF00FF","FF00FFFF","FFFF0000"]

    # Color scheme to use for level patch borders.
    colors = black
    width = 1

    # Create high level 'levels.kml' file
    level_files = []
    doc_levels = []
    styles = []

    # Assume that if we are using ForestClaw, that we have set maxlevels correctly
    for i in range(0,maxlevels+1-level_base):
        level_file_name = "level_" + str(i+level_base).rjust(2,'0')
        level_files.append(level_file_name)

        # KML Document for each level
        doc_levels.append(KML.kml(KML.Document()))

        # Styles for levels
        styles.append(KML.Style(
            KML.LineStyle(
                KML.color(colors[i % len(colors)]),   # cycle through colors
                KML.width(width)),
            KML.PolyStyle(KML.color("00000000")),
            id="patchborder"))


    # Create individual level files in subdirectories

    doc_frames = [[0 for j in range(numframes)] for i in range(0,maxlevels+1-level_base)]
    for j in range(0,numframes):
        frameno = framenos[j]
        for i in range(0,maxlevels+1-level_base):
            frame_file_name = level_files[i] + "_" + str(frameno).rjust(4,'0') + ".kml"
            if i == 0:
                vis = 0  # Don't show first level
            else:
                vis = 1

            N = KML.NetworkLink(
                KML.name("Frame %s" % str(frameno).rjust(4,'0')),
                KML.visibility(vis),
                deepcopy(TS[j]),
                KML.Link(
                    KML.href(os.path.join(level_files[i],frame_file_name))))
            doc_levels[i].Document.append(deepcopy(N))


            # Create files in each subdirectory
            doc_frames[i][j] = KML.kml(KML.Document())
            doc_frames[i][j].Document.append(deepcopy(styles[i]))

    print("     Re-reading output files to get patch information")
    print(" ")
    for j in range(0,numframes):
        frameno = framenos[j]

        framesolns = []
        # loop over all outdirs:
        if len(plotdata._outdirs) == 0:
            plotdata._outdirs = [plotdata.outdir]

        for outdir in plotdata._outdirs:
            framesolns.append(plotdata.getframe(frameno, outdir))

        if type(framesolns) is not list:
            framesolns = [framesolns]

        for k, framesoln in enumerate(framesolns):  # patches?
            for stateno,state in enumerate(framesoln.states):
                patch = state.patch
                xlower = patch.dimensions[0].lower
                xupper = patch.dimensions[0].upper
                ylower = patch.dimensions[1].lower
                yupper = patch.dimensions[1].upper
                level = patch.level

                if plotdata.kml_map_topo_to_latlong is not None:
                    xlower,ylower = plotdata.kml_map_topo_to_latlong(xlower,ylower)
                    xupper,yupper = plotdata.kml_map_topo_to_latlong(xupper,yupper)

                lv = []
                if xlower > 180:
                    for x in [xlower,xupper]:
                        lv.append(x - 360)
                elif xupper < -180:
                    for x in [xlower,xupper]:
                        lv.append(x + 360)
                else:
                    # Not quite sure why this works in the case when x1,x2 cross 180 ...
                    lv = [xlower,xupper]

                mapping = {}
                mapping["x1"] = lv[0]
                mapping["y1"] = ylower
                mapping["x2"] = lv[1]
                mapping["y2"] = yupper
                mapping["elev"] = 0

                border_text = """
                {x1:10.4f},{y1:10.4f},{elev:10.4f}
                {x2:10.4f},{y1:10.4f},{elev:10.4f}
                {x2:10.4f},{y2:10.4f},{elev:10.4f}
                {x1:10.4f},{y2:10.4f},{elev:10.4f}
                {x1:10.4f},{y1:10.4f},{elev:10.4f}
                """.format(**mapping).replace(' ','')

                r = KML.Polygon(
                    KML.tessellate(1),
                    KML.altitudeMode("clampToGround"),
                    KML.outerBoundaryIs(
                        KML.LinearRing(
                            KML.coordinates(border_text))))


                p = KML.Placemark(
                    KML.name("Grid %d" % stateno),
                    KML.visibility(1),
                    KML.styleUrl(chr(35) + "patchborder"))

                p.append(deepcopy(r))

                try:
                    doc_frames[level-level_base][j].Document.append(deepcopy(p))
                except:
                    import pdb
                    pdb.set_trace()


    # Create directories for each level.
    for i in range(0,maxlevels+1-level_base):
        # Directory for storing levels for each time step
        shutil.rmtree(os.path.join(kml_dir,level_dir,level_files[i]),True)
        os.mkdir(os.path.join(kml_dir,level_dir,level_files[i]))


    # Print out individual frame files for each element
    for j in range(0,numframes):
        for i in range(0,maxlevels+1-level_base):
            frameno = framenos[j]
            level_file_name = level_files[i] + "_" + str(frameno).rjust(4,'0') + ".kml"
            kml_frame_file = open(os.path.join(kml_dir,level_dir,
                                               level_files[i],level_file_name),'wt')
            kml_frame_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            kml_text = etree.tostring(etree.ElementTree(doc_frames[i][j]),
                                                pretty_print=True)
            kml_frame_file.write(kml_text.decode())
            kml_frame_file.close()

    # Print out level files containing time stamps and references to frame files
    for i in range(0,maxlevels+1-level_base):
        kml_level_file = open(os.path.join(kml_dir,level_dir,level_files[i]+".kml"),'w')
        kml_level_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        kml_text = etree.tostring(etree.ElementTree(doc_levels[i]),
                                                pretty_print=True)
        kml_level_file.write(kml_text.decode())
        kml_level_file.close()

    # Folders in top level file 'levels.kml'
    doc_levels_top = KML.kml(KML.Document())
    for i in range(0,maxlevels+1-level_base):
        level_file_name = "level_" + str(i+level_base).rjust(2,'0')
        f = KML.Folder(KML.name("Level " + str(i+level_base)))
        f.append(KML.NetworkLink(
            KML.name("Frames"),
            KML.Link(
                KML.href(os.path.join(level_dir,level_file_name + ".kml")))))

        doc_levels_top.Document.append(f)

    kml_levels = open(os.path.join(kml_dir,level_kml_file),'wt')
    kml_levels.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_text = etree.tostring(etree.ElementTree(doc_levels_top),
                                    pretty_print=True).decode()
    kml_levels.write(kml_text)
    kml_levels.close()

    # Add to top level KML file
    doc.Document.append(
        KML.NetworkLink(
            KML.name("Levels"),
            KML.visibility(1),
            KML.Link(KML.href(os.path.join(kml_dir,"levels.kml")))))


    # ----------- add user-supplied KML files ------------
    user_dir = "user_files"
    shutil.rmtree(user_dir,True)
    os.mkdir(user_dir)

    if len(plotdata.kml_user_files) > 0:
        for f in plotdata.kml_user_files:
            print(" ")
            print("KML ===> Adding user KML file %s" % f[0])
            fname = f[0].partition('.')[0]
            if f[1]:
                vis = 1
            else:
                vis = 0

            shutil.copy(os.path.join("..",f[0]),user_dir)
            doc.Document.append(
                KML.NetworkLink(
                    KML.name(fname),
                    KML.visibility(vis),
                    KML.Link(KML.href(os.path.join(user_dir,f[0])))))


    # ----------- zip additional directories and clean up ------------
    dir_list = [kml_dir, img_dir, user_dir]
    for d in dir_list:
        for dirname, subdirs, files in os.walk(d):
            zip.write(dirname)
            for filename in files:
                zip.write(os.path.join(dirname, filename))

        shutil.rmtree(d)

    # ----------- Write doc.kml file --------------------
    # Top level KML file
    docfile = open("doc.kml",'wt')
    docfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    kml_text = etree.tostring(etree.ElementTree(doc),pretty_print=True).decode()
    kml_text = kml_text.replace('&gt;','>')  # needed for CDATA blocks
    kml_text = kml_text.replace('&lt;','<')
    docfile.write(kml_text)

    #docfile.write(etree.tostring(etree.ElementTree(doc),pretty_print=True))
    docfile.close()

    # Store this in the zip file and remove it.
    zip.write("doc.kml")   # Root KML file
    os.remove("doc.kml")

    zip.close()

    if plotdata.kml_publish is not None:
        print(" ")
        print("KML ===> Creating file %s.kml" % plotdata.kml_index_fname)
        # Create a KML file that can be used to link to a remote server
        update_time = 5    # minutes
        doc = KML.kml(KML.Document(
            KML.name("GeoClaw"),
            KML.visibility(1),
            KML.open(1),
            deepcopy(initial_view),
            KML.NetworkLink(
                KML.name(plotdata.kml_name),
                KML.visibility(1),
                KML.open(1),
                KML.Snippet("Updates every %d minutes" % update_time),
                KML.Link(
                    KML.href(os.path.join(plotdata.kml_publish,
                                          plotdata.kml_index_fname + ".kmz")),
                    KML.refreshMode("onInterval"),
                             KML.refreshInterval(update_time*60)))))

        file = open(plotdata.kml_index_fname + ".kml",'wt')
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        kml_text = etree.tostring(etree.ElementTree(doc),pretty_print=True)
        file.write(kml_text.decode())
        file.close()
        print(" ")

    print("KML ===> Done creating files for Google Earth.  Open " \
        "%s.kmz in the Google Earth browser" % plotdata.kml_index_fname)
    print(" ")
    os.chdir(startdir)

#   end of plotclaw2kml


#======================================================================
def cd_with_mkdir(newdir, overwrite=False, verbose=True):
#======================================================================

    newdir = os.path.abspath(newdir)
    if os.path.isfile(newdir):
        print("*** Error in cd_with_mkdir: directory specified is a file")
        raise
    elif (os.path.isdir(newdir) & overwrite):
        if verbose:
            print("Directory '%s' " % newdir)
            print("    already exists, files may be overwritten ")
    elif (os.path.isdir(newdir) & (not overwrite)):
        print("*** Error in cd_with_mkdir")
        print("Directory already exists:\n  ",newdir)
        print("Remove directory with \n '  rm -r %s' " % newdir)
        print("  and try again, or set overwrite=True ")
        raise
    else:
        try:
            os.mkdir(newdir)
            if verbose:
                print("Created directory:\n   ", newdir)
        except:
            print("*** Error in cd_with_mkdir")
            print("Cannot make directory: \n  ",newdir)
            raise
    try:
        os.chdir(newdir)
    except:
        print("*** Error in cd_with_mkdir")
        print("Cannot change directory to \n  ",newdir)


#======================================================================
def cd_plotdir(plotdir, overwrite):
#======================================================================

    verbose = False
    if os.path.isfile(plotdir):
        print("*** Error in cd_plotdir: plotdir specified is a file")
        raise
    elif (os.path.isdir(plotdir) & overwrite):
        if verbose:
            print("Directory '%s' " % plotdir)
            print("    already exists, files may be overwritten ")
    elif (os.path.isdir(plotdir) & (not overwrite)):
        print("Directory '%s'" % plotdir)
        print("  already exists")
        print("Remove directory with \n '  rm -r %s' " % plotdir)
        print("  and try again, or set overwrite=True ")
        print("*** Error in cd_plotdir")
        raise
    else:
        try:
            os.mkdir(plotdir)
        except:
            print("Cannot make directory ",plotdir)
            print("*** Error in cd_plotdir")
            raise
    try:
        os.chdir(plotdir)
    except:
        print("*** Error trying to cd to ",plotdir)


#=====================================
def massage_frames_data(plot_pages_data):
#=====================================
    ppd = plot_pages_data

    try:
        framenos = ppd.timeframes_framenos
        frametimes = ppd.timeframes_frametimes
        fignos = ppd.timeframes_fignos
        fignames = ppd.timeframes_fignames
        prefix = getattr(ppd, 'file_prefix', 'fort')
        if prefix == 'fort':
            prefix = getattr(ppd, 'timeframes_prefix', 'frame')
        if prefix != 'frame':
            prefix = prefix + 'frame'
    except:
        print('*** Error: timeframes not set properly')
        return

    startdir = os.getcwd()

    if framenos == 'all' or fignos == 'all':
        # need to determine which figures exist
        files = glob.glob('%s*.png' % prefix)
        np = len(prefix)
        if framenos == 'all':
            framenos = set()
            for file in files:
                frameno = int(file[np:(np+4)])
                framenos.add(frameno)
            framenos = list(framenos)
            framenos.sort()
        if fignos == 'all':
            fignos = set()
            for file in files:
                figno = int(os.path.splitext(file)[0][(np+7):])
                fignos.add(figno)
            fignos = list(fignos)
            fignos.sort()

    allframesfile = {}
    for figno in fignos:
        if figno not in fignames:
            fignames[figno] = 'Solution'
        allframesfile[figno] = 'allframes_fig%s.html'  % figno

    numframes = len(framenos)
    numfigs = len(fignos)

    if len(framenos) == 0:
        print('*** Warning: 0 frames to print')
    if len(fignos) == 0:
        print('*** Warning: 0 figures to print each frame')

    pngfile = {}
    htmlfile = {}
    frametimef = {}
    allfigsfile = {}
    #print '    Making png and html files for %i frames:' % numframes, framenos
    for frameno in framenos:
        framef = str(frameno).zfill(4)
        try:
            ftime = frametimes[frameno]
        except:
            ftime = '?'

        if ftime == '?':
            ftimef = ftime
        elif ((ftime == 0) | ((ftime > 0.001) & (ftime < 1000))):
            ftimef = '%9.5f' % ftime
        else:
            ftimef = '%12.5e' % ftime
        frametimef[frameno] = ftimef
        framef = str(frameno).zfill(4)
        for figno in fignos:
            pngfile[frameno,figno] = '%s%sfig%s.png'  % (prefix,framef,figno)
            htmlfile[frameno,figno] = '%s%sfig%s.html' % (prefix,framef,figno)
        allfigsfile[frameno] = '%s_allfigs%s.html' % (prefix,framef)

    ppd.timeframes_framenos = framenos
    ppd.timeframes_fignos = fignos
    ppd.timeframes_fignames = fignames
    ppd._pngfile = pngfile
    ppd._htmlfile = htmlfile
    ppd._frametimef = frametimef
    ppd._allfigsfile = allfigsfile
    ppd._allframesfile = allframesfile
    return ppd




#======================================================================
def timeframes2latex(plot_pages_data):
#======================================================================
    """
    take a sequence of figure files in format frame000NfigJ.png for
    N in framenos and J in fignos, and produce a latex file containing
    them all.
      plot_pages_data.timeframes_framenos  is list of frames to use,
      plot_pages_data.timeframes_frametimes  is dictionary of time for each frame
      plot_pages_data.timeframes_fignos  is list of figs to use,
      plot_pages_data.timeframes_fignames  is dictionary of fig names for index.
      plot_pages_data.timeframes_prefix  is the string indicating how the
                             files are named  ('frame' by default).
    """

    print('\n-----------------------------------\n')
    print('Creating latex file...')

    startdir = os.getcwd()

    ppd =plot_pages_data
    try:
        cd_with_mkdir(ppd.plotdir, ppd.overwrite, ppd.verbose)
    except:
        print("*** Error, aborting timeframes2latex")
        raise

    creationtime = current_time()
    ppd = massage_frames_data(ppd)

    plotdir = ppd.plotdir

    framenos = ppd.timeframes_framenos
    frametimes = ppd.timeframes_frametimes
    fignos = ppd.timeframes_fignos
    fignames = ppd.timeframes_fignames
    pngfile = ppd._pngfile

    numframes = len(framenos)
    numfigs = len(fignos)

    latexfile = open(ppd.latex_fname + '.tex', 'w')

    # latex header
    #-------------

    latexfile.write(r"""
        \documentclass[11pt]{article}
        \usepackage{graphicx}
        \setlength{\textwidth}{7.5in}
        \setlength{\oddsidemargin}{-0.5in}
        \setlength{\evensidemargin}{-0.5in}
        \setlength{\textheight}{9.2in}
        \setlength{\voffset}{-1in}
        \setlength{\headsep}{5pt}
        \begin{document}
        \begin{center}{\Large\bf %s}\vskip 5pt
        """ % ppd.latex_title)

    latexfile.write(r"""
        \bf Plots created {\tt %s} in directory: \vskip 5pt
        \verb+%s+
        \end{center}
        \vskip 5pt
        """ % (creationtime, startdir))

    # latex layout
    #-------------

    # determine how many plots should appear on each page and line:
    framesperpage = ppd.latex_framesperpage
    if framesperpage == 'all':
        framesperpage = len(framenos)
    framesperline = ppd.latex_framesperline
    if framesperline == 'all':
        framesperline = len(framenos)
    figsperline = ppd.latex_figsperline
    if figsperline == 'all':
        figsperline = len(fignos)
    if (figsperline < len(fignos)) & (framesperline > 1):
        print('*** Incompatible layout: resetting framesperline to 1')
        framesperline = 1
    totalperline = framesperline * figsperline
    if totalperline < 1:
        print('*** Warning: 0 figures per line requested in latex file')
        print('No latex file generated due to format error')
        return

    # width each plot must be:
    fwidth = 0.95/totalperline

    framecnt = 0
    for frameno in framenos:
        #latexfile.write('\\centerline{\Large Frame %s at time = %s' \
        #       % (frameno frametime[frameno])
        if framecnt >= framesperpage:
            latexfile.write('\\newpage \n')
            framecnt = 0
        elif framecnt >= framesperline:
            latexfile.write('\\vskip 10pt \n')
            framecnt = 0
        framecnt += 1
        figcnt = 0
        for figno in fignos:
            if figcnt >= figsperline:
                latexfile.write('\\vskip 10pt \n')
                figcnt = 0
            figcnt += 1
            latexfile.write('\\includegraphics[width=%s\\textwidth]{%s}\n' \
                            % (fwidth,pngfile[frameno,figno]))
        #latexfile.write('\\vskip 10pt \n')
    latexfile.write('\\end{document}\n')
    latexfile.close()

    print("\nLatex file created:  ")
    print("  %s/%s.tex" % (plotdir, ppd.latex_fname))
    print("\nUse pdflatex to create pdf file")
    if ppd.latex & ppd.latex_makepdf:
        try:
            os.system('pdflatex %s' % ppd.latex_fname)
        except:
            print('*** pdflatex command failed')
        print("\nSuccessfully created pdf file:  %s/%s.pdf" \
                % (plotdir, ppd.latex_fname))

    os.chdir(startdir)
    # end of timeframes2latex



#============================
def test(makeplots = True):
#============================
    try:
        from pylab import linspace,clf,plot,title,savefig,mod
    except:
        print('*** Error: could not import pylab')
        return

    ppd = PlotPagesData()

    ppd.plotdir = 'plots'

    ppd.html = True

    ppd.latex = True
    ppd.latex_itemsperline = 2
    ppd.latex_itemsperpage = 4
    ppd.latex_makepdf = False

    # create test figures:
    x = linspace(0,1,201)
    for n in range(6):
        fname = 'plot%s.png' % n
        fname_savefig = os.path.join(ppd.plotdir, fname)
        if makeplots:
            clf()
            y = x**n
            plot(x,y)
            title('$f(x) = x^%s$' % n)
            savefig(fname_savefig)
        pid = ppd.new_pageitem()
        pid.fname = fname
        pid.html_index_entry = "Plot of x^%s" % n
        if mod(n,2) == 0:
            pid.latex_preitem = r"""
              \vskip 5pt \noindent{\large\bf Plot of $x^%s$}\vskip 2pt""" % n

    ppd.make_pages()


#============================
def clawtest():
#============================
    html_index = HtmlIndex(fname='vary_mx_index.html', \
          title='Results from running vary_mx.py')
    html_index.add(text = 'Experiments varying mx')

    for mx in [50, 100]:
        ppd = PlotPagesData()

        outdir = 'output.mx%s' % mx
        ppd.plotdir = outdir
        ppd.overwrite = True

        ppd.html = True
        ppd.html_index_title = 'Clawpack Plots with mx = %s' % mx

        ppd.latex = True
        ppd.latex_makepdf = False

        ppd.timeframes_framenos = 'all'
        ppd.timeframes_frametimes = {}
        ppd.timeframes_fignos = 'all'
        ppd.timeframes_fignames = {}

        ppd.make_timeframes_html()
        ppd.make_timeframes_latex()

        # update global index:
        mx_text = 'mx = %s' % mx
        mx_index = os.path.join(outdir, ppd.html_index_fname)
        html_index.add(text = mx_text, link = mx_index)

    html_index.close()

#-----------------------------
def current_time(addtz=False):
#-----------------------------
    # determine current time and reformat:
    time1 = time.asctime()
    year = time1[-5:]
    day = time1[:-14]
    hour = time1[-13:-5]
    current_time = day + year + ' at ' + hour
    if addtz:
        current_time = current_time + ' ' + time.tzname[time.daylight]
    return current_time


#======================================================================
def plotclaw2html(plotdata):
#======================================================================

    """
    Create and html index and html pages for each figure created from the
    specified plotdata.

    Assumes the following types of figures may exist:
       time frame figures of the form frame000NfigJ.png
       gauge figures of the form gauge000NfigJ.png
       other each_run type figures of the form figJ.png
       other figures can be specified in a dictionary plotdata.otherfigs

      plotdata.timeframes_framenos  is list of frames to use,
      plotdata.timeframes_frametimes  is dictionary of time for each frame
      plotdata.timeframes_fignos  is list of figs to use,
      plotdata.timeframes_fignames  is dictionary of fig names for index.
      plotdata.gauges_gaugenos  is list of gauges to use,
      plotdata.gauges_fignos  is list of figs to use,
      plotdata.gauges_fignames  is dictionary of fig names for index.
      plotdata.eachrun_fignos  is list of figs to use,
      plotdata.eachrun_fignames  is dictionary of fig names for index.

    """


    print('\n-----------------------------------\n')
    print('\nCreating html pages for figures...\n')

    startdir = os.getcwd()

    try:
        cd_with_mkdir(plotdata.plotdir, plotdata.overwrite, plotdata.verbose)
    except:
        print("*** Error, aborting plotclaw2html")
        raise

    creationtime = current_time()
    plotdata = massage_frames_data(plotdata)
    if plotdata.gauges_fignos is not None:
        plotdata = massage_gauges_data(plotdata)
        gauge_pngfile = plotdata._gauge_pngfile
        gauge_htmlfile = plotdata._gauge_htmlfile
        gauge_allfigsfile = plotdata._gauge_allfigsfile

    framenos = plotdata.timeframes_framenos
    frametimes = plotdata.timeframes_frametimes
    fignos = plotdata.timeframes_fignos
    fignames = plotdata.timeframes_fignames
    pngfile = plotdata._pngfile
    htmlfile = plotdata._htmlfile
    frametimef = plotdata._frametimef
    allfigsfile = plotdata._allfigsfile
    allframesfile = plotdata._allframesfile

    numframes = len(framenos)
    numfigs = len(fignos)


    eagle = getattr(plotdata,'html_eagle',False)


    # Create the index page:
    #-----------------------

    html = open(plotdata.html_index_fname,'w')

    if eagle:
        html.write("""
          <html><meta http-equiv="expires" content="0">
          <title>EagleClaw Plot Index</title>
          <head>
          <link type="text/css" rel="stylesheet"
                href="http://localhost:50005/eagleclaw/eagleclaw.css">
          </head>
          <eagle1>EagleClaw -- Plot Index</eagle1>
          <eagle2>Easy Access Graphical Laboratory for Exploring Conservation
          Laws</eagle2>
          <p>
          <center><eagle3>
          <a href="../eaglemenu.html">Main Menu for this run-directory
          </a></eagle3> </center><p>
        """)


    else:
        html.write('<html><meta http-equiv="expires" content="0">')
        html.write('\n<title>%s</title>' % plotdata.html_index_title)
        html.write('\n<body><center><h1>%s</h1></center>\n' \
                   % plotdata.html_index_title)
        homelink = getattr(plotdata,'html_homelink',None)
        if homelink:
            html.write('<center><a href="%s">Back to %s</a></center>\n' \
                       % (homelink, homelink))

    html.write('<p>\n')
    html.write('<center>Plots created: %s &nbsp;&nbsp; ' % creationtime )
    html.write('</center><p>\n')

    html.write('<p>\n<b>Go to:</b>\n')

    gaugenos = plotdata.gauges_gaugenos
    if gaugenos is not None:
        numgauges = len(gaugenos)
        if (len(plotdata.gauges_fignos)>0):
            html.write('&nbsp;&nbsp; <a href="#gauges">Gauges</a>\n')

    html.write('&nbsp;&nbsp; <a href="#eachrun">Other plots</a>\n')

    html.write('<p>\n<a name="timeframes"><h3>Time frames:</h3></a>\n')
    html.write('<p>\n<table border=0 cellpadding=5 cellspacing=5>\n')


    if plotdata.latex_makepdf:
        html.write('<p><tr><td><b>pdf file:</b></td>')
        html.write('\n   <td><a href="%s.pdf">%s.pdf</a></td>' \
               % (plotdata.latex_fname,plotdata.latex_fname))
        html.write('</tr>\n')

    if plotdata.html_movie:
        html.write('<p><tr><td><b>js Movies:</b></td>')
        for figno in fignos:
            html.write('\n   <td><a href="%sfig%s.html">%s</a></td>' \
                         % (plotdata.movie_name_prefix,figno,fignames[figno]))
        html.write('</tr>\n')
    if plotdata.gif_movie:
        html.write('<p><tr><td><b>gif Movies:</b></td>')
        for figno in fignos:
            html.write('\n   <td><a href="%sfig%s.gif">%s</a></td>' \
                         % (plotdata.movie_name_prefix,figno,fignames[figno]))
        html.write('</tr>\n')
    if plotdata.mp4_movie:
        html.write('<p><tr><td><b>mp4 Movies:</b></td>')
        for figno in fignos:
            html.write('\n   <td><a href="%sfig%s.mp4">%s</a></td>' \
                         % (plotdata.movie_name_prefix,figno,fignames[figno]))
        html.write('</tr>\n')
    html.write('<p>\n<tr><td><b>All Frames:</b></td> ')
    for ifig in range(len(fignos)):
        html.write('\n   <td><a href="%s">%s</a></td>' \
                       % (allframesfile[fignos[ifig]],fignames[fignos[ifig]]))
    html.write('</tr>\n')
    html.write('<p>\n<tr><td><b>Individual Frames:</b></td> </tr>\n')

    for frameno in framenos:

        html.write('\n <tr><td>Frame %s, t = %s:</td>' \
                    % (frameno,frametimef[frameno]))
        for figno in fignos:
            figname = fignames[figno]
            html.write('\n   <td><a href="%s">%s</a></td>' \
                       % (htmlfile[frameno,figno],figname))
        if numfigs > 1:
            html.write('\n<td><a href="%s">All figures</a></td>' \
                       % allfigsfile[frameno])
        html.write('</tr>\n')
    html.write('</table>\n')

    # Gauges:
    #----------------
    if gaugenos is not None:
        fignos = plotdata.gauges_fignos
        fignames = plotdata.gauges_fignames
        if (len(fignos)>0):
            html.write('<p>\n<a name="gauges"><h3>Gauges:</h3></a>\n')
            html.write('<p>\n<table border=0 cellpadding=5 cellspacing=5>\n')
            html.write('<p>\n<tr><td><b>All Gauges:</b></td> ')
            for ifig in range(len(fignos)):
                html.write('\n   <td><a href="allgaugesfig%s.html">%s</a></td>' \
                               % (fignos[ifig],fignames[fignos[ifig]]))
            html.write('</tr>\n')
            html.write('<p>\n<tr><td><b>Individual Gauges:</b></td> </tr>\n')

            for gaugeno in gaugenos:

                html.write('\n <tr><td>Gauge %s:</td>' % (gaugeno))
                for figno in fignos:
                    figname = fignames[figno]
                    html.write('\n   <td><a href="%s">%s</a></td>' \
                               % (gauge_htmlfile[gaugeno,figno],figname))
                if numfigs > 1:
                    html.write('\n<td><a href="%s">All figures</a></td>' \
                               % gauge_allfigsfile[gaugeno])
                html.write('</tr>\n')
            html.write('</table>\n')

    # Other plots:
    #----------------
    if len(plotdata.otherfigure_dict)>0:
        html.write('<p>\n<a name="eachrun"><h3>Other plots:</h3></a>\n')
        html.write('<p><ul>\n')
        for name in plotdata.otherfigure_dict.keys():
            otherfigure = plotdata.otherfigure_dict[name]
            fname = otherfigure.fname
            makefig = otherfigure.makefig
            if makefig:
                if type(makefig)==str:
                    try:
                        exec((makefig), globals(), locals())
                    except:
                        print("*** Problem executing makefig ")
                        print("    for otherfigure ",name)
                else:
                    try:
                        makefig(plotdata)
                    except:
                        print("*** Problem executing makefig function")
                        print("    for otherfigure ",name)
                        raise

            html.write('<p><li><a href="%s">%s</a>\n' %(fname,name))
        html.write('<p></ul>\n')

    html.write('</body></html>')

    # end of index
    #----------------------------------------------------------------------

    fignos = plotdata.timeframes_fignos
    fignames = plotdata.timeframes_fignames

    # allframesfigJ.html
    #-------------------
    for figno in fignos:
        html = open(allframesfile[figno], 'w')
        html.write('<html><meta http-equiv="expires" content="0">')
        html.write('<title>Plots</title>')
        html.write('<body>\n<center><h1>All Frames -- %s</h1>\n' \
                   % fignames[figno])
        html.write('<p>\n')
        html.write('\n<p><h3><a href=%s>Plot Index</a></h3>\n' \
                   % (plotdata.html_index_fname))
        html.write('<p>\n')
        html.write('<h3>Click on a figure to enlarge</h3>\n')
        html.write('<p>\n')

        for frameno in framenos:
            html.write('  <a href="%s"><img src="%s" width=400></a>\n' \
                % (htmlfile[frameno,figno], pngfile[frameno,figno]))

        html.write('\n</center></body></html>\n')
        html.close()


    # allfigsframeN.html
    #-------------------
    if numfigs > 1:
        for iframe in range(numframes):
            frameno = framenos[iframe]
            html = open(allfigsfile[frameno], 'w')
            html.write('<html><meta http-equiv="expires" content="0">')
            html.write('<title>Plots</title>')
            html.write('<body>\n<center><h3>All Figures -- Frame %s' \
                 % framenos[iframe])
            html.write('&nbsp; at time t = %s' % frametimef[frameno])
            html.write('<p>\n')

            # Write link commands to previous and next frame:

            html.write('<p> <a href="%s">' % allfigsfile[framenos[0]])
            html.write('&#060; &#060;</a> &nbsp; &nbsp;\n')
            if iframe==0:
                html.write('&#060; &nbsp; &nbsp; ')
                html.write('\n<a href="%s">Index</a> ' \
                     % plotdata.html_index_fname)
                if numframes > 1:
                    html.write('&nbsp; &nbsp; <a href="%s"> &#062; </a> ' \
                        % allfigsfile[framenos[1]])

            elif iframe==numframes-1:
                if numframes > 1:
                    html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                        % allfigsfile[framenos[iframe-1]])
                html.write('\n<a href="%s">Index</a> ' \
                     % plotdata.html_index_fname)
                html.write(' &nbsp; &nbsp; &#062; ')

            else:
                html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                        % allfigsfile[framenos[iframe-1]])
                html.write('\n<a href="%s">Index</a> ' \
                     % plotdata.html_index_fname)
                html.write('\n&nbsp; &nbsp; <a href="%s"> &#062; </a>  &nbsp; &nbsp; ' \
                        % allfigsfile[framenos[iframe+1]])

            html.write('&nbsp; &nbsp; \n<a href="%s"> ' \
                      % allfigsfile[framenos[numframes-1]])
            html.write('&#062; &#062;</a>  \n')

            html.write('</h3><p>\n')
            html.write('<h3>Click on a figure to enlarge</h3>\n')
            html.write('<p>\n')

            for figno in fignos:
                html.write('  <a href="%s"><img src="%s" width=400></a>\n' \
                        % (htmlfile[frameno,figno], pngfile[frameno,figno]))

            # list of all frames at bottom:

            html.write('\n<p><b>Other frames:</b></a> &nbsp;&nbsp;')
            for frameno2 in framenos:
                if frameno2 == frameno:
                    html.write('\n<font color=red>%i</font>&nbsp;&nbsp;' \
                               % frameno)
                else:
                    html.write('\n<a href="%s">%i</a>  &nbsp; &nbsp; ' \
                           % (allfigsfile[frameno2],frameno2))

            html.write('\n</center></body></html>\n')
            html.close()


    # frameNfigJ.html  -- individual files for each frame/fig combo
    #----------------

    for iframe in range(numframes):
        frameno = framenos[iframe]
        for figno in fignos:
            html = open(htmlfile[frameno,figno],'w')
            html.write('<html><meta http-equiv="expires" content="0">\n')
            html.write('<title>Plots</title>')
            html.write('<body><center>\n')
            html.write('\n<h3>Frame %i ' % frameno)
            if numfigs > 1:
                html.write(' &nbsp;---&nbsp; %s' % fignames[figno] )
            html.write('&nbsp;&nbsp; at time t = %s</h3>' % frametimef[frameno])

            # Write link commands to previous and next frame:

            html.write('<p> <a href="%s">' % htmlfile[framenos[0],figno])
            html.write('&#060; &#060;</a> &nbsp; &nbsp;\n')
            if iframe==0:
                html.write('&#060; &nbsp; &nbsp; ')
                html.write('\n<a href="%s">Index</a> ' \
                     % plotdata.html_index_fname)
                if numframes > 1:
                    html.write('&nbsp; &nbsp; <a href="%s"> &#062; </a> ' \
                        % htmlfile[framenos[1],figno])

            elif iframe==numframes-1:
                if numframes > 1:
                    html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                        % htmlfile[framenos[iframe-1],figno])
                html.write('\n<a href="%s">Index</a> ' \
                     % plotdata.html_index_fname)
                html.write(' &nbsp; &nbsp; &#062; ')

            else:
                html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                        % htmlfile[framenos[iframe-1],figno])
                html.write('\n<a href="%s">Index</a> ' \
                     % plotdata.html_index_fname)
                html.write('\n &nbsp; &nbsp;<a href="%s"> &#062; </a>  &nbsp; &nbsp; ' \
                        % htmlfile[framenos[iframe+1],figno])

            html.write('&nbsp; &nbsp; \n<a href="%s"> ' \
                      % htmlfile[framenos[numframes-1],figno])
            html.write('&#062; &#062;</a>  \n')

            # image:
            html.write('\n\n <p><img src="%s"><p>  \n ' \
                        % pngfile[frameno,figno])

            html.write('\n\nImage source: &nbsp; %s'  \
                   % os.path.join(os.getcwd(),pngfile[frameno,figno]))

            # list of all figures at bottom of page:

            if numfigs > 1:
                html.write('\n<p><b>Other figures at this time:</b> &nbsp;&nbsp;')
                for figno2 in fignos:
                    if figno2 == figno:
                        html.write('\n<font color=red>%s</font>&nbsp;&nbsp;' \
                               % fignames[figno])
                    else:
                        html.write('\n<a href="%s">%s</a>  &nbsp; &nbsp; ' \
                           % (htmlfile[frameno,figno2],fignames[figno2]))
                html.write('\n<a href="%s"> All Figures </a>' \
                     % allfigsfile[frameno])

            # list of all frames at bottom of page:

            html.write('\n<p><b>Other frames:</b></a> &nbsp;&nbsp;')
            for frameno2 in framenos:
                if frameno2 == frameno:
                    html.write('\n<font color=red>%i</font>&nbsp;&nbsp;' \
                               % frameno)
                else:
                    html.write('\n<a href="%s">%i</a>  &nbsp; &nbsp; ' \
                           % (htmlfile[frameno2,figno],frameno2))
            html.write('\n<a href="%s">  All Frames </a>' \
                     % allframesfile[figno])

            html.write('\n<p><h3><a href=%s>Plot Index</a></h3>' \
                      % (plotdata.html_index_fname))
            if eagle:
                html.write("""<p><h3><a href="../eaglemenu.html">Main Menu for
                this run-directory</a></h3>  """)
            html.write('</center></body></html>')
            html.close()


    # moviefigJ.html
    #-------------------

    if (plotdata.html_movie in [True, "4.x"]) and (len(framenos) > 0):

        # original style still used if plotdata.html_movie == "4.x":
        for figno in fignos:
            html = open('movie%s' % allframesfile[figno], 'w')
            text = htmlmovie(plotdata.html_index_fname,pngfile,framenos,figno)
            html.write(text)
            html.close()



    #----------------------------------------------------------------------
    fignos = plotdata.gauges_fignos
    fignames = plotdata.gauges_fignames

    # allgaugesfigJ.html
    #-------------------
    if fignos is None:
        fignos = []
    for figno in fignos:
        html = open('allgaugesfig%s.html' % figno, 'w')
        html.write('<html><meta http-equiv="expires" content="0">')
        html.write('<title>Plots</title>')
        html.write('<body>\n<center><h1>All Gauges -- %s</h1>\n' \
                   % fignames[figno])
        html.write('<p>\n')
        html.write('\n<p><h3><a href=%s>Plot Index</a></h3>\n' \
                   % (plotdata.html_index_fname))
        html.write('<p>\n')
        html.write('<h3>Click on a figure to enlarge</h3>\n')
        html.write('<p>\n')

        for gaugeno in gaugenos:
            html.write('  <a href="%s"><img src="%s" width=400></a>\n' \
                % (gauge_htmlfile[gaugeno,figno], gauge_pngfile[gaugeno,figno]))

        html.write('\n</center></body></html>\n')
        html.close()


    # allfigsgaugeN.html
    #-------------------
    if gaugenos is not None:
        if numfigs > 1:
            for igauge in range(numgauges):
                gaugeno = gaugenos[igauge]
                html = open(gauge_allfigsfile[gaugeno], 'w')
                html.write('<html><meta http-equiv="expires" content="0">')
                html.write('<title>Plots</title>')
                html.write('<body>\n<center><h3>All Figures -- Gauge %s' \
                     % gaugenos[igauge])
                html.write('<p>\n')

                # Write link commands to previous and next gauge:

                html.write('<p> <a href="%s">' % gauge_allfigsfile[gaugenos[0]])
                html.write('&#060; &#060;</a> &nbsp; &nbsp;\n')
                if igauge==0:
                    html.write('&#060; &nbsp; &nbsp; ')
                    html.write('\n<a href="%s">Index</a> ' \
                         % plotdata.html_index_fname)
                    if numgauges > 1:
                        html.write('&nbsp; &nbsp; <a href="%s"> &#062; </a> ' \
                            % gauge_allfigsfile[gaugenos[1]])

                elif igauge==numgauges-1:
                    if numgauges > 1:
                        html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                            % gauge_allfigsfile[gaugenos[igauge-1]])
                    html.write('\n<a href="%s">Index</a> ' \
                         % plotdata.html_index_fname)
                    html.write(' &nbsp; &nbsp; &#062; ')

                else:
                    html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                            % gauge_allfigsfile[gaugenos[igauge-1]])
                    html.write('\n<a href="%s">Index</a> ' \
                         % plotdata.html_index_fname)
                    html.write('\n&nbsp; &nbsp; <a href="%s"> &#062; </a>  &nbsp; &nbsp; ' \
                            % gauge_allfigsfile[gaugenos[igauge+1]])

                html.write('&nbsp; &nbsp; \n<a href="%s"> ' \
                          % gauge_allfigsfile[gaugenos[numgauges-1]])
                html.write('&#062; &#062;</a>  \n')

                html.write('</h3><p>\n')
                html.write('<h3>Click on a figure to enlarge</h3>\n')
                html.write('<p>\n')

                for figno in fignos:
                    html.write('  <a href="%s"><img src="%s" width=400></a>\n' \
                            % (gauge_htmlfile[gaugeno,figno], gauge_pngfile[gaugeno,figno]))

                # list of all gauges at bottom:

                html.write('\n<p><b>Other gauges:</b></a> &nbsp;&nbsp;')
                for gaugeno2 in gaugenos:
                    if gaugeno2 == gaugeno:
                        html.write('\n<font color=red>%i</font>&nbsp;&nbsp;' \
                                   % gaugeno)
                    else:
                        html.write('\n<a href="%s">%i</a>  &nbsp; &nbsp; ' \
                               % (gauge_allfigsfile[gaugeno2],gaugeno2))

                html.write('\n</center></body></html>\n')
                html.close()


        # gaugeNfigJ.html  -- individual files for each gauge/fig combo
        #----------------

        for igauge in range(numgauges):
            gaugeno = gaugenos[igauge]
            for figno in fignos:
                html = open(gauge_htmlfile[gaugeno,figno],'w')
                html.write('<html><meta http-equiv="expires" content="0">\n')
                html.write('<title>Plots</title>')
                html.write('<body><center>\n')
                html.write('\n<h3>Gauge %i ' % gaugeno)
                if numfigs > 1:
                    html.write(' &nbsp;---&nbsp; %s' % fignames[figno] )

                # Write link commands to previous and next gauge:

                html.write('<p> <a href="%s">' % gauge_htmlfile[gaugenos[0],figno])
                html.write('&#060; &#060;</a> &nbsp; &nbsp;\n')
                if igauge==0:
                    html.write('&#060; &nbsp; &nbsp; ')
                    html.write('\n<a href="%s">Index</a> ' \
                         % plotdata.html_index_fname)
                    if numgauges > 1:
                        html.write('&nbsp; &nbsp; <a href="%s"> &#062; </a> ' \
                            % gauge_htmlfile[gaugenos[1],figno])

                elif igauge==numgauges-1:
                    if numgauges > 1:
                        html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                            % gauge_htmlfile[gaugenos[igauge-1],figno])
                    html.write('\n<a href="%s">Index</a> ' \
                         % plotdata.html_index_fname)
                    html.write(' &nbsp; &nbsp; &#062; ')

                else:
                    html.write('\n<a href="%s"> &#060; </a>  &nbsp; &nbsp; ' \
                            % gauge_htmlfile[gaugenos[igauge-1],figno])
                    html.write('\n<a href="%s">Index</a> ' \
                         % plotdata.html_index_fname)
                    html.write('\n &nbsp; &nbsp;<a href="%s"> &#062; </a>  &nbsp; &nbsp; ' \
                            % gauge_htmlfile[gaugenos[igauge+1],figno])

                html.write('&nbsp; &nbsp; \n<a href="%s"> ' \
                          % gauge_htmlfile[gaugenos[numgauges-1],figno])
                html.write('&#062; &#062;</a>  \n')

                # image:
                html.write('\n\n <p><img src="%s"><p>  \n ' \
                            % gauge_pngfile[gaugeno,figno])

                html.write('\n\nImage source: &nbsp; %s'  \
                       % os.path.join(os.getcwd(),gauge_pngfile[gaugeno,figno]))

                # list of all figures at bottom of page:

                if numfigs > 1:
                    html.write('\n<p><b>Other figures at this time:</b> &nbsp;&nbsp;')
                    for figno2 in fignos:
                        if figno2 == figno:
                            html.write('\n<font color=red>%s</font>&nbsp;&nbsp;' \
                                   % fignames[figno])
                        else:
                            html.write('\n<a href="%s">%s</a>  &nbsp; &nbsp; ' \
                               % (gauge_htmlfile[gaugeno,figno2],fignames[figno2]))
                    html.write('\n<a href="%s"> All Figures </a>' \
                         % gauge_allfigsfile[gaugeno])

                # list of all gauges at bottom of page:

                html.write('\n<p><b>Other gauges:</b></a> &nbsp;&nbsp;')
                for gaugeno2 in gaugenos:
                    if gaugeno2 == gaugeno:
                        html.write('\n<font color=red>%i</font>&nbsp;&nbsp;' \
                                   % gaugeno)
                    else:
                        html.write('\n<a href="%s">%i</a>  &nbsp; &nbsp; ' \
                               % (gauge_htmlfile[gaugeno2,figno],gaugeno2))
                html.write('\n<a href="allgaugesfig%s.html">  All Gauges </a>' \
                         % figno)

                html.write('\n<p><h3><a href=%s>Plot Index</a></h3>' \
                          % (plotdata.html_index_fname))
                if eagle:
                    html.write("""<p><h3><a href="../eaglemenu.html">Main Menu for
                    this run-directory</a></h3>  """)
                html.write('</center></body></html>')
                html.close()

    os.chdir(startdir)
    # end of plotclaw2html


#=====================================
def massage_gauges_data(plot_pages_data):
#=====================================
    ppd = plot_pages_data

    try:
        gaugenos = ppd.gauges_gaugenos
        fignos = ppd.gauges_fignos
        fignames = ppd.gauges_fignames
        prefix = getattr(ppd, 'gauges_prefix', 'gauge')
    except:
        print('*** Error: gauges not set properly')
        return

    startdir = os.getcwd()

    for figno in fignos:
        if figno not in fignames:
            fignames[figno] = 'Solution'

    numgauges = len(gaugenos)
    numfigs = len(fignos)

    #if len(gaugenos) == 0:
    #    print '*** Warning: 0 gauges to print'
    #if len(fignos) == 0:
    #    print '*** Warning: 0 figures to print each gauge'

    pngfile = {}
    htmlfile = {}
    allfigsfile = {}
    for gaugeno in gaugenos:
        gaugef = str(gaugeno).zfill(4)
        for figno in fignos:
            pngfile[gaugeno,figno] = '%s%sfig%s.png'  % (prefix,gaugef,figno)
            htmlfile[gaugeno,figno] = '%s%sfig%s.html' % (prefix,gaugef,figno)
        allfigsfile[gaugeno] = 'allfigs%s%s.html' % (prefix,gaugef)

    ppd.gauges_gaugenos = gaugenos
    ppd.gauges_fignos = fignos
    ppd.gauges_fignames = fignames
    ppd._gauge_pngfile = pngfile
    ppd._gauge_htmlfile = htmlfile
    ppd._gauge_allfigsfile = allfigsfile
    return ppd

def redirect_stdouts(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        stdout_save = sys.stdout
        stderr_save = sys.stderr
        try:
            return f(*args, **kwds)
        finally:
            # reset stdout for future print statements
            sys.stdout = stdout_save
            sys.stderr = stderr_save
    return wrapper

#============================================
@redirect_stdouts
def plotclaw_driver(plotdata, verbose=False, format='ascii'):
#============================================
    """
    The ClawPlotData object plotdata will be initialized by a call to
    function setplot unless plotdata.setplot=False.

    If plotdata.setplot=True then it is assumed that the current directory
    contains a module setplot.py that defines this function.

    If plotdata.setplot is a string then it is assumed this is the name of
    a module to import that contains the function setplot.

    If plotdata.setplot is a function then this function will be used.
    """

    import glob, sys, os
    from clawpack.visclaw.data import ClawPlotData
    from clawpack.visclaw import frametools, gaugetools

    # doing plots in parallel?
    _parallel = plotdata.parallel and (plotdata.num_procs > 1)

    if plotdata._parallel_todo == 'frames':
        # all we need to do is make png's for some frames in this case:
        for frameno in plotdata.print_framenos:
            frametools.plotframe(frameno, plotdata, verbose)
            print('Creating png for Frame %i' % frameno)
        return

    plotdata.save_frames = False

    if format == "petsc":
        plotdata.file_prefix = "claw"
        file_extension = "ptc"
    else:
        file_extension = "q"
    if plotdata.file_prefix is None:
        plotdata.file_prefix = 'fort'

    datadir = os.getcwd()  # assume data files in this directory

    if 'matplotlib' not in sys.modules:
        print('*** Error: matplotlib not found, no plots will be done')
        return plotdata

    if not isinstance(plotdata,ClawPlotData):
        print('*** Error, plotdata must be an object of type ClawPlotData')
        return plotdata

    plotdata._mode = 'printframes'

    # plotdata = frametools.call_setplot(plotdata.setplot, plotdata)

    try:
        plotdata.rundir = os.path.abspath(plotdata.rundir)
        plotdata.outdir = os.path.abspath(plotdata.outdir)
        plotdata.plotdir = os.path.abspath(plotdata.plotdir)

        framenos = plotdata.print_framenos # frames to plot
        gaugenos = plotdata.print_gaugenos # gauges to plot
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
    plotdata = frametools.set_show(plotdata)
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
        cd_plotdir(plotdata.plotdir, plotdata.overwrite)
    except:
        print("*** Error, aborting plotframes")
        return plotdata


    framefiles = glob.glob(os.path.join(plotdir,'frame*.png')) + \
                    glob.glob(os.path.join(plotdir,'frame*.html'))

    if (not _parallel) or (plotdata._parallel_todo=='initialize'):
        if overwrite:
            # remove any old versions:
            for file in framefiles:
                os.remove(file)
        else:
            if len(framefiles) > 1:
                print("*** Remove frame*.png and frame*.html and try again,")
                print("  or use overwrite=True in call to printframes")
                return plotdata

    if plotdata._parallel_todo=='initialize':
        os.chdir(rundir)
        return plotdata

    try:
        os.chdir(outdir)
    except:
        print('*** Error plotclaw_driver: cannot move to outdir = ',outdir)
        return plotdata


    fortfile = {}
    pngfile = {}
    frametimes = {}

    for file in glob.glob(plotdata.file_prefix + '.'+file_extension+r'\d{4}'):
        frameno = int(file[-4:])
        fortfile[frameno] = file
        for figno in fignos_each_frame:
            pngfile[frameno,figno] = 'frame' + file[-4:] + 'fig%s.png' % figno

    if len(fortfile) == 0:
        print('*** Warning: No fort.q or claw.pkl files found in directory ', os.getcwd())
        #return plotdata

    # Discard frames that are not from latest run, based on
    # file modification time:
    framenos = frametools.only_most_recent(framenos, plotdata.outdir,
                                           plotdata.file_prefix)

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

    # Only grab times by loading in time
    for frameno in framenos:
        plotdata.output_controller.output_path = plotdata.outdir
        plotdata.output_controller.file_prefix = plotdata.file_prefix
        frametimes[frameno] = plotdata.output_controller.get_time(frameno)

    # for frameno in framenos:
    #     frametimes[frameno] = plotdata.getframe(frameno, plotdata.outdir).t

    plotdata.timeframes_framenos = framenos
    plotdata.timeframes_frametimes = frametimes
    plotdata.timeframes_fignos = fignos_each_frame
    plotdata.timeframes_fignames = fignames

    # Gauges:
    # -------
    if os.path.exists(os.path.join(plotdata.outdir,"gauges.data")):
        gaugenos = plotdata.print_gaugenos
        if gaugenos == 'all':
            # Read gauge numbers from setgauges.data if it exists:
            setgauges = gaugetools.read_setgauges(plotdata.outdir)
            gaugenos = setgauges.gauge_numbers

        plotdata.gauges_gaugenos = gaugenos
        plotdata.gauges_fignos = fignos_each_gauge
        plotdata.gauges_fignames = fignames
    else:
        gaugenos = []

    # Make html files for time frame figures:
    # ---------------------------------------

    if plotdata.html_movie == "JSAnimation":
        # Only import if we need it:
        try:
            from matplotlib import animation
        except:
            print("*** Warning: Your version of matplotlib may not support JSAnimation")
            print("    Switching to 4.x style animation")
            plotdata.html_movie = "4.x"

    os.chdir(plotdir)

    if plotdata.html:
        plotclaw2html(plotdata)
        pass

    # Make png files for all frames and gauges:
    # -----------------------------------------

    if not plotdata.printfigs:
        print("Using previously printed figure files")
    else:
        print("Now making png files for all figures...")

        if not _parallel:
            # don't create the png for frames when run in parallel
            # (unless plotdata._parallell_todo=='frames', handled earlier)
            for frameno in framenos:
                frametools.plotframe(frameno, plotdata, verbose)
                print('Frame %i at time t = %s' % (frameno, frametimes[frameno]))

        gaugenos_input = tuple(gaugenos)
        gaugenos = []
        for gaugeno in gaugenos_input:
            try:
                gaugetools.plotgauge(gaugeno, plotdata, verbose)
                print('Found data for Gauge %i ' % gaugeno)
                gaugenos.append(gaugeno)
            except:
                print('*** Warning: Unable to plot Gauge %i' \
                        % gaugeno)


    if plotdata.latex:
        timeframes2latex(plotdata)

    if plotdata.kml:
        plotclaw2kml(plotdata)

    if ((plotdata.html_movie == "JSAnimation") or plotdata.mp4_movie) and (len(framenos) > 0):

        # Create Animations
    
        for figno in fignos_each_frame:
            fname = '*fig' + str(figno) + '.png'
            filenames=sorted(glob.glob(fname))

            # RJL: This way gives better resolution although it basically does
            # the same thing as the code I removed, so not sure why

            raw_html = '<html>\n<center><h3><a href=%s>Plot Index</a></h3>\n' \
                        % plotdata.html_index_fname
            
            if plotdata.file_prefix in ['fort',None]:
                png_prefix = ''
            else:
                png_prefix = plotdata.file_prefix

            # get original fig shape
            figname = plotdata._figname_from_num[figno]
            plotfigure = plotdata.plotfigure_dict[figname]
            figkwargs = getattr(plotfigure, 'kwargs', {})
            figsize = getattr(plotfigure, 'figsize', None)
            if figsize is None:
                figsize = figkwargs.get('figsize', None)
            if figsize is None:
                figsize = (8,6)  # reasonable for browser?

            # make animations
            if plotdata.mp4_movie:
                # use default dpi or get from plotdata
                # this ensures that if it was set, dpi of mp4 is same as frames.
                dpi = figkwargs.get('dpi', html_movie_dpi)
                animation_tools.make_anim_outputs_from_plotdir(plotdir=plotdir,
                                #file_name_prefix='movieframe_allframes',
                                file_name_prefix=plotdata.movie_name_prefix,
                                png_prefix=png_prefix,
                                figsize=figsize,
                                dpi=dpi,
                                fignos=[figno], outputs=['mp4'],
                                raw_html=raw_html)

            if plotdata.html_movie == "JSAnimation":
                # use different dpi so that plots do not take over browser width.
                animation_tools.make_anim_outputs_from_plotdir(plotdir=plotdir,
                                #file_name_prefix='movieframe_allframes',
                                file_name_prefix=plotdata.movie_name_prefix,
                                png_prefix=png_prefix,
                                figsize=figsize,
                                dpi=plotdata.html_movie_dpi,
                                fignos=[figno], outputs=['html'],
                                raw_html=raw_html)

            # Note: setting figsize=None above chooses figsize with aspect
            # ratio based on .png files read in, may fit better on page
            # 3/21/24 - For MP4 size and dpi are taken from plotdata for
            # each figure.


    #-----------
    # gif movie:
    #-----------

    if plotdata.gif_movie and (len(framenos) > 0):
        print('Making gif movies.  This may take some time....')
        for figno in fignos_each_frame:
            fname_gif = '%sfig%s.gif' \
                        % (plotdata.movie_name_prefix, figno)
            try:
                os.system('convert -delay 20 frame*fig%s.png %s' \
                   % (figno,fname_gif))
                print('    Created %s' % fname_gif)
            except:
                print('*** Error creating %s' % fname_gif)

    os.chdir(rootdir)

    # print out pointers to html index page:
    path_to_html_index = os.path.join(os.path.abspath(plotdata.plotdir), \
                               plotdata.html_index_fname)
    if plotdata.html:
        print_html_pointers(path_to_html_index)



    return plotdata
    # end of printframes
