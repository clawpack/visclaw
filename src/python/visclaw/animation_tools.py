"""
This animation_tools module contains tools to create animations in Python and
Jupyter notebooks.

Three types of animations are supported: 
 - using the ipywidget interact to create a figure with a slider bar, 
 - an `animation.FuncAnimation` object, which can be displayed using the
   `to_jshtml` method in a notebook, or written to an html file.
   NOTE: this replaces the old JSAnimation tools, now incorporated into
   matplotlib's `animation.FuncAnimation`.
 - creation of mp4 files using ffmpeg (provided this package is installed).

The set of images to combine in an animation can be specified as a
list of images, a list of `matplotlib` figures, or a directory of
`png` or other image files.

Utilities are provided to convert between these.

Functions are provided to create inline animations in Jupyter notebooks or 
stand-alone files that can be viewed in other ways, including 
 - An html file with the JSAnimation version,
 - A mp4 file,
 - A reStructured text file with the JSAnimation for inclusion in Sphinx docs.

The utility function make_anim_outputs_from_plotdir can be used to convert the 
png files in a Clawpack _plots directory into standalone animations of the types
listed above.  See the file 
    $CLAW/visclaw/src/python/visclaw/make_anim.py 
for an example of how this can be invoked from an applications directory.

For illustration of many of the tools defined in this module, see the notebook
  $CLAW/apps/notebooks/visclaw/animation_tools_demo.html
also visible in rendered form in the Clawpack gallery:
  http://www.clawpack.org/gallery/_static/apps/notebooks/visclaw/animation_tools_demo.html
  
See also:
 https://ipywidgets.readthedocs.io/en/latest/#ipywidgets
 https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.animation.Animation.html

More documentation of these functions is needed and they can probably be
improved.

Version: Updated for Clawpack v5.7.1.

"""

# use Python 3 style print function rather than Python 2 print statements:
from __future__ import print_function 

from matplotlib import image, animation
from matplotlib import pyplot as plt
import warnings


def make_plotdir(plotdir='_plots', clobber=True):
    """
    Utility function to create a directory for storing a sequence of plot
    files, or if the directory already exists, clear out any old plots.  
    If clobber==False then it will abort instead of deleting existing files.
    """

    import os
    if os.path.isdir(plotdir):
        if clobber:
            os.system("rm %s/*" % plotdir)
        else:
            raise IOError('*** Cannot clobber existing directory %s' % plotdir)
    else:
        os.system("mkdir %s" % plotdir)
    print("Figure files for each frame will be stored in ", plotdir)


def save_frame(frameno, plotdir='_plots', fname_base='frame', format='png',
               verbose=False, **kwargs):
    """
    After giving matplotlib commands to create the plot for a single frame 
    of the desired animation, this can be called to save the figure with
    the appropriate file name such as _plots/frame00001.png.
    """

    plt.draw()
    filename = '%s/%s%s.%s' % (plotdir, fname_base, str(frameno).zfill(5), format)
    plt.savefig(filename, **kwargs)
    if verbose:
        print("Saved ",filename)


def make_anim(plotdir, fname_pattern='frame*.png', figsize=None, dpi=None):
    """
    Assumes that a set of frames are available as png files in directory _plots,
    numbered consecutively, e.g. frame0000.png, frame0001.png, etc.

    Creates an animation based display each frame in turn, and returns anim.

    You can then display anim in an IPython notebook, or
    call make_html(anim) to create a stand-alone webpage.
    
    Note also the convenience functions that call this function:
        animate_from_plotdir: assumes plotdir has standard from from Clawpack
        make_anim_outputs_from_plotdir: creates .html, .mp4, and/or .rst files
    """

    import matplotlib

    import glob   # for finding all files matching a pattern

    # Find all frame files:
    filenames = glob.glob('%s/%s' % (plotdir, fname_pattern))
    
    if len(filenames)==0:
        msg = '\n*** No files found matching %s/%s' % (plotdir, fname_pattern)
        warnings.warn(msg)
        return None

    # sort them into increasing order:
    filenames=sorted(filenames)

    im0 = image.imread(filenames[0])
    
    if figsize is None:
        # choose figsize based on aspect ratio of image
        xin = 6.  # width in inches
        yin = xin * im0.shape[0]/im0.shape[1]
        figsize = (xin,yin)
        #print('+++ im0.shape, xin, yin: ',im0.shape, xin, yin)
        
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')  # so there's not a second set of axes
    im = plt.imshow(im0)
    
    def init():
        im.set_data(im0)
        return im,

    def animate(i):
        image_i=image.imread(filenames[i])
        im.set_data(image_i)
        return im,

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                          frames=len(filenames), interval=200, blit=True)

    plt.close(fig)

    return anim


