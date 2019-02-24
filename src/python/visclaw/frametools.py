#!/usr/bin/env python
"""
Module frametools for plotting frames of time-dependent data.
"""

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import traceback
import glob
import time
import types

import six
from six.moves import input
# "reload" is only available from a module in Python 3.
if sys.version_info[0] >= 3:
    if sys.version_info[1] >= 4:
        from importlib import reload
    else:
        from imp import reload

import clawpack.clawutil.data as clawdata
from clawpack.visclaw.data import ClawPlotData
from clawpack.visclaw import setplot_default
from clawpack.pyclaw import Solution

import numpy as np
import matplotlib.pyplot as plt
from numpy import ma
from clawpack.visclaw import colormaps
from matplotlib.colors import Normalize



#==============================================================================
def plotframe(frameno, plotdata, verbose=False, simple=False, refresh=False):
#==============================================================================
    """
    Plot a single frame from the computation.

    This routine checks input, loads the appropriate frame from each
    outdir, and then calls plot_frame.

    If simple == True, then plot_frame is not called.  In this case,
    plotdata.setplot should actually be a (matplotlib) function that takes a
    Solution object and plots it.
    """

    if verbose:  print('    Plotting frame %s ... '  % frameno)

    if simple:
        plotfun = plotdata.setplot
        sol = Solution(frameno,path=plotdata.outdir,file_format=plotdata.format)
        plotfun(sol)
        return

    try:
        plotfigure_dict = plotdata.plotfigure_dict
    except AttributeError:
        print('*** Error in plotframe: plotdata missing plotfigure_dict')
        print('*** This should not happen')
        return None

    if len(plotfigure_dict) == 0:
        print('*** Warning in plotframe: plotdata has empty plotfigure_dict')
        print('*** Apparently no figures to plot')

    plotdata.set_outdirs()  # set _outdirs attribute to be list of
                                      # all outdirs for all items

    framesolns = []
    # loop over all outdirs:
    if len(plotdata._outdirs) == 0:
        plotdata._outdirs = [plotdata.outdir]
    for outdir in plotdata._outdirs:
        framesolns.append(plotdata.getframe(frameno, outdir, refresh=refresh))


    # It seems that 'current_data', returned from plot_frame,
    # doesn't get used at all.
    plot_frame(framesolns, plotdata, frameno,verbose=verbose)


