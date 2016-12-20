
"""
Tools to assist interpolating from fort.gauge output to a given
set of times (e.g. equally spaced).

Example:
  Set gaugeno to the desired gauge number, iq to the component of q to 
  plot, e.g. iq=3 for surface eta.

    import gauge_interp
    getgauge = gauge_interp.make_getgauge(output='_outdir')
    gf,t1,t2 = gauge_interp.gauge_function(getgauge, gaugeno, iq)
    t = numpy.linspace(t1,t2,50)  # desired times of interpolation
    gt = gf(t)
    
Then gt will be an array of the same length as t containing interpolated 
values (piecewise linear).

See also the test function below, which can be run via:

    $ cd $CLAW/geoclaw/examples/tsunami/chile2010
    $ make .output
    $ python
    >>> from clawpack.visclaw import gauge_interp
    >>> gauge_interp.test()

"""


from __future__ import absolute_import
def make_getgauge(outdir='_output'):
    """
    Create function getgauge that will grab one set of gauge data
    from the fort.gauge file in directory specified by outdir.
    """
    from clawpack.visclaw.data import ClawPlotData
    plotdata = ClawPlotData()
    plotdata.outdir = outdir
    getgauge = plotdata.getgauge
    return getgauge
    

def gauge_function(getgauge, gaugeno, iq):
    """
    Given getgauge function, return a function that
    can be used to evaluate the iq component of q at any time
    in the interval covered by the gauge output.

    Also returns t1, t2 the end points of validity.
    
    Does piecewise linear interpolation based on g.q and g.q[iq,:]
    where g is the gauge data.
    """

    from scipy import interpolate

    g = getgauge(gaugeno)
    gf = interpolate.interp1d(g.t, g.q[iq,:])
    t1 = g.t[0]
    t2 = g.t[-1]
    return gf, t1, t2


def test(gaugeno=32412, iq=3):

    # Test should work in $CLAW/geoclaw/examples/tsunami/chile2010
    import numpy
    import matplotlib.pyplot as plt

    # interpolate at a set of times t:
    getgauge = make_getgauge(outdir='_output')
    gf,t1,t2 = gauge_function(getgauge, gaugeno, iq)
    t = numpy.linspace(t1,t2,100)
    gt = gf(t)

    # Plot the two for comparison:
    plt.plot(t,gt,'ro', markersize=5, label='interpolated')
    g = getgauge(gaugeno)
    plt.plot(g.t, g.q[iq,:], 'k-',label='original data')
    plt.legend()
    plt.show()