def animate_images(images, figsize=(10,6), dpi=None):

    """
    Convert a list of images to anim using animation.FuncAnimation.
    """
    
    import matplotlib

    # display each image in a new fig:
    fig = plt.figure(figsize=figsize, dpi=None)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')  # so there's not a second set of axes

    im = plt.imshow(images[0])

    def init():
        im.set_data(images[0])
        return im,

    def animate(i):
        im.set_data(images[i])
        return im,

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                          frames=len(images), interval=200, blit=True)

    plt.close(fig)
    return anim


def animate_figs(figs, figsize=(10,6), dpi=300):

    """
    Convert a list of figs to anim using animation.FuncAnimation.
    """
    
    images = make_images(figs, dpi=dpi)
    anim = animate_images(images, figsize=figsize, dpi=dpi)
    return anim
    
    
def make_html(anim, file_name='anim.html', title=None, raw_html='', \
              fps=None, embed_frames=True, default_mode='once'):
    """
    Take an animation anim created by animation.FuncAnimation or by
    one of the other functions in this module, and convert it into a
    stand-alone html file with specified title.
    
    raw_html Will be put in the html file before the figure.
    """


    try:
        html_body = anim.to_jshtml(fps=fps, embed_frames=embed_frames, \
                                   default_mode=default_mode)
    except:
        msg = '\n*** anim.to_jshtml() failed, not making animation' \
              + '\n*** you may need to update your version of matplotlib'
        warnings.warn(msg)
        html_body = '<h2>Unable to make animation</h2>\n' + \
                    '<h3>Consider updating matplotlib</h3>\n'

    html_file = open(file_name,'w')
    if title is not None:
        html_file.write("<html>\n <h1>%s</h1>\n" % title)
    html_file.write(raw_html)
    html_file.write(html_body)
    html_file.close()
    print("Created %s" % file_name)


def make_rst(anim, file_name='anim.rst',
              fps=None, embed_frames=True, default_mode='once'):
    """
    Take an animation anim created by animation.FuncAnimation or by
    one of the other functions in this module, and convert it into rst.
    (reStructuredText, for inclusion in Sphinx documentation, for example).
    """


    rst_body = anim.to_jshtml(fps=fps, embed_frames=embed_frames, \
                               default_mode=default_mode)

    rst_body = rst_body.split('\n')

    rst_file = open(file_name,'w')
    rst_file.write(".. raw:: html\n")
    for line in rst_body:
        rst_file.write("   %s\n" % line)
    rst_file.close()
    print("Created %s" % file_name)
    print("Imbed this in another rst file using:")
    print(".. include:: %s" % file_name)


def make_mp4(anim, file_name='anim.mp4',
              fps=None, embed_frames=True, default_mode='once',
              dpi=None):
    """
    Take an animation and covert to mp4 file using ffmpeg, which must be
    installed.
    """
    import os

    if not animation.writers.is_available('ffmpeg'):
        print("** ffmpeg must be installed to create mp4 file")
        return

    if os.path.splitext(file_name)[1] != '.mp4':
        msg = "\n*** Might not work if file extension is not .mp4"
        warnings.warn(msg)
    if fps is None:
        fps = 3
    writer = animation.writers['ffmpeg'](fps=fps)
    anim.save(file_name, writer=writer, dpi=dpi)
    print("Created %s" % file_name)


def read_images(plotdir, fname_pattern='*.png'):

    import glob, os
    images = []
    files = glob.glob(os.path.join(plotdir, fname_pattern))
    for file in files:
        im = plt.imread(file)
        images.append(im)
    return images

def save_images(images, figsize=(8,6), plotdir='_plots', clobber=True, \
                fname_base='frame', format='png', verbose=False, **kwargs):

    make_plotdir(plotdir=plotdir, clobber=clobber)
    for frameno,image in enumerate(images):
        fig = imshow_noaxes(image, figsize)
        filename = '%s/%s%s.%s' % (plotdir, fname_base, str(frameno).zfill(5), format)
        plt.savefig(filename, format=format, **kwargs)
        plt.close(fig)
        if verbose:
            print("Saved ",filename)

def save_figs(figs, plotdir='_plots', clobber=True, \
                fname_base='frame', format='png', verbose=False, **kwargs):

    make_plotdir(plotdir=plotdir, clobber=clobber)
    for frameno,fig in enumerate(figs):
        filename = '%s/%s%s.%s' % (plotdir, fname_base, str(frameno).zfill(5), format)
        fig.savefig(filename, format=format, **kwargs)
        plt.close(fig)
        if verbose:
            print("Saved ",filename)


def make_image(fig, **kwargs):
    """
    Take a matplotlib figure *fig* and convert it to an image *im* that 
    can be viewed with imshow.
    """

    import io
    png = io.BytesIO()
    fig.savefig(png,format='png', **kwargs)
    png.seek(0)
    im = plt.imread(png)
    return im