#==============================================================================
def plot_frame(framesolns,plotdata,frameno=0,verbose=False):
#==============================================================================
    """
    Plot a single frame from the computation.

    This routine checks input and then calls plotitemN for the
    proper space dimension.  Framesolns is a list of solutions at the same time
    but usually from different output directories.
    """

    if type(framesolns) is not list:
        framesolns = [framesolns]

    t = framesolns[0].t

    # initialize current_data, which will be passed
    # to afterframe, afteraxes, afterpatch commands
    current_data = clawdata.ClawData()
    current_data.add_attribute('user',{})   # for user specified attributes
                                            # to avoid potential conflicts
    current_data.add_attribute('plotdata',plotdata)
    current_data.add_attribute('frameno',frameno)
    current_data.add_attribute('t',t)
    current_data.add_attribute('var',None)
    current_data.add_attribute('plotaxes',None)
    current_data.add_attribute('plotfigure',None)

    # call beforeframe if present, which might define additional
    # attributes in current_data or otherwise set up plotting for this
    # frame.
    beforeframe =  getattr(plotdata, 'beforeframe', None)
    current_data = run_str_or_func(beforeframe,current_data)


    # iterate over each single plot that makes up this frame:
    # -------------------------------------------------------

    if plotdata.mode() == 'iplotclaw':
        plt.ion()
        print('    Plotting Frame %s at t = %s' % (frameno,t))
        requested_fignos = plotdata.iplotclaw_fignos
    else:
        requested_fignos = plotdata.print_fignos

    plotted_fignos = []
    kml_fignos = []

    plotdata = set_show(plotdata)   # set _show attributes for which figures
                                    # and axes should be shown.

    # loop over figures to appear for this frame:
    # -------------------------------------------

    for figname in plotdata._fignames:
        plotfigure = plotdata.plotfigure_dict[figname]
        if (not plotfigure._show) or (plotfigure.type != 'each_frame'):
            continue  # skip to next figure

        figno = plotfigure.figno
        if (requested_fignos != 'all') and (figno not in requested_fignos):
            continue # skip to next figure

        plotted_fignos.append(figno)
        if plotfigure.use_for_kml:
            kml_fignos.append(figno)

        if 'facecolor' not in plotfigure.kwargs:
            # use Clawpack's default bg color (tan)
            plotfigure.kwargs['facecolor'] = '#ffeebb'

        # create figure and set handle:
        plotfigure._handle = plt.figure(num=figno, **plotfigure.kwargs)

        #plt.ioff()
        if plotfigure.clf_each_frame:
            plt.clf()

        plotaxes_dict = plotfigure.plotaxes_dict

        if (len(plotaxes_dict) == 0) or (len(plotfigure._axesnames) == 0):
            print('*** Warning in plotframe: plotdata has empty plotaxes_dict')
            print('*** Apparently no axes to plot in figure ',figno)

        # loop over axes to appear on this figure:
        # ----------------------------------------

        for axesname in plotfigure._axesnames:
            plotaxes = plotaxes_dict[axesname]
            if not plotaxes._show:
                continue   # skip this axes if no items show

            # create the axes:
            axescmd = getattr(plotaxes,'axescmd','subplot(1,1,1)')
            axescmd = 'plotaxes._handle = plt.%s' % axescmd
            exec(axescmd)

            current_data.plotaxes = plotaxes
            current_data.plotfigure = plotaxes._plotfigure

            beforeaxes = getattr(plotaxes,'beforeaxes',None)
            current_data = run_str_or_func(beforeaxes,current_data)
                

            # NOTE: This was rearranged December 2009 to
            # loop over patches first and then over plotitems so that
            # finer patches will plot over coarser patches of other items.
            # Needed in particular if masked arrays are used, e.g. if
            # two different items do pcolor plots with different color maps
            # for different parts of the domain (e.g. water and land).

            for i, framesoln in enumerate(framesolns):

                if abs(framesoln.t - t) > 1e-12:
                    print('*** Warning: t values do not agree for frame ',frameno)
                    print('*** t = %22.15e for outdir = %s' % (t,plotdata.outdir))
                    print('*** t = %22.15e for outdir = %s' % (framesoln.t,plotdata._outdirs[i]))

                current_data.add_attribute('framesoln',framesoln)

                # loop over patches:
                # ----------------

                for stateno,state in enumerate(framesoln.states):

                    patch = state.patch

                    current_data.add_attribute('patch',patch)
                    current_data.add_attribute("level",1)
                    current_data.add_attribute('q',state.q)
                    current_data.add_attribute('aux',state.aux)
                    current_data.add_attribute('xlower',patch.dimensions[0].lower)
                    current_data.add_attribute('xupper',patch.dimensions[0].upper)

                    current_data.add_attribute("x",patch.grid.p_centers[0])
                    current_data.add_attribute("dx",patch.delta[0])


                    if patch.num_dim == 2:
                        current_data.add_attribute('ylower',patch.dimensions[1].lower)
                        current_data.add_attribute('yupper',patch.dimensions[1].upper)
                        current_data.add_attribute('y',patch.grid.p_centers[1])
                        current_data.add_attribute('dy',patch.delta[1])

                    if plotfigure.use_for_kml:

                        # -------------------------------------------------------------
                        # Mask out all coarse grid regions that are under fine grids
                        # This could be made into a subroutine
                        # -------------------------------------------------------------
                        this_level = patch.level

                        xc_centers,yc_centers = patch.grid.c_centers
                        mask_coarse = np.empty(xc_centers.shape, dtype=bool)
                        mask_coarse.fill(False)

                        # iterate over all grids to see which one masks this grid
                        for stateno_fine,state_fine in enumerate(framesoln.states):
                            # iterate over all patches, and find any finer level grids that are
                            # sitting on top of this patch/grid/state.
                            patch_fine = state_fine.patch

                            # Only look at patches one level finer
                            if patch_fine.level != this_level+1:
                                continue

                            xlower_fine = patch_fine.dimensions[0].lower
                            xupper_fine = patch_fine.dimensions[0].upper
                            ylower_fine = patch_fine.dimensions[1].lower
                            yupper_fine = patch_fine.dimensions[1].upper

                            m1 = (xc_centers > xlower_fine) & (xc_centers < xupper_fine)
                            m2 = (yc_centers > ylower_fine) & (yc_centers < yupper_fine)

                            # Mask all fine grid regions
                            mask_coarse = (m1 & m2) | mask_coarse

                        current_data.add_attribute('mask_coarse',mask_coarse)
                        # -------------------------------------------------------------
                        # Done with masking
                        # -------------------------------------------------------------


                    # loop over items:
                    # ----------------

                    for itemname in plotaxes._itemnames:

                        plotitem = plotaxes.plotitem_dict[itemname]

                        try:
                            item_outdir = plotitem.outdir
                            if not plotitem.outdir:
                                item_outdir = plotdata.outdir
                            if item_outdir != plotdata._outdirs[i]:
                                # skip to next item
                                continue
                        except (NameError, AttributeError):  # no outdir if plotting from memory
                            pass

                        num_dim = plotitem.num_dim

                        # option to suppress printing some levels:
                        amr_data_show = plotitem.amr_data_show
                        if len(amr_data_show) > 0:
                            j = min(len(amr_data_show), patch.level) - 1
                            show_this_level = amr_data_show[j]
                        else:
                            show_this_level = True

                        if plotitem._show and show_this_level:
                            if num_dim == 1:
                                plotitem_fun = plotitem1
                            elif num_dim == 2:
                                plotitem_fun = plotitem2
                            current_data = plotitem_fun(framesoln,plotitem,current_data,stateno)

                            if verbose:
                                print('      Plotted  plotitem ', itemname)

                    # end of loop over plotitems
                # end of loop over patches
            # end of loop over framesolns


            for itemname in plotaxes._itemnames:
                plotitem = plotaxes.plotitem_dict[itemname]
                if plotitem.afteritem:
                    print("*** ClawPlotItem.afteritem is deprecated")
                    print("*** use ClawPlotAxes.afteraxes ")
                    print("*** or  ClawPlotItem.afterpatch instead")
                try:
                    if plotfigure.use_for_kml:
                        # Build colorbar for Google Earth (now done in setplot.py)
                        pass
                    elif plotitem.has_attribute('add_colorbar') and plotitem.add_colorbar:
                        pobj = plotitem._current_pobj # most recent plot object
                        # set dictionary values for keywords explicitly set:
                        if plotitem.colorbar_shrink is not None:
                            plotitem.colorbar_kwargs['shrink'] = \
                                    plotitem.colorbar_shrink
                        if plotitem.colorbar_ticks is not None:
                            plotitem.colorbar_kwargs['ticks'] = \
                                    plotitem.colorbar_ticks

                        cbar = plt.colorbar(pobj, **plotitem.colorbar_kwargs)

                        if plotitem.has_attribute('colorbar_tick_labels'):
                            if plotitem.colorbar_tick_labels is not None:
                                cbar.ax.set_yticklabels(plotitem.colorbar_tick_labels)
                        if plotitem.colorbar_label is not None:
                            cbar.set_label(plotitem.colorbar_label)
                except:
                    print("*** problem generating colorbar")
                    pass

            if plotfigure.use_for_kml:
                pass
            else:
                if plotaxes.title_with_t:
                    if (t==0.) | ((t>=0.001) & (t<1000.)):
                        plt.title("%s at time t = %14.8f" % (plotaxes.title,t))
                    else:
                        plt.title("%s at time t = %14.8e" % (plotaxes.title,t))
                else:
                    plt.title(plotaxes.title)


            # call an afteraxes function if present:
            afteraxes =  getattr(plotaxes, 'afteraxes', None)
            current_data = run_str_or_func(afteraxes,current_data)

            if plotaxes.scaled:
                plt.axis('scaled')
            elif plotaxes.image:
                plt.axis('image')

            # set axes limits:
            if (plotfigure.use_for_kml and plotfigure.kml_use_figure_limits):
                if (plotfigure.kml_xlimits is not None) & (type(plotfigure.kml_xlimits) is not str):
                    try:
                        plt.xlim(plotfigure.kml_xlimits[0], plotfigure.kml_xlimits[1])
                    except:
                        print(" ")
                        print("*** KML error : Set plotfigure.kml_xlimits")
                        print(" ")
                        return

                if (plotfigure.kml_ylimits is not None) & (type(plotfigure.kml_ylimits) is not str):
                    try:
                        plt.ylim(plotfigure.kml_ylimits[0], plotfigure.kml_ylimits[1])
                    except:
                        print(" ")
                        print("*** KML error : Set plotfigure.kml_ylimits")
                        print(" ")
                        return
            else:
                if (plotaxes.xlimits is not None) & (type(plotaxes.xlimits) is not str):
                    try:
                        plt.xlim(plotaxes.xlimits[0], plotaxes.xlimits[1])
                    except:
                        pass  # let axis be set automatically
                if (plotaxes.ylimits is not None) & (type(plotaxes.ylimits) is not str):
                    try:
                        plt.ylim(plotaxes.ylimits[0], plotaxes.ylimits[1])
                    except:
                        pass  # let axis be set automatically

            # end of loop over plotaxes
        # end of loop over plotfigures


    # call an afterframe function if present:
    afterframe =  getattr(plotdata, 'afterframe', None)
    current_data = run_str_or_func(afterframe,current_data)

    if plotdata.mode() == 'iplotclaw':
        plt.ion()
    for figno in plotted_fignos:
        plt.figure(figno)
        plt.draw()

    if verbose:
        print('    Done with plotframe for frame %i at time %g' % (frameno,t))


    # print the figure(s) to file(s) if requested:
    if (plotdata.mode() != 'iplotclaw') & plotdata.printfigs:
        # iterate over all figures that are to be printed:
        for figname in plotdata._fignames:
            plotfigure = plotdata.plotfigure_dict[figname]
            figno = plotfigure.figno
            if figno in plotted_fignos:
                if figno in kml_fignos:
                    printfig(frameno=frameno, figno=figno, \
                             format=plotdata.print_format, plotdir=plotdata.plotdir,\
                             verbose=verbose,kml_fig=True,kml_dpi=plotfigure.kml_dpi,
                             kml_figsize=plotfigure.kml_figsize)
                else:
                    printfig(frameno=frameno, figno=figno, \
                             format=plotdata.print_format, plotdir=plotdata.plotdir,\
                             verbose=verbose,kml_fig=False)

    return current_data
    # end of plotframe


