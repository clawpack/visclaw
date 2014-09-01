"""
Requires the JSAnimation package,
   https://github.com/jakevdp/JSAnimation 

"""

import glob
from matplotlib import image, animation
from matplotlib import pyplot as plt
from JSAnimation import IPython_display

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
    print "Figure files for each frame will be stored in ", plotdir


def save_frame(frameno, plotdir='_plots', fname_base='frame', verbose=False):
    """
    After giving matplotlib commands to create the plot for a single frame 
    of the desired animation, this can be called to save the figure with
    the appropriate file name such as _plots/frame00001.png.
    """

    plt.draw()
    filename = '%s/%s%s.png' % (plotdir, fname_base, str(frameno).zfill(5))
    plt.savefig(filename)
    if verbose:
        print "Saved ",filename


def make_anim(plotdir, fname_base='frame', figsize=(10,6)):
    """
    Assumes that a set of frames are available as png files in directory _plots,
    numbered consecutively, e.g. frame0000.png, frame0001.png, etc.

    Creates an animation based display each frame in turn, and returns anim.

    You can then display anim in an IPython notebook, or
    call make_html(anim) to create a stand-alone webpage.
    """

    import glob   # for finding all files matching a pattern

    # Find all frame files:
    filenames = glob.glob('%s/%s*.png' % (plotdir, fname_base))

    # sort them into increasing order:
    filenames=sorted(filenames)

    fig = plt.figure(figsize=figsize, dpi=80)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')  # so there's not a second set of axes
    im = plt.imshow(image.imread(filenames[0]))

    def init():
        im.set_data(image.imread(filenames[0]))
        return im,

    def animate(i):
        image_i=image.imread(filenames[i])
        im.set_data(image_i)
        return im,

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                          frames=len(filenames), interval=200, blit=True)

    return anim


def make_html(anim, file_name='anim.html', title=None, \
              fps=None, embed_frames=True, default_mode='loop'):
    """
    Take an animation created by make_anim and convert it into a stand-alone
    html file.
    """

    from JSAnimation.IPython_display import anim_to_html

    html_body = anim_to_html(anim, fps=fps, embed_frames=embed_frames, \
                 default_mode=default_mode)

    html_file = open(file_name,'w')
    html_file.write("<html>\n <h1>%s</h1>\n" % title)
    html_file.write(html_body)
    html_file.close()
    print "Created %s" % file_name

