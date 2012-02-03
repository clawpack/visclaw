

.. _plotting_faq:

***********************
Plotting hints and FAQ
***********************

.. seealso:: 
    :ref:`plotting`, 
    :ref:`setplot`, 
    :ref:`plotexamples` 


.. contents::

More to come!

What's the difference between ``make .plots`` and ``make plots`` ?
------------------------------------------------------------------

The default Makefile configuration in Version 4.5.1 was changed to allow two
different targets ``.plots`` and ``plots``.  The former creates a 
hidden file ``.plots`` whose modification time is used to check dependencies.
The plotting commands will be performed again only if the output of
``setplot`` file has been changed, and will also re-run the code if it appears
that the output is out of date relative to the ``setrun`` file, for example.
If you want to create the plots without checking dependencies (and perhaps
accidentally re-running the code), use the ``make plots`` option.
``plots`` is a phony target in the default Makefile.



How to plot a something other than a component of q?
----------------------------------------------------

Objects of class :ref:`ClawPlotItem` have an attribute ``plot_var``.  If
this is set to an integer than the corresponding component of q is plotted
(remembering that Python indexing starts at 0, so ``plot_var = 0`` will
specify plotting the first component of q, for example).

If plot_var is a function then this function is applied to applied to 
:ref:`current_data` and should return the array of values to be plotted.
For an example, see :ref:`plotexample-acou-1d-6`.

Sometimes you want to plot something other than the solution on the patch, 
for example to add another feature to a plot of the solution. This can be
done via an ``afteraxes`` command, for example, which is called after all
items have been plotted on the current axes.  See :ref:`ClawPlotAxes` for
details and an example.


How to add another curve to a plot, e.g. the true solution?
-----------------------------------------------------------

The ``afteraxes`` attribute of a :ref:`ClawPlotAxes`` object can be specified as
either a string or a function.  The string is executed (using ``exec(...)``) or
the function is called after performing
all plots on these axes (as specified by :ref:`ClawPlotItem`` objects). 
This can be used to add a curve to a plot.

For example, if the true solution to an advection equation
is known to be :math:`q(x,t) = \sin(x+t)`, this could be added to a plot  as a
red curve via::

    def add_true_solution(current_data):
        from pylab import sin, plot
        x = current_data.x
        t = current_data.t
        qtrue = sin(x+t)
        plot(x, qtrue, 'r')

    plotaxes.afteraxes = add_true_solution


How to change the title in a plot?
----------------------------------

The ``title`` attribute of a :ref:`ClawPlotAxes`` object determines the title that
appears a the top of the plot.  

The ``title_with_t`` attributed determines if the time is included in this title.
If True (the default value), then "at time t = ..." is appended to the title.
The time is printed using format ``14.8f`` if ``(t>=0.001) & (t<1000.)``,
or format ``14.8e`` more generally.

It is also possible to change the title using and afteraxes function.  For
example, to create a larger title with fontsize 20 and only 4 digits in t::

    def add_title(current_data):
        from pylab import title
        t = current_data.t
        title("Solution at time t = %10.4e" % t, fontsize=20)

    plotaxes.afteraxes = add_title


How to specify ``outdir``, the directory to find ``fort.*`` files for plotting?
-------------------------------------------------------------------------------

This is normally determined by the ``outdir`` attribute of
the :ref:`ClawPlotData` object directing the plotting.  But see the next FAQ
for the option of using different directories for some plot items (e.g. to
compare results of two computations).

If you are making a set of hardcopy plots using::

    $ make .plots

or
    
    $ make plots


then ``outdir`` is specified in the Makefile by setting the ``CLAW_OUTDIR``
variable.

If you are making plots interactively using Iplotclaw_, then you can
directly specify the ``outdir`` as a parameter, e.g.::

    In[1]: ip=Iplotclaw(outdir="_output");   ip.plotloop()

If you don't specify this parameter, `Iplotclaw`_ will look for a file
``.output`` in the current directory.  If you created the ``fort.*`` files by
the command::

    $ make .output

then the output directory is set in the Makefile and the file ``.output``
contains the path to the output directory.

Note: If you use

    $ make output

which does not check dependencies, this also 
does not create a target file ``.output``.


If the file ``.output`` does not exist,  ``outdir = '.'`` is used by
default, the current directory.  

Note that if you stop a calculation mid-stream using ``<ctrl>-C``, the file
``.output`` may not exist or be correct, since this file is written after
the execution finishes.  

How to specify a different ``outdir`` for some plot item?
-------------------------------------------------------------

If you want one plot item on an axis to use the default ``plotdata.outdir``
while another to take data from a different directory (in order to compare
two computations, for example), you can set the ``outdir``
attribute of a :ref:`ClawPlotItem` directly.  If you do not set it, by
default it inherits from the :ref:`ClawPlotFigure` object this item belongs
to.

For example, you might have the following in your ``setplot`` function::

    plotfigure = plotdata.new_plotfigure(name='compare', figno=1)
    plotaxes = plotfigure.new_plotaxes()

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 0
    plotitem.plotstyle = '-o'
    plotitem.color = 'b'

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    import os
    plotitem.outdir = os.path.join(os.getcwd(), '_output2')
    plotitem.plot_var = 0
    plotitem.plotstyle = '-+'
    plotitem.color = 'r'

This would plot results from ``plotdata.outdir`` as blue circles and results
from ``./_output2`` as red plus signs.  It's best to give the full path
name, e.g. as done here using ``os.path.join(os.getcwd(), '_output2')``.

How to set plot parameters that are not provided as attributes of :ref:`ClawPlotItem``?
----------------------------------------------------------------------------------------