def run_str_or_func(str_or_func,current_data):
    if str_or_func is None:
        return current_data
    if isinstance(str_or_func, str):
        exec(str_or_func)
    else:
        output = str_or_func(current_data)
        if output:
            return output
    return current_data


def params_dict(plotitem, base_params, level_params, level):
    """
    Create a dictionary containing the plot parameters.

    For each level_param check if there is an amr_ list for this
    parameter and if so select the value corresponding to the level of
    this patch.  Otherwise, use plotitem attribute of this name.
    """
    pp = {}
    for plot_param in base_params:
        pp[plot_param] = getattr(plotitem, plot_param, None)


    for plot_param in level_params:
        amr_plot_param = "amr_%s" % plot_param
        amr_list = getattr(plotitem, amr_plot_param, [])
        if len(amr_list) > 0:
            index = min(level, len(amr_list)) - 1
            pp[plot_param] = amr_list[index]
        else:
            pp[plot_param] = getattr(plotitem, plot_param, None)

    return pp

#==================================================================
def plotitem1(framesoln, plotitem, current_data, stateno):
#==================================================================
    """
    Make a 1d plot for a single plot item for the solution in framesoln.

    The current_data object holds data that should be passed into
    afterpatch or afteraxes if these functions are defined.  The functions
    may add to this object, so this function should return the possibly
    modified current_data for use in other plotitems or in afteraxes or
    afterframe.

    """

    plotdata = plotitem._plotdata

    state = framesoln.states[stateno]
    patch = state.patch
    current_data.patch = patch
    current_data.q = state.q
    current_data.aux = state.aux

    # level not currently set in 1d, default to level = 1:
    current_data.level = getattr(patch,'level',1)

    t = framesoln.t

    # the following plot parameters should be set and independent of
    # which AMR level a patch is on:

    base_params = ['plot_type','afteritem','mapc2p','MappedGrid','gaugeno']

    # the following plot parameters may be set, depending on what
    # plot_type was requested:

    # Note: not all of these are initialized in data.py - need to clean up
    level_params = ['plot_var','afterpatch','plotstyle','color','kwargs',\
             'plot_var2','fill_where','map_2d_to_1d','data_show']

    pp = params_dict(plotitem, base_params, level_params, patch.level)

    if pp['mapc2p'] is None:
        # if this item does not have a mapping, check for a global mapping:
        pp['mapc2p'] = getattr(plotdata, 'mapc2p', None)

    if pp['plot_type'] == '1d':
        pp['plot_type'] = '1d_plot'  # '1d' is deprecated

    if pp['plot_type'] == '1d_gauge_trace':
        gaugesoln = plotdata.getgauge(pp['gaugeno'])
        xc_centers = None
        xc_edges = None

    elif pp['plot_type'] in ['1d_plot', '1d_semilogy', '1d_fill_between',
            '1d_empty','1d_from_2d_data', '1d_pwconst']:
        var = get_var(state,pp['plot_var'],current_data)
        current_data.var = var

    else:
        raise ValueError("Unrecognized plot_type: %s" % pp['plot_type'])

    if pp['plot_type'] == '1d_fill_between':
        var  = get_var(state,pp['plot_var'],current_data)
        var2 = get_var(state,pp['plot_var2'],current_data)
        current_data.var = var
        current_data.add_attribute('var2',var2)

    # Grid mapping:

    if pp['MappedGrid'] is None:
        pp['MappedGrid'] = (pp['mapc2p'] is not None)

    if (pp['MappedGrid'] & (pp['mapc2p'] is None)):
        print("*** Warning: MappedGrid == True but no mapc2p specified")
    elif pp['MappedGrid']:
        p_centers = pp['mapc2p'](current_data.x)
    else:
        p_centers = current_data.x

    if pp['plot_type'] == '1d_from_2d_data':
        if not pp['map_2d_to_1d']:
            print('*** Error, plot_type = 1d_from_2d_data requires ')
            print('*** map_2d_to_1d function as plotitem attribute')
            raise
            return
        p_centers, var = pp['map_2d_to_1d'](current_data)
        p_centers = p_centers.flatten()  # convert to 1d
        var = var.flatten()  # convert to 1d

    # The plot commands using matplotlib:

    if pp['color']:
        pp['kwargs']['color'] = pp['color']

    if pp['data_show']:
        if (pp['plot_type'] in ['1d_plot','1d_from_2d_data']):
            pobj=plt.plot(p_centers,var,pp['plotstyle'],**pp['kwargs'])

        elif pp['plot_type'] == '1d_semilogy':
            pobj=plt.semilogy(p_centers,var,pp['plotstyle'], **pp['kwargs'])

        elif pp['plot_type'] == '1d_fill_between':
            if pp['fill_where']:
                pp['fill_where'] = pp['fill_where'].replace('plot_var','var')
                pp['fill_where'] = pp['fill_where'].replace('plot_var2','var2')
                pobj=plt.fill_between(p_centers,var,var2,pp['fill_where'],**pp['kwargs'])
            else:
                pobj=plt.fill_between(p_centers,var,var2,**pp['kwargs'])

        elif pp['plot_type'] == '1d_pwconst':

            # should improve this to also work on mapped grid
            xc_edges = patch.grid.c_nodes[0]
            medges = len(xc_edges)
            mcells = medges - 1  # number of grid cells
            # double up points for pw constant plot
            xc_edges2 = np.reshape(np.vstack((xc_edges,xc_edges)).T, 
                (2*medges,))
            xc_edges2 = xc_edges2[1:-1]  # discard first and last
            var2 = np.reshape(np.vstack((var,var)).T, (2*mcells,))
            pobj=plt.plot(xc_edges2,var2,pp['plotstyle'],**pp['kwargs'])

        elif pp['plot_type'] == '1d_gauge_trace':

            gauget = gaugesoln.t
            gaugeq = gaugesoln.q[3,:]
            pobj=plt.plot(gauget, gaugeq)

            # interpolate to the current time t:
            try:
                i1 = np.where(gauget < t)[0][-1]
                i1 = min(i1,len(gauget)-2)
                slope = (gaugeq[i1+1]-gaugeq[i1]) / (gauget[i1+1]-gauget[i1])
                qt = gaugeq[i1] + slope * (t-gauget[i1])
            except IndexError:
                qt = gaugeq[0]
                print("Warning: t out of range")
            plt.plot([t], [qt], 'ro')

        elif pp['plot_type'] == '1d_empty':
            # no plot to create (user might make one in afteritem or
            # afteraxes)
            pass

        else:
            raise ValueError("Unrecognized plot_type: %s" % pp['plot_type'])
            return None

    # call an afterpatch function if present:
    if pp['afterpatch']:
        if isinstance(pp['afterpatch'], str):
            # a string to be executed
            exec(pp['afterpatch'])
        else:
            # assume it's a function
            try:
                # set values that may be needed in afterpatch:
                #current_data.patchno = patch.patch_index # can get from patch
                current_data.add_attribute('plotitem',plotitem)
                current_data.patch = patch
                current_data.var = var
                current_data.xlower = patch.dimensions[0].lower
                current_data.xupper = patch.dimensions[0].upper
                current_data.x = p_centers # cell centers
                current_data.dx = patch.delta[0]
                output = pp['afterpatch'](current_data)
                if output: current_data = output
            except:
                print('*** Error in afterpatch ***')
                raise

    try:
        plotitem._current_pobj = pobj
    except NameError:
        pass # if no plot was done

    return current_data


