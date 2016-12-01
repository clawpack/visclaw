
"""
JSAnimation sometimes puts a space between anim and the hash code in lines such as 
    onclick="anim6c16c71bbda280b...
The webpage then shows a broken link.

fix_file function below fixes a single file.
fix_movie fixes a file produced by Clawpack plotting routines.
fix_movies fixes all movie files in a specified plotdir.

Default if run from command line is to fix all movies in _plots.
Can specify plotdir and optionally figno for movie on the command line.

It would be better to figure out the bug in JSAnimation.html_writer.
"""

from __future__ import absolute_import
from __future__ import print_function
import os, glob

def fix_file(fname, verbose=True):
    f = open(fname,'r')
    html = f.read()
    f.close()

    html = html.replace('anim ','anim')

    f = open(fname,'w')
    f.write(html)
    f.close()
    if verbose:
        print("Fixed file ",fname)

def fix_movie(plotdir, figno):
    fname = os.path.join(plotdir, 'movieframe_allframesfig%s.html' % figno)
    fix_file(fname)
    
def fix_movies(plotdir='_plots'):
    pattern = r'movieframe_allframesfig*.html'
    files = glob.glob(os.path.join(plotdir, pattern))
    for fname in files:
        fix_file(fname)
    
if __name__=="__main__":
    import sys
    args = sys.argv[1:]   # any command line arguments
    if len(args) < 2:
        fix_movies(*args)
    else:
        fix_movie(*args)