Some commonly used plotting parameters can be specified as an attribute of a
:ref:`ClawPlotItem``, for example::

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 0
    plotitem.plotstyle = '-'
    plotitem.color = 'b'
    
specifies plotting a blue line.  These attributes are used in the call to the
matplotlib ``plot`` function.  The ``plot`` function has many other keyword
parameters that are not all duplicated as attributes of :ref:`ClawPlotItem``.  To
change these, the ``kwargs`` attribute can be used.  

For example, to plot as above, but with a wider blue line, append the following::

    plotitem.kwargs = {'linewidth': 2}

If you try to specify the same keyword argument two different ways, e.g.::

    plotitem.color = 'b'
    plotitem.kwargs = {'linewidth': 2, 'color': 'r'}

the  value in ``kwargs`` takes precedence.  It is the ``kwargs`` dictionary that
is actually used in the call, and the ``color`` attribute is checked only if it
has not been defined by the user in the ``kwargs`` attribute.

How to change the size or background color of a figure?
-------------------------------------------------------

By default, a figure is created of the default matplotlib size, with a tan
background.  Any desired
keyword arguments to the matplotlib `figure <??>`_ command can
be passed using the ``kwargs`` attributed of :ref:`ClawPlotFigure``.  For
example, to create a figure that is 10 inches by 5 inches with a pink
background::

    plotfigure = plotdata.new_plotfigure(name='pinkfig', figno=1)
    plotfigure.kwargs = {'figsize': [10,5],  'facecolor': [1, .7, .7]}



How to debug setplot.py?
--------------------------

Suppose you are working in an interactive Python shell such as ipython and
encounter the following when trying to plot with `Iplotclaw`_::

    In [3]: ip=Iplotclaw(); ip.plotloop()
    *** Error in call_setplot: Problem executing function setplot
    *** Problem executing setplot in Iplotclaw
        setplot =  setplot.py
    *** Either this file does not exist or 
        there is a problem executing the function setplot in this file.
    *** PLOT PARAMETERS MAY NOT BE SET! ***
    
    Interactive plotting for Clawpack output... 
    
    Plotting data from outdir =  _output
    Type ? at PLOTCLAW prompt for list of commands
    
        Start at which frame [default=0] ? 
    
    
This tells you that there was some problem importing ``setplot.py``, but is not
very informative and it is hard to debug from within the
``Iplotclaw.plotloop``
method. You may also run into this if you modify ``setplot.py``
(inadvertantly introducing a bug)
and then use the ``resetplot`` option::

    PLOTCLAW > resetplot
    Executing setplot from  setplot.py
    *** Error in call_setplot: Problem executing function setplot
    *** Problem re-executing setplot
    PLOTCLAW > 


If you can't spot the bug by examing ``setplot.py``, it is easiest to debug
by exiting the plotloop and doing::
    
    PLOTCLAW > q
    quitting...
    
    In [4]: import setplot
    In [5]: pd = ip.plotdata
    In [6]: pd = setplot.setplot(pd)
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    
          8 
          9     # Figure for q[0]
    ---> 10     plotfigure = plotdata.new_plotfgure(name='q[0]', figno=1)
         11 
         12     # Set up for axes in this figure:
    
    AttributeError: 'ClawPlotData' object has no attribute 'new_plotfgure'
    
    
In this case, the error is that ``new_plotfigure`` is mis-spelled.

In ipython you can also easily turn on the Python debugger pdb::

    In [9]: pdb
    Automatic pdb calling has been turned ON

    In [10]: pd = setplot.setplot(pd)
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
          8 
          9     # Figure for q[0]
    ---> 10     plotfigure = plotdata.new_plotfgure(name='q[0]', figno=1)
         11 
         12     # Set up for axes in this figure:

    AttributeError: 'ClawPlotData' object has no attribute 'new_plotfgure'

    ipdb> 

For more complicated debugging you could now explore the current state using
any pdb commands, described in the `documentation
<http://docs.python.org/library/pdb.html>`_.  See also 
the `ipython documentation
<http://ipython.scipy.org/doc/manual/html/index.html>`_.