#==================================================================
def plotitem2(framesoln, plotitem, current_data, stateno):
#==================================================================
    """
    Make a 2d plot for a single plot item for the solution in framesoln.

    The current_data object holds data that should be passed into
    afterpatch or afteraxes if these functions are defined.  The functions
    may add to this object, so this function should return the possibly
    modified current_data for use in other plotitems or in afteraxes or
    afterframe.

    """

    plotdata = plotitem._plotdata

    state = framesoln.states[stateno]
    patch = state.patch
    level = patch.level #2d only

    current_data.patch = patch
    current_data.q = state.q
    current_data.aux = state.aux
    current_data.add_attribute('level',level) #2d only

    t = framesoln.t

    # The following plot parameters should be set and independent of
    # which AMR level a patch is on:

    base_params = ['plot_type','afteritem','mapc2p','MappedGrid']

    level_params = ['plot_var','afterpatch','kwargs',
             'celledges_show','celledges_color','patch_bgcolor',
             'patchedges_show','patchedges_color','add_colorbar',
             'pcolor_cmap','pcolor_cmin','pcolor_cmax',
             'imshow_cmap','imshow_cmin','imshow_cmax',
             'contour_levels','contour_nlevels','contour_min','contour_max',
             'contour_colors','contour_cmap','contour_show',
             'fill_cmap','fill_cmin','fill_cmax','fill_colors',
             'schlieren_cmap','schlieren_cmin', 'schlieren_cmax',
             'quiver_coarsening','quiver_var_x','quiver_var_y','quiver_key_show',
             'quiver_key_scale','quiver_key_label_x','quiver_key_label_y',
             'quiver_key_scale','quiver_key_units','quiver_key_kwargs']

    pp = params_dict(plotitem, base_params, level_params,patch.level)

    if pp['mapc2p'] is None:
        # if this item does not have a mapping, check for a global mapping:
        pp['mapc2p'] = getattr(plotdata, 'mapc2p', None)

    # turn patch background color into a colormap for use with pcolor cmd:
    pp['patch_bgcolormap'] = colormaps.make_colormap({0.: pp['patch_bgcolor'], \
                                             1.: pp['patch_bgcolor']})

    var  = get_var(state,pp['plot_var'],current_data)
    current_data.var = var

    # Grid mapping:

    xc_edges, yc_edges = patch.grid.c_nodes
    xc_centers, yc_centers = patch.grid.c_centers
    if pp['MappedGrid'] is None:
        pp['MappedGrid'] = (pp['mapc2p'] is not None)

    if (pp['MappedGrid'] & (pp['mapc2p'] is None)):
        raise Exception("MappedGrid == True but no mapc2p specified")
    elif pp['MappedGrid']:
        X_center, Y_center = pp['mapc2p'](xc_centers, yc_centers)
        X_edge, Y_edge = pp['mapc2p'](xc_edges, yc_edges)
    else:
        X_center, Y_center = xc_centers, yc_centers
        X_edge, Y_edge = xc_edges, yc_edges

    if ma.isMaskedArray(var):
        # If var is a masked array: plotting should work ok unless all
        # values are masked, in which case pcolor complains and there's
        # no need to try to plot.  Check for this case...
        var_all_masked = (ma.count(var) == 0)
    else:
        # not a masked array, so certainly not all masked:
        var_all_masked = False

    # pcolormesh is much faster but cannot be used with masked coordinate arrays
    if ma.isMaskedArray(X_edge) or ma.isMaskedArray(Y_edge):
        pc_cmd = 'pcolor'
        pc_mth = plt.pcolor
    else:
        pc_cmd = 'pcolormesh'
        pc_mth = plt.pcolormesh

    if pp['plot_type'] == '2d_pcolor':

        pcolor_cmd = "plotitem._current_pobj = plt."+pc_cmd+"(X_edge, Y_edge, var, \
                        cmap=pp['pcolor_cmap']"

        if pp['celledges_show']:
            pcolor_cmd += ", edgecolors=pp['celledges_color']"
        else:
            pcolor_cmd += ", shading='flat'"

        pcolor_cmd += ", **pp['kwargs'])"

        if not var_all_masked:
            exec(pcolor_cmd)


            if (pp['pcolor_cmin'] not in ['auto',None]) and \
                     (pp['pcolor_cmax'] not in ['auto',None]):
                plt.clim(pp['pcolor_cmin'], pp['pcolor_cmax'])
        else:
            #print '*** Not doing pcolor on totally masked array'
            pass

    elif pp['plot_type'] == '2d_imshow':

        if not var_all_masked:
            if pp['imshow_cmin'] in ['auto',None]:
                pp['imshow_cmin'] = np.min(var)
            if pp['imshow_cmax'] in ['auto',None]:
                pp['imshow_cmax'] = np.max(var)
            color_norm = Normalize(pp['imshow_cmin'],pp['imshow_cmax'],clip=True)

            xylimits = (X_edge[0,0],X_edge[-1,-1],Y_edge[0,0],Y_edge[-1,-1])
            pobj = plt.imshow(np.flipud(var.T), extent=xylimits, \
                    cmap=pp['imshow_cmap'], interpolation='nearest', \
                    norm=color_norm)

            if pp['celledges_show']:
                # This draws patch for labels shown.  Levels not shown will
                # not have lower levels blanked out however.  There doesn't
                # seem to be an easy way to do this.
                pobj = plt.plot(X_edge, Y_edge, color=pp['celledges_color'])
                pobj = plt.plot(X_edge.T, Y_edge.T, color=pp['celledges_color'])

        else:
            #print '*** Not doing imshow on totally masked array'
            pass


    elif pp['plot_type'] in ['2d_contour','2d_contourf']:
        levels_set = True
        if pp['contour_levels'] is None:
            levels_set = False
            if pp['contour_nlevels'] is None:
                print('*** Error in plotitem2:')
                print('    contour_levels or contour_nlevels must be set')
                raise
                return
            if (pp['contour_min'] is not None) and \
                    (pp['contour_max'] is not None):

                pp['contour_levels'] = np.linspace(pp['contour_min'], \
                       pp['contour_max'], pp['contour_nlevels'])
                levels_set = True


        if pp['celledges_show']:
            pobj = pc_mth(X_edge, Y_edge, np.zeros(var.shape), \
                    cmap=pp['patch_bgcolormap'], edgecolors=pp['celledges_color'])
        elif pp['patch_bgcolor'] is not 'w':
            pobj = pc_mth(X_edge, Y_edge, np.zeros(var.shape), \
                    cmap=pp['patch_bgcolormap'], edgecolors='None')

        if pp['plot_type'] == '2d_contour':
            # create the contour command:
            contourcmd = "pobj = plt.contour(X_center, Y_center, var, "
            if levels_set:
                contourcmd += "pp['contour_levels']"
            else:
                contourcmd += "pp['contour_nlevels']"

            if pp['contour_cmap']:
                if (pp['kwargs'] is None) or ('cmap' not in pp['kwargs']):
                    contourcmd += ", cmap = pp['contour_cmap']"
            elif pp['contour_colors']:
                if (pp['kwargs'] is None) or ('colors' not in pp['kwargs']):
                    contourcmd += ", colors = pp['contour_colors']"

            contourcmd += ", **pp['kwargs'])"

            if (pp['contour_show'] and not var_all_masked):
                # may suppress plotting at coarse levels
                exec(contourcmd)


        if pp['plot_type'] == '2d_contourf':

            # create the contourf command:
            contourcmd = "pobj = plt.contourf(X_center, Y_center, var, "
            if levels_set:
                contourcmd += "pp['contour_levels']"
            else:
                contourcmd += "pp['contour_nlevels']"

            if pp['fill_cmap']:
                if (pp['kwargs'] is None) or ('cmap' not in pp['kwargs']):
                    contourcmd += ", cmap = pp['fill_cmap']"
            elif pp['fill_colors']:
                if (pp['kwargs'] is None) or ('colors' not in pp['kwargs']):
                    contourcmd += ", colors = pp['fill_colors']"


            if (pp['kwargs'] is None) or ('extend' not in pp['kwargs']):
                contourcmd += ", extend = 'both'"

            contourcmd += ", **pp['kwargs'])"


            if (not var_all_masked):
                # may suppress plotting at coarse levels
                exec(contourcmd)

                if pp['fill_cmap'] and \
                         (pp['fill_cmin'] not in ['auto',None]) and \
                         (pp['fill_cmax'] not in ['auto',None]):
                    plt.clim(pp['fill_cmin'], pp['fill_cmax'])


    elif pp['plot_type'] == '2d_patch':
        # plot only the patches, no data:
        if pp['celledges_show']:
            pobj = pc_mth(X_edge, Y_edge, np.zeros(var.shape), \
                    cmap=pp['patch_bgcolormap'], edgecolors=pp['celledges_color'],\
                    shading='faceted')
        else:
            pobj = pc_mth(X_edge, Y_edge, np.zeros(var.shape), \
                    cmap=pp['patch_bgcolormap'], shading='flat')


    elif pp['plot_type'] == '2d_schlieren':
        # plot 2-norm of gradient of variable var:

        # No idea why this next line is needed...maybe a 64-/32-bit incompatibility issue?
        var = np.array(var)
        (vx,vy) = np.gradient(var)
        vs = np.sqrt(vx**2 + vy**2)

        pcolor_cmd = "pobj = plt.pcolormesh(X_edge, Y_edge, vs, \
                        cmap=pp['schlieren_cmap']"

        if pp['celledges_show']:
            pcolor_cmd += ", edgecolors=pp['celledges_color']"
        else:
            pcolor_cmd += ", edgecolors='None'"

        pcolor_cmd += ", **pp['kwargs'])"

        if not var_all_masked:
            exec(pcolor_cmd)

            if (pp['schlieren_cmin'] not in ['auto',None]) and \
                     (pp['schlieren_cmax'] not in ['auto',None]):
                plt.clim(pp['schlieren_cmin'], pp['schlieren_cmax'])

    elif pp['plot_type'] == '2d_quiver':
        if pp['quiver_coarsening'] > 0:
            var_x = get_var(state,pp['quiver_var_x'],current_data)
            var_y = get_var(state,pp['quiver_var_y'],current_data)
            Q = plt.quiver(X_center[::pp['quiver_coarsening'],::pp['quiver_coarsening']],
                             Y_center[::pp['quiver_coarsening'],::pp['quiver_coarsening']],
                             var_x[::pp['quiver_coarsening'],::pp['quiver_coarsening']],
                             var_y[::pp['quiver_coarsening'],::pp['quiver_coarsening']],
                             **pp['kwargs'])
                             # units=pp['quiver_units'],scale=pp['quiver_scale'])

            # Show key
            if pp['quiver_key_show']:
                if pp['quiver_key_scale'] is None:
                    key_scale = np.max(np.sqrt(var_x**2+var_y**2))*0.5
                else:
                    key_scale = pp['quiver_key_scale']
                label = r"%s %s" % (str(np.ceil(key_scale)),pp['quiver_key_units'])
                plt.quiverkey(Q,pp['quiver_key_label_x'],pp['quiver_key_label_y'],
                                key_scale,label,**pp['quiver_key_kwargs'])

    elif pp['plot_type'] == '2d_empty':
        # no plot to create (user might make one in afteritem or
        # afteraxes)
        pass

    else:
        raise ValueError("Unrecognized plot_type: %s" % pp['plot_type'])
        return None

    # end of various plot types



    # plot patch patch edges if desired:

    if pp['patchedges_show']:
        for i in [0, X_edge.shape[0]-1]:
            X1 = X_edge[i,:]
            Y1 = Y_edge[i,:]
            plt.plot(X1, Y1, pp['patchedges_color'])
        for i in [0, X_edge.shape[1]-1]:
            X1 = X_edge[:,i]
            Y1 = Y_edge[:,i]
            plt.plot(X1, Y1, pp['patchedges_color'])


    if pp['afterpatch']:
        try:
            if isinstance(pp['afterpatch'], str):
                exec(pp['afterpatch'])
            else:
                # assume it's a function
                #current_data.patchno = patch.patch_index # can get from patch
                current_data.add_attribute('plotitem',plotitem)
                current_data.patch = patch
                current_data.var = var
                current_data.xlower = patch.dimensions[0].lower
                current_data.xupper = patch.dimensions[0].upper
                current_data.ylower = patch.dimensions[1].lower
                current_data.yupper = patch.dimensions[1].upper
                current_data.x = X_center # cell centers
                current_data.y = Y_center # cell centers
                current_data.dx = patch.delta[0]
                current_data.dy = patch.delta[1]

                output = pp['afterpatch'](current_data)
                if output: current_data = output
        except:
            print('*** Warning: could not execute afterpatch')
            raise


    try:
        plotitem._current_pobj = pobj
    except NameError:
        pass # if no pobj generated


    return current_data

