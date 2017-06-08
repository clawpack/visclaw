"""
A tool to add a desired legend to an existing plot more easily when 
adaptive mesh refinement is used in VisClaw.

To do fancier things with legends, see:
    http://matplotlib.org/users/legend_guide.html
"""

def add_legend(labels,colors='k',linestyles='-',markers='', **kwargs):
    """
    Add a legend to an existing plot with a specified set of line colors.
    Input:
        labels:  list of labels
        colors:  list of colors, of same length as labels
            or a single string used for all entries.
            Default is 'k', so all will be black.
        linestyles: list of strings of same length as labels, 
            or a single string used for all entries.
            Default is '-', so all will be solid lines. 
            Set to '' for no line.
        markers: list of strings of same length as labels,  
            or a single string used for all entries.
            Default is '', so no marker for any entry
        kwargs: keyword arguments to be passed to `plt.legend`, e.g.
            `loc` or `fontsize`.
    There is one entry in the legend for each color/label.
    
    Useful for annotating an AMR plot when plots were made
    by looping over patches.  In this case it's not possible to simply add
    a label as a kwarg to the plot command or the legend will contain an
    entry for every patch.    
    """
    
    import matplotlib.lines as mlines
    import matplotlib.pyplot as plt
    
    # convert single string to list of correct length:
    
    if type(colors) is str:
        colors = len(labels)*[colors]

    if type(linestyles) is str:
        linestyles = len(labels)*[linestyles]

    if type(markers) is str:
        markers = len(labels)*[markers]
            
    handles = []
    for k in range(len(colors)):
          handle = mlines.Line2D([], [], color=colors[k], 
                    linestyle=linestyles[k], marker=markers[k], 
                    label=labels[k])
          handles.append(handle)
              
    plt.legend(handles=handles,**kwargs)
    