def make_images(figs, **kwargs):
    """
    Take a list of matplotlib figures *figs* and convert to list of images.
    """

    images = []
    for fig in figs:
        im = make_image(fig, **kwargs)
        images.append(im)
    return images

def imshow_noaxes(im, figsize=(8,6)):
    fig = plt.figure(figsize=figsize)
    ax = plt.axes()
    plt.imshow(im)
    ax.axis('off')
    return fig
    
def interact_animate_images(images, figsize=(10,6), manual=False, TextInput=False):

    import ipywidgets
    from ipywidgets import interact, interact_manual

    def display_frame(frameno): 
        imshow_noaxes(images[frameno], figsize=figsize)

    if TextInput:
        if TextInput:
            print("Valid frameno values: from %i to %i" % (0,len(images)-1))
        widget = ipywidgets.IntText(min=0,max=len(images)-1, value=0)
    else:
        widget = ipywidgets.IntSlider(min=0,max=len(images)-1, value=0)

    if manual:
        interact_manual(display_frame, frameno=widget)
    else:
        interact(display_frame, frameno=widget)

def interact_animate_figs(figs, manual=False, TextInput=False):

    from IPython.display import display
    import ipywidgets
    from ipywidgets import interact, interact_manual

    def display_frame(frameno): 
        display(figs[frameno])

    if TextInput:
        widget = ipywidgets.IntText(min=0,max=len(figs)-1, value=0)
    else:
        widget = ipywidgets.IntSlider(min=0,max=len(figs)-1, value=0)

    if manual:
        if TextInput:
            print("Valid frameno values: from %i to %i" % (0,len(figs)-1))
        interact_manual(display_frame, frameno=widget)
    else:
        interact(display_frame, frameno=widget)


def make_anim_outputs_from_plotdir(plotdir='_plots', fignos='all',
        outputs=['mp4','html','rst'], file_name_prefix='',
        png_prefix='frame', figsize=None, dpi=None, fps=5, raw_html=''):

    """
    After running `make plots` using VisClaw, convert the png files in 
    the plots directory into stand-alone files that can be embedded in
    webpages or Sphinx documentation.

    Call this from a script that starts with:
        import matplotlib
        matplotlib.use('Agg')
    """
    import glob, re

    if fignos == 'all':
        # determine what fignos are used in the plotdir
        movie_files = glob.glob(plotdir + '/movie*html')
        if len(movie_files) == 0:
            print('No movie files found in %s' % plotdir)
            return
    
        fignos = []
        regexp = re.compile(r"movie[^ ]*fig(?P<figno>[0-9]*)[.html]")
        for f in movie_files:
            result = regexp.search(f)
            fignos.append(result.group('figno'))

        print("Found these figures: %s" % fignos)
    

    for figno in fignos:

        #fname_pattern = 'frame*fig%s.png' % figno
        fname_pattern = '%s*fig%s.png' % (png_prefix,figno)
        anim = make_anim(plotdir, fname_pattern, figsize, dpi)

        if 'mp4' in outputs:
            file_name = file_name_prefix + 'fig%s.mp4' % figno

            make_mp4(anim, file_name, fps=fps, \
                embed_frames=True, default_mode='once', dpi=dpi)

        if 'html' in outputs:
            file_name = file_name_prefix + 'fig%s.html' % figno
            make_html(anim, file_name, fps=fps, \
                embed_frames=True, default_mode='once', raw_html=raw_html)

        if 'rst' in outputs:
            file_name = file_name_prefix + 'fig%s.rst' % figno
            make_rst(anim, file_name, fps=fps, \
                embed_frames=True, default_mode='once')


def animate_from_plotdir(plotdir='_plots', figno=None, figsize=None,
                         dpi=None, fps=5):
    """
    Use the png files in plotdir to create an animation that is returned.
    Convenience function that calls make_anim with the 
        fname_pattern = 'frame*fig%s.png' % figno
    If figno==None, attempt to determine figno from the movies found in plotdir.
    """
    import glob, re
    
    if figno is None:
        # Try to determine figno from movie files
        movie_files = glob.glob(plotdir + '/movie*html')
        if len(movie_files) == 0:
            print('No movie files found in %s' % plotdir)
            return
    
        fignos = []
        regexp = re.compile(r"movie[^ ]*fig(?P<figno>[0-9]*)[.html]")
        for f in movie_files:
            result = regexp.search(f)
            fignos.append(result.group('figno'))

        if len(fignos)==0:
            print('Could not determine figno automatically')
            return None
            
        if len(fignos) > 1:
            print("Found multiple fignos: %s" % fignos)
            
        figno = int(fignos[0])
        print("Using figno = %i" % figno)
        
    fname_pattern = 'frame*fig%s.png' % figno
    anim = make_anim(plotdir, fname_pattern, figsize, dpi)
    return anim
        
        
        