#--------------------------------------
def get_var(state, plot_var, current_data):
#--------------------------------------
    """
    Return arrays for spatial variable(s) (on mapped patch if necessary)
    and variable to be plotted on a single patch in num_dim space dimensions.
    """

    if isinstance(plot_var, int):
        var = state.q[plot_var,...]
    else:
        try:
            var = plot_var(current_data)
        except:
            print('*** Error applying function plot_var = ',plot_var)
            raise

    return var


#------------------------------------------------------------------------
def printfig(fname='',frameno='', figno='', format='png', plotdir='.', \
             verbose=True, kml_fig=False, kml_dpi=None, kml_figsize=None):
#------------------------------------------------------------------------
    """
    Save the current plot to file fname or standard name from frame/fig.
.
    If fname is nonempty it is used as the filename, with extension
    determined by format if it does not already have a valid extension.

    If fname=='' then save to file frame000NfigJ.ext  where N is the frame
    number frameno passed in, J is the figure number figno passed in,
    and the extension ext is determined by format.
    If figno='' then the figJ part is omitted.
    """

    if fname == '':
        fname = 'frame' + str(frameno).rjust(4,'0')
        if isinstance(figno,int):
            fname = fname + 'fig%s' % figno
    splitfname = os.path.splitext(fname)
    if splitfname[1] not in ('.png','.emf','.eps','.pdf'):
        fname = splitfname[0] + '.%s' % format
    if figno=='':
        figno = 1
    plt.figure(figno)
    if plotdir != '.':
        fname = os.path.join(plotdir,fname)
    if verbose:  print('    Saving plot to file ', fname)
    if kml_fig:
        # from webpage : https://robotics.usc.edu/~ampereir/wordpress/?p=626
        # This was added so that in KML, axes, tick labels, etc do not get printed.
        fig = plt.gcf()
        fig.patch.set_alpha(0)
        a = fig.gca()
        a.set_position([0.,0.,1.0,1.0])
        a.set_frame_on(False)

        # These have to be turned off explicitly so the plot doesn't have any padding.
        a.set_xticks([])
        a.set_yticks([])

        plt.axis('off')
        if kml_figsize is not None:
            fig.set_size_inches(kml_figsize[0],kml_figsize[1])
        plt.savefig(fname, transparent=True, bbox_inches='tight', \
                      pad_inches=0,dpi=kml_dpi)
    else:
        plt.savefig(fname)


#======================================================================
def printframes(plotdata=None, verbose=True):
#======================================================================

    """
    Deprecated: use plotpages.plotclaw_driver instead to get gauges as well.
      - RJL, 1/1/10

    Produce a set of png files for all the figures specified by plotdata.
    Also produce a set of html files for viewing the figures and navigating
    between them.  These will all be in directorey plotdata.plotdir.

    The ClawPlotData object plotdata will be initialized by a call to
    function setplot unless plotdata.setplot=False.

    If plotdata.setplot=True then it is assumed that the current directory
    contains a module setplot.py that defines this function.

    If plotdata.setplot is a string then it is assumed this is the name of
    a module to import that contains the function setplot.

    If plotdata.setplot is a function then this function will be used.
    """
    from clawpack.visclaw import plotpages

    if 'matplotlib' not in sys.modules:
        print('*** Error: matplotlib not found, no plots will be done')
        return plotdata

    if not isinstance(plotdata,ClawPlotData):
        print('*** Error, plotdata must be an object of type ClawPlotData')
        return plotdata

    plotdata._mode = 'printframes'

    plotdata = call_setplot(plotdata.setplot, plotdata)

    try:
        plotdata.rundir = os.path.abspath(plotdata.rundir)
        plotdata.outdir = os.path.abspath(plotdata.outdir)
        plotdata.plotdir = os.path.abspath(plotdata.plotdir)

        framenos = plotdata.print_framenos # frames to plot
        fignos = plotdata.print_fignos     # figures to plot at each frame
        fignames = {}                      # names to use in html files

        rundir = plotdata.rundir       # directory containing *.data files
        outdir = plotdata.outdir       # directory containing fort.* files
        plotdir = plotdata.plotdir     # where to put png and html files
        overwrite = plotdata.overwrite # ok to overwrite?
        msgfile = plotdata.msgfile     # where to write error messages
    except AttributeError:
        print('*** Error in printframes: plotdata missing attribute')
        print('  *** plotdata = ',plotdata)
        return plotdata

    if fignos == 'all':
        fignos = plotdata._fignos
        #for (figname,plotfigure) in plotdata.plotfigure_dict.iteritems():
        #    fignos.append(plotfigure.figno)


    # filter out the fignos that will be empty, i.e.  plotfigure._show=False.
    plotdata = set_show(plotdata)
    fignos_to_show = []
    for figname in plotdata._fignames:
        figno = plotdata.plotfigure_dict[figname].figno
        if (figno in fignos) and plotdata.plotfigure_dict[figname]._show:
            fignos_to_show.append(figno)
    fignos = fignos_to_show


    rootdir = os.getcwd()

    # annoying fix needed when EPD is used for plotting under cygwin:
    cw_path = r'C:\cygwin'
    if rootdir[0:9] == cw_path and outdir[0:9] != cw_path:
        outdir = cw_path + outdir
        plotdata.outdir = outdir
    if rootdir[0:9] == cw_path and rundir[0:9] != cw_path:
        rundir = cw_path + rundir
        plotdata.rundir = rundir
    if rootdir[0:9] == cw_path and plotdir[0:9] != cw_path:
        plotdir = cw_path + plotdir
        plotdata.plotdir = plotdir

    try:
        os.chdir(rundir)
    except OSError:
        print('*** Error: cannot move to run directory ',rundir)
        print('rootdir = ',rootdir)
        return plotdata


    if msgfile != '':
        sys.stdout = open(msgfile, 'w')
        sys.stderr = sys.stdout


    try:
        plotpages.cd_plotdir(plotdata)
    except:
        print("*** Error, aborting plotframes")
        return plotdata


    framefiles = glob.glob(os.path.join(plotdir,'frame*.png')) + \
                    glob.glob(os.path.join(plotdir,'frame*.html'))
    if overwrite:
        # remove any old versions:
        for file in framefiles:
            os.remove(file)
    else:
        if len(framefiles) > 1:
            print("*** Remove frame*.png and frame*.html and try again,")
            print("  or use overwrite=True in call to printframes")
            return plotdata


    # Create each of the figures
    #---------------------------

    try:
        os.chdir(outdir)
    except OSError:
        print('*** Error printframes: cannot move to outdir = ',outdir)
        return plotdata


    fortfile = {}
    frametimes = {}

    for file in glob.glob('fort.q*'):
        frameno = int(file[6:])
        fortfile[frameno] = file

    if len(fortfile) == 0:
        print('*** No fort.q files found in directory ', os.getcwd())
        return plotdata

    # Discard frames that are not from latest run, based on
    # file modification time:
    framenos = only_most_recent(framenos, plotdata.outdir)

    numframes = len(framenos)

    print("Will plot %i frames numbered:" % numframes, framenos)
    print('Will make %i figure(s) for each frame, numbered: ' % len(fignos),\
          fignos)

    fignames = {}
    for figname in plotdata._fignames:
        figno = plotdata.plotfigure_dict[figname].figno
        fignames[figno] = figname



    # Make png files by calling plotframe:
    # ------------------------------------

    for frameno in framenos:
        #plotframe(frameno, plotdata, verbose)
        frametimes[frameno] = plotdata.getframe(frameno, plotdata.outdir).t
        #print 'Frame %i at time t = %s' % (frameno, frametimes[frameno])

    plotdata.timeframes_framenos = framenos
    plotdata.timeframes_frametimes = frametimes
    plotdata.timeframes_fignos = fignos
    plotdata.timeframes_fignames = fignames

    os.chdir(plotdir)

    if plotdata.html:
        plotpages.timeframes2html(plotdata)

    if not plotdata.printfigs:
        print("Using previously printed figure files")
    else:
        print("Now making png files for all figures...")
        for frameno in framenos:
            plotframe(frameno, plotdata, verbose)
            #frametimes[frameno] = plotdata.framesoln_dict[frameno].t
            print('Frame %i at time t = %s' % (frameno, frametimes[frameno]))

    if plotdata.latex:
        plotpages.timeframes2latex(plotdata)


    # Movie:
    #-------

    if plotdata.gif_movie:
        print('Making gif movies.  This may take some time....')
        for figno in fignos:
            try:
                os.system('convert -delay 20 frame*fig%s.png moviefig%s.gif' \
                   % (figno,figno))
                print('    Created moviefig%s.gif' % figno)
            except:
                print('*** Error creating moviefig%s.gif' % figno)

    os.chdir(rootdir)

    # print out pointers to html index page:
    path_to_html_index = os.path.join(os.path.abspath(plotdata.plotdir), \
                               plotdata.html_index_fname)
    plotpages.print_html_pointers(path_to_html_index)

    # reset stdout for future print statements
    sys.stdout = sys.__stdout__

    return plotdata
    # end of printframes


#------------------------------------------------------------------
def var_limits(plotdata,vars,padding=0.1):
#------------------------------------------------------------------
    """
    Determine range of values encountered in data for all frames
    in the most recent computation in order to determine appropriate
    y-axis limits for plots.

    vars is a list of variables to return the limits for.
    Each element of the list can be a number, indicating the
    corresponding element of the q vector, or a function that should
    be applied to q to obtain the value of interest.  In other words,
    any valid plot_var attribute of a ClawPlotItem object.

    If vars=='all', use vars=[0,1,...] over all components of q.
    *** not implemented yet ***

    Returns: varmin, varmax, varlim,
    each is a dictionary with keys consisting by the elements of vars.

    For each var in vars,
      varmin[var] is the minimum of var over all frames,
      varmax[var] is the maximum of var over all frames,
      varlim[var] is of the form [v1, v2] suitable to use as the
            ylimits attritube of an object of class ClawPlotAxes with
                v1 = vmin - padding*(vmax-vmin)
                v2 = vmax + padding*(vmax-vmin)
            to give some space above and below the min and max.

    """

    varlim = {}
    vmin,vmax = var_minmax(plotdata,'all',vars)
    varmin = {}
    varmax = {}
    for var in vars:
        varmin[var] = vmin[var]['all']   # min over all frames
        varmax[var] = vmax[var]['all']   # max over all frames
        v1 = varmin[var] - padding*(varmax[var]-varmin[var])
        v2 = varmax[var] + padding*(varmax[var]-varmin[var])
        varlim[var] = [v1,v2]

    return varmin,varmax,varlim


#------------------------------------------------------------------
def var_minmax(plotdata,framenos,vars):
#------------------------------------------------------------------
    """
    Determine range of values encountered in data for all frames
    in the list framenos.  If framenos='all', search over all frames
    in the most recent computation.

    vars is a list of variables to return the min and max for.
    Each element of the list can be a number, indicating the
    corresponding element of the q vector, or a function that should
    be applied to q to obtain the value of interest.  In other words,
    any valid plot_var attribute of a ClawPlotItem object.

    If vars=='all', use vars=[0,1,...] over all components of q.
    *** not implemented yet ***

    Returns (varmin, varmax) where varmin and varmax are each
    dictionaries with keys given by the variables.

    For each var in vars, varmin[var] and varmax[var] are dictionaries, with
    keys given by frame numbers in framenos.

    Also varmin[var]['all'] and varmax[var]['all'] are the min and max of
    variable var over all frames considered.

    For example if vars = [0,'machnumber'] then
       varmin[0][3] is the minimum of q[0] (the first component of the
           solution vector q) over all patches in frame 3.
       varmin['machnumber']['all'] is the minimum of machnumber
           over all patches in all frames.

    """

    framenos = only_most_recent(framenos, plotdata.outdir)
    if len(framenos) == 0:
        print('*** No frames found in var_minmax!')

    print('Determining min and max of variables: ',vars)
    print('   over frames: ',framenos)

    varmin = {}
    varmax = {}
    if vars=='all':
        print("*** Error in var_minmax: vars == 'all' is not implemented yet")
        return (varmin,varmax)
    for var in vars:
        varmin[var] = {'all': np.inf}
        varmax[var] = {'all': -np.inf}
        for frameno in framenos:
            varmin[var][frameno] = np.inf
            varmax[var][frameno] = -np.inf

    for frameno in framenos:
        solution = plotdata.getframe(frameno, plotdata.outdir)
        num_dim = solution.num_dim

        for state in solution.states:
            patch = state.patch
            for var in vars:
                if isinstance(var,int):
                    if num_dim == 1:
                        qvar = state.q[var,:]
                    elif num_dim == 2:
                        qvar = state.q[var,:,:]
                    elif num_dim == 3:
                        qvar = state.q[var,:,:,:]
                else:
                    t = solution.t
                    #patch.compute_physical_coordinates()
                    if num_dim == 1:
                        X_center = patch.grid.p_centers[0]
                        qvar = var(state.q, X_center, t)
                    elif num_dim == 2:
                        X_center, Y_center = patch.grid.p_centers
                        qvar = var(state.q, X_center, \
                                   Y_center, t)
                    elif num_dim == 3:
                        X_center, Y_center, Z_center = patch.grid.p_centers
                        qvar = var(state.q, X_center, \
                                   Y_center, Z_center, t)
                varmin[var][frameno] = min(varmin[var][frameno], qvar.min())
                varmax[var][frameno] = max(varmax[var][frameno], qvar.max())
                varmin[var]['all'] = min(varmin[var]['all'], \
                                         varmin[var][frameno])
                varmax[var]['all'] = max(varmax[var]['all'], \
                                         varmax[var][frameno])
    return (varmin, varmax)



#------------------------------------------------------------------
def only_most_recent(framenos,outdir='.',verbose=True):
#------------------------------------------------------------------

    """
    Filter the list framenos of frame numbers and return a new
    list that only contains the ones from the most recent run.
    This is determined by comparing modification times of
    fort.q files.

    Returns the filtered list.
    """

    startdir = os.getcwd()
    if outdir != '.':
        try:
            os.chdir(outdir)
        except OSError:
            print("*** Could not chdir to ", outdir)
            return framenos

    fortfile = {}
    for file in glob.glob('fort.q*'):
        frameno = int(file[6:])
        fortfile[frameno] = file

    #DK: In PetClaw, we don't output fort.q* files.  Instead count the
    #claw.pkl* files.
    if len(fortfile) == 0:
        for file in glob.glob('claw.pkl*'):
            frameno = int(file[8:])
            fortfile[frameno] = file

    if len(fortfile) == 0:
        print('*** No fort.q or claw.pkl files found in directory ', os.getcwd())
        framenos = []
        return framenos

    # Figure out which files are from latest run:
    numframes = 0
    mtime = 0
    framekeys = list(fortfile.keys())
    framekeys.sort()
    for frameno in framekeys:
        mtimeprev = mtime
        mtime = os.path.getmtime(fortfile[frameno])
        # sometimes later fort files are closed a few seconds after
        # earlier ones, so include a possible delaytime:
        delaytime = 5  # seconds
        if mtime < mtimeprev-delaytime:
            break
        numframes = numframes + 1

    newframes = framekeys[:numframes]
    if (numframes < len(framekeys)) & verbose:
        print('*** Frames %s and above appear to be from an old run' \
                       % framekeys[numframes])
        print('***    and will be ignored.')
        time.sleep(2)

    #print 'framenos = ',framenos
    if framenos == 'all':
        framenos = newframes
    else:
        # compute intersection of framenos and newframes:
        framenos = list(set(framenos).intersection(set(newframes)))
    framenos.sort()
    os.chdir(startdir)
    return framenos

#------------------------------------------------------------------------
def call_setplot(setplot, plotdata, verbose=True):
#------------------------------------------------------------------
    """
    Try to apply setplot to plotdata and return the result.
    If setplot is False or None, return plotdata unchanged.
    If setplot is True, setplot function is in setplot.py.
    If setplot is a string, setplot function is in module named by string.
    Otherwise assume setplot is a function.
    """
    # This is a bit of a hack to make sure that we still handle the
    # setplot == None case, we may want to deprecate this and require
    # an argument here
    if setplot is None:
        setplot = False

    # Figure out what to do with the setplot passed in
    if not isinstance(setplot,types.FunctionType):
        # We need to parse the names given and import the module and function
        if isinstance(setplot,bool):
            if setplot:
                # Assume that we should import setplot.py from current directory
                setplot_module_dir = os.getcwd()
                setplot_module_name = "setplot"
            else:
                if verbose:
                    print("*** WARNING:  No setplot specified!", file=sys.stderr)
                return plotdata
        elif isinstance(setplot,str):
            # Assume this is the path to the required setplot module
            path = os.path.abspath(os.path.expandvars(os.path.expanduser(setplot)))
            setplot_module_dir = os.path.dirname(path)
            setplot_module_name = os.path.splitext(os.path.basename(setplot))[0]
        else:
            raise Exception("Invalid setplot module specification.")

        if verbose:
            print("Importing %s.setplot from %s." % (setplot_module_name,setplot_module_dir))

        # Attempt to import whatever was handed to us and parsed above
        try:
            sys.path.insert(0,setplot_module_dir)
            setplot_module = __import__(setplot_module_name)
            reload(setplot_module)
            setplot = setplot_module.setplot
            if not isinstance(setplot,types.FunctionType):
                raise ImportError("Failed importing %s.setplot" % setplot_module_name)
        except ImportError as e:
            print("WARNING: Failed to import %s.setplot from %s." \
                                        % (setplot_module_name,setplot_module_dir), file=sys.stderr)
            print("Exception and traceback:", file=sys.stderr)
            print("="*80, file=sys.stderr)
            print("\t%s\n\n" % e, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print("="*80, file=sys.stderr)

            # Not sure if this is the right place to be doing this, maybe
            # this should go higher up than this routine so it can check all
            # of the same attributes?
            print("Would you like to use clawpack.visclaw.setplot_default() instead [Y/n]?")
            use_default = input()
            if (use_default == "") or ("Y" in use_default.capitalize()):
                setplot = setplot_default.setplot
            else:
                sys.exit(1)

            plotdata = setplot(plotdata)
            return plotdata
        except:
            raise
    else:
        # setplot was handed to us as a function, we don't have to do anything!
        pass

    # Execute the setplot function
    try:
        plotdata = setplot(plotdata)
        if plotdata is None:
            # Simple warning if we did not get anything back from plotdata
            print('*** Did you forget the "return plotdata" statement?')
            raise Exception("Plotdata was not set by given setplot function!")
        if verbose:
            print('Executed setplot successfully')
    except:
        print('*** Error in call_setplot: Problem executing function setplot', file=sys.stderr)
        raise

    return plotdata


#------------------------------------------------------------------
def clawpack_header():
#------------------------------------------------------------------
    plt.axes([.3, .8, .98, 1.])
    plt.text(.1,.13,'Clawpack Plots',fontsize=30,color='brown')
    plt.axis('off')

#------------------------------------------------------------------
def errors_2d_vs_1d(solution,reference,var_2d,var_1d,map_2d_to_1d):
#------------------------------------------------------------------
    """
    Input:
      solution: object of class ClawSolution with 2d computed solution

      reference: object of class ClawSolution with 1d reference solution

      var_2d: variable to compare from solution
      if integer, compare q[var_2d,:,:]
      if function, apply to q to obtain the variable

      var_1d: variable to compare from reference
      if integer, compare to q[var_2d,:]
      if function, apply to q to obtain the variable

      map_2d_to_1d: function mapping 2d data to 1d for comparison::

          xs, qs = map_2d_to_1d(xcenter, ycenter, q)
    """

    t = solution.t
    xs = {}
    qs = {}
    qint = {}

    errmax = 0.
    for stateno,state in enumerate(solution.states):
        patch = state.patch

        X_center, Y_center = patch.grid.p_centers
        X_edge, Y_edge = patch.grid.p_centers

        if isinstance(var_2d, int):
            q = state.q[var_2d,:,:]
        else:
            try:
                q = var_2d(state.q, X_center, Y_center, t)
            except:
                print('*** Error applying function plot_var = ',plot_var)
                traceback.print_exc()
                return

        xs1, qs1 = map_2d_to_1d(q, X_center, Y_center, t)

        if hasattr(reference,'states'):
            if len(reference.states) > 1:
                print('*** Warning in errors_2d_vs_1d: reference solution')
                print('*** has more than one patch -- only using patch[0]')
            refstate = reference.states[0]
        else:
            refstate = reference   # assume this contains true solution or
                                  # something set separately rather than
                                  # a framesoln

        xref = patch.grid.p_centers[0]
        if isinstance(var_1d, int):
            qref = refstate.q[var_1d,:].T
        else:
            try:
                qref = var_1d(refstate.q, xref, t)
            except:
                print('*** Error applying function var_1d')
                return

        qint1 = np.interp(xs1, xref, qref)

        xs[stateno] = xs1
        qs[stateno] = qs1
        qint[stateno] = qint1
        errabs = abs(qs1 - qint1)
        errmax = max(errmax, errabs.max())

    return errmax, xs, qs, qint



#------------------------------------------------------------------
def set_show(plotdata):
#------------------------------------------------------------------
    """
    Determine which figures and axes should be shown.
    plotaxes._show should be true only if plotaxes.show and at least one
    item is showing or if the axes have attribute type=='empty', in which
    case something may be plotting in an afteraxes command, for example.

    plotfigure._show should be true only if plotfigure.show and at least
    one axes is showing.
    """

    for figname in plotdata._fignames:
        plotfigure = plotdata.plotfigure_dict[figname]
        plotfigure._show = False
        if plotfigure.show:
            # Loop through all axes to make sure at least some item is showing
            for plotaxes in six.itervalues(plotfigure.plotaxes_dict):
                plotaxes._show = False
                if plotaxes.show:
                    # Loop through plotitems checking each item to see if it
                    # should be shown
                    for plotitem in six.itervalues(plotaxes.plotitem_dict):
                        plotitem._show = plotitem.show
                        if plotitem.show:
                            plotaxes._show = True
                            plotfigure._show = True
                    # Check to see if the axes are supposed to be empty or
                    # something may be in the afteraxes function
                    if not plotaxes._show:
                        if plotaxes.afteraxes is not None or plotaxes.type == 'empty':
                            plotaxes._show = True
                            plotfigure._show = True

    return plotdata
