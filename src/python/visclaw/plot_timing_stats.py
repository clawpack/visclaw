"""
Plot timing info found in timing.csv file.
Requires modified valout function from Clawpack 5.5.0 to print this info.

To use, first run the Clawpack or GeoClaw code, and insure that the 
file `timing.csv` was generated in the output directory.
This file has one line for each output time giving the cumulative CPU and
Wall time, both in total and broken down by levels.

If you execute this at the command line you can specify the output
directory, e.g.

    python plot_timing_stat.py _output

and plots will be made with some default choices of units and png files
placed in the output directory.

For more control, import this module and call the function `make_plots`.
This allows setting units and also redirecting the png files to the _plots
directory and creating an html file to easily view them.
"""

from __future__ import print_function
from pylab import *
import os

# text for html file showing all plots:

html_text1 = """
    <html>
    <h1>Timing information</h1>
    <p>
    <pre>
    """
html_text2 = """
    </pre>
    <p>
    <img width=30% src="timing_CumWallTime.png">
    <img width=30% src="timing_CumCPUTime.png">
    <img width=30% src="timing_CumCellUpdates.png">
    
    <p>
    <img width=30% src="timing_ByFrameWallTime.png">
    <img width=30% src="timing_ByFrameCPUTime.png">
    <img width=30% src="timing_ByFrameCellUpdates.png">
    
    <p>
    <img width=50% src="timing_ByFrameCellUpdatesPerCPU.png">
    
    </html>
"""

#=======================================================================

def make_plots(outdir='_output', make_pngs=True, make_html=None, 
               plotdir=None, units={}):

    """
    `outdir` is the directory containing `timing.csv`.
    Set `make_pngs` to `True` to create png files, 
    By default, an html index will be made if `make_pngs == True` but
    you can turn this off by setting `make_html` to `False`.
    If `plotdir == None` then png file will be put in `outdir`.
    
    The `units` directory can be used to choose units for the plots:

    units['comptime'] can be 'seconds', 'minutes', 'hours', or 'days'.
        Since computer time (wall and CPU) is in seconds in the csv file,
        changing these units will rescale by a factor of 60, 3600, or
        24*3600 in the plots (for 'minutes', 'hours', or 'days' respectively).
        The default is 'seconds' if you do not set this element of the 
        dictionary.

    units['simtime'] is the units used in the simulation.  
        The default is 'nondimensional', which is appropriate if the PDE is 
        non-dimensionalized or there are no specific units.

    You can set units['simtime'] to an arbitrary string to be used in labels
        on the axes, if this is the units of the simulation.  If you want to 
        scale `t` by a multiplicative factor then you can also specify
        units['simtime_factor'].  For example, if `t` in the PDE is
        in nanoseconds but you ran out so long that you want to the units 
        in the plots to be milliseconds, you could set:
            units['simtime'] = 'milliseconds'
            units['simtime_factor'] = 1e6
        Then `t` will be divided by `1e6` before plotting.

    Special case: Since many simulations use units in which `t` is in seconds 
        (in particular, GeoClaw simulations): 

        if units['simtime'] one of:
             'seconds', 'minutes', 'hours', or 'days',
        and if units['simtime_factor'] is not specified, 
        then these factors default to:
             1, 60, 3600, or 24*3600 respectively.
        So if `t` in your PDE is in hours and you want to plot as such, 
        you will have to over-ride this default with
            units['simtime'] = 'hours'
            units['simtime_factor'] = 1.

    
    units['cell'] is the units used in plotting the number of grid cells
        updated between output frames, and the cumulative plot.

        if units['cell'] == 'raw count' then number of cells is plotted
        if units['cell'] is one of 'thousands', 'millions', 'billions', or
            'trillions', then the number of cell updates is divided by the
            appropriate factor (1e3, 1e6, 1e9, 1e12 resp.) before plotting.
        if you want to use some other units, you can also explicitly set
            units['cell_factor'] to the appropriate value.
        The default is units['cell'] == 'millions', appropriate for many
            smallish problems.
        

    """

    if make_pngs:
        if plotdir is None:
            plotdir = outdir
        os.system('mkdir -p %s' % plotdir)

    if make_html is None:
        make_html = make_pngs

    if make_html and (not make_pngs):
        print('Warning: will make html index but no png files')

    def make_png(fname):
        if make_pngs:
            tight_layout() # since labels sometimes disappear
            fname = os.path.join(plotdir, fname)
            savefig(fname)
            #savefig(fname, bbox_inches='tight')
            print('Created %s' % fname)

    # set desired units for simulation time and computer time,
    # based on length of run:

    # set units and scaling factors for Simulation time t (simtime), 
    # CPU/Wall time (comptime), and for number of cells updated.
    # units is used for text in plots, factor is used for scaling values read in
    # if None, then no units appear in plots, and/or no scaling is done.

    # computer time is recorded in seconds so this is the natural units:
    #comptime_units = 'seconds'
    #comptime_units = 'minutes'
    
    comptime_units = units.get('comptime', 'seconds')
    if comptime_units == 'seconds':
        comptime_factor = 1
    elif comptime_units == 'minutes':
        comptime_factor = 60.
    elif comptime_units == 'hours':
        comptime_factor = 3600.
    elif comptime_units == 'days':
        comptime_factor = 24*3600.
    else:
        comptime_units = 'dimensionless'
        comptime_factor = 1

    simtime_units = units.get('simtime', 'dimensionless')
    simtime_factor = units.get('simtime_factor', 'default')

    # note: if units['simtime_factor'] is not specified it is set to 'default',
    # which causes special case behavior below.

    if simtime_units == 'dimensionless':
        simtime_factor = 1
    if simtime_units == 'seconds':
        if simtime_factor == 'default':
            simtime_factor = 1
    elif simtime_units == 'minutes':
        if simtime_factor == 'default':
            simtime_factor = 60.
    elif simtime_units == 'hours':
        if simtime_factor == 'default':
            simtime_factor = 3600.
    elif simtime_units == 'days':
        if simtime_factor == 'default':
            simtime_factor = 24*3600.
    elif simtime_factor == 'default':
        print("*** warning, no default simtime_factor for units['simtime'] = %s" \
              % simtime_units)
        print("Using simtime_factor = 1")
        simtime_factor = 1

    # Units for number of cell updates:
    cell_units = units.get('cell', 'millions')
    cell_factor = units.get('cell_factor', 'default')

    if cell_units == 'raw count':
        cell_factor = 1
    if cell_units == 'thousands':
        cell_factor = 1e3
    if cell_units == 'millions':
        cell_factor = 1e6
    elif cell_units == 'billions':
        cell_factor = 1e9
    elif cell_units == 'trillions':
        cell_factor = 1e12
    else:
        if cell_factor is 'default':
            print("*** Warning, units['cell'] = %s has no default cell_factor, using 1" \
             % cell_units)
            cell_factor = 1


    # define colors, with colors[0] used for overhead, colors[j] for level j >= 1
    colors = ['gray'] + 3*['r','c','m','limegreen','b','orange','g','yellow'] 


    # Read in timing states from output directory:
    timing_stats_file = os.path.join(outdir, 'timing.csv')
    timing_stats = loadtxt(timing_stats_file, skiprows=1, delimiter=',',
                           ndmin=2)
    ntimes = timing_stats.shape[0]
    nlevels = int(timing_stats.shape[1] / 3) - 1

    time = zeros(ntimes)
    total_cpu = zeros(ntimes)
    total_wall = zeros(ntimes)
    wtime = zeros((ntimes, nlevels))
    cpu = zeros((ntimes, nlevels))
    cells = zeros((ntimes, nlevels))

    for j in range(ntimes):
        time[j] = timing_stats[j,0] / simtime_factor
        total_wall[j] = timing_stats[j,1] / comptime_factor
        total_cpu[j] = timing_stats[j,2] / comptime_factor
        for level in range(nlevels):
            wtime[j, level] = timing_stats[j,3*level + 3] / comptime_factor
            cpu[j, level] = timing_stats[j,3*level + 4] / comptime_factor
            cells[j, level] = timing_stats[j,3*level + 5] / cell_factor
        
    xlimits = [time.min(), time.max()]
    ylimits_comptime = [0, 1.1*total_cpu.max()]
    ylimits_cells = [0, 1.1*sum(cells[-1,:])]


    figure(21)
    clf()
    sum_cells_over_levels = zeros(ntimes)
    for j in range(nlevels):
        if max(cells[:,j]) == 0:
            break
        #plot(time/3600, cells[:,j], label='Level %s' % (j+1))
        last_sum_cells = sum_cells_over_levels.copy()
        sum_cells_over_levels += cells[:,j]
        plot(time, sum_cells_over_levels, 'k')
        fill_between(time, last_sum_cells, sum_cells_over_levels, 
                     color=colors[j+1], edgecolor=None,
                     label='Level %s' % (j+1))

    plot(time, sum_cells_over_levels, 'k', lw=1, label='Total Cells')
    xlim(xlimits)
    #ylim(0, 1.1*sum_cells_over_levels[-1])
    ylim(ylimits_cells)
    title('Cumulative cells updated on each level')
    xlabel('Simulation time t (%s)' % simtime_units)
    if cell_units is None:
        ylabel('Grid cells updated')
    else:
        ylabel('Grid cells updated (%s)' % cell_units)

    legend(loc='upper left')

    make_png('timing_CumCellUpdates.png')


    figure(22)
    clf()
    sum_cpu_over_levels = zeros(ntimes)
    for j in range(nlevels):
        if max(cpu[:,j]) == 0:
            break
        #plot(time/3600, cpu[:,j], label='Level %s' % (j+1))
        last_sum_cpu = sum_cpu_over_levels.copy()
        sum_cpu_over_levels += cpu[:,j]
        fill_between(time, last_sum_cpu, sum_cpu_over_levels, color=colors[j+1],
                      edgecolor=None,label='Level %s' % (j+1))
        plot(time, sum_cpu_over_levels, 'k')

    fill_between(time, total_cpu,sum_cpu_over_levels,color=colors[0],
                  edgecolor=None,label='Overhead')
    plot(time, total_cpu, 'k', lw=1, label='Total CPU')
    xlim(xlimits)
    ylim(ylimits_comptime)
    title('Cumulative CPU time on each level')
    xlabel('Simulation time t (%s)' % simtime_units)
    ylabel('CPU time (%s)' % comptime_units)
    legend(loc='upper left')

    make_png('timing_CumCPUTime.png')


    figure(23)
    clf()
    sum_wtime_over_levels = zeros(ntimes)
    for j in range(nlevels):
        if max(wtime[:,j]) == 0:
            break
        last_sum_wtime = sum_wtime_over_levels.copy()
        sum_wtime_over_levels += wtime[:,j]
        fill_between(time, last_sum_wtime,
                     sum_wtime_over_levels, 
                     color=colors[j+1], edgecolor=None,
                     label='Level %s' % (j+1))
        plot(time, sum_wtime_over_levels, 'k')

    fill_between(time, total_wall, sum_wtime_over_levels, color=colors[0],
                  edgecolor=None,label='Overhead')
    plot(time, total_wall, 'k', lw=1, label='Total Wall')
    title('Cumulative wall time on each level')
    xlabel('Simulation time t (%s)' % simtime_units)
    ylabel('Wall time (%s)' % comptime_units)
    legend(loc='upper left')
    xlim(xlimits)
    ylim(ylimits_comptime)

    make_png('timing_CumWallTime.png')


    # cells between frames:

    figure(31)
    clf()
    dc_max = 0
    for n in range(1,ntimes):
        dt = (time[n] - time[n-1])
        tt = array([time[n-1],time[n]])
        if dt == 0:
            continue
        dcn = 0
        for j in range(nlevels):
            #dc = (cells[n,j] - cells[n-1,j]) / dt
            dc = (cells[n,j] - cells[n-1,j])
            if dc >= 0:
                plot(tt, [dcn+dc, dcn+dc], 'k')
                if n == 1:
                    fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                                 color=colors[j+1], edgecolor=None,
                                 label='Level %s' % (j+1))
                else:
                    fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                                  edgecolor=None,color=colors[j+1])
            dcn = dcn + dc

        plot([time[n-1],time[n-1]], [0,dcn], 'k')
        plot([time[n],time[n]], [0,dcn], 'k')
        dc_max = max(dc_max, dcn)

                             
    xlim(xlimits)
    ylim(0, 1.2*dc_max)
    title('Cells updated between output frames')
    xlabel('Simulation time t (%s)' % simtime_units)
    if cell_units is None:
        ylabel('Grid cells updated')
    else:
        ylabel('Grid cells updated (%s)' % cell_units)

    legend(loc='upper left')

    make_png('timing_ByFrameCellUpdates.png')


    # cpu_time between frames:

    figure(32)
    clf()
    dc_max = 0
    for n in range(1,ntimes):
        dt = (time[n] - time[n-1])
        tt = array([time[n-1],time[n]])
        if dt == 0:
            continue
        dcn = 0
        for j in range(nlevels):
            dc = (cpu[n,j] - cpu[n-1,j]) #/ dt
            if dc >= 0:
                plot(tt, [dcn+dc, dcn+dc], 'k')
                if n == 1:
                    fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                                 color=colors[j+1], edgecolor=None,
                                 label='Level %s' % (j+1))
                else:
                    fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                                  edgecolor=None,color=colors[j+1])
            dcn = dcn + dc

        if n == 1:
            kwargs_label = {'label': 'Overhead'}
        else:
            kwargs_label = {}
        dtot = (total_cpu[n]-total_cpu[n-1]) #/ dt 
        plot(tt, [dtot,dtot], 'k')
        fill_between(tt, [dcn,dcn], [dtot,dtot], 
                     color=colors[0],
                     alpha=1, edgecolors='k', **kwargs_label)

        plot([time[n-1],time[n-1]], [0,dtot], 'k')
        plot([time[n],time[n]], [0,dtot], 'k')
        
        dc_max = max(dc_max, dtot)
         
        #plot(time, total_cpu, 'k', lw=1, label='Total CPU')

                             
    #plot(time, sum_cells_over_levels, 'k', lw=1, label='Total Cells')
    xlim(xlimits)
    ylimits_avecomptime = [0, 1.2*dc_max]
    ylim(ylimits_avecomptime)

    title('CPU time between output frames')
    xlabel('Simulation time t (%s)' % simtime_units)
    ylabel('CPU time (%s) / frame' % comptime_units)
    legend(loc='upper left')

    make_png('timing_ByFrameCPUTime.png')



    # wall time between frames:

    figure(33)
    clf()
    dc_max = 0
    for n in range(1,ntimes):
        dt = (time[n] - time[n-1])
        tt = array([time[n-1],time[n]])
        if dt == 0:
            continue
        dcn = 0
        for j in range(nlevels):
            #last_dc = last_dc + dc
            dc = (wtime[n,j] - wtime[n-1,j]) #/ dt
            if dc >= 0:
                plot(tt, [dcn+dc, dcn+dc], 'k')
                if n == 1:
                    fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                                 color=colors[j+1], edgecolor=None,
                                 label='Level %s' % (j+1))
                else:
                    fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc], edgecolor=None,
                                 color=colors[j+1])
            dcn = dcn + dc

        if n == 1:
            kwargs_label = {'label': 'Overhead'}
        else:
            kwargs_label = {}
        dtot = (total_wall[n]-total_wall[n-1]) #/ dt 
        plot(tt, [dtot,dtot], 'k')
        fill_between(tt, [dcn,dcn], [dtot,dtot], 
                     color=colors[0],
                     alpha=1, edgecolors='k', **kwargs_label)

        plot([time[n-1],time[n-1]], [0,dtot], 'k')
        plot([time[n],time[n]], [0,dtot], 'k')
        
        dc_max = max(dc_max, dtot)

                             
    xlim(xlimits)
    #ylim(0, 1.2*dc_max)
    ylim(ylimits_avecomptime)
    title('Wall time between output frames')
    xlabel('Simulation time t (%s)' % simtime_units)
    ylabel('Wall time (%s)/ output frame' % comptime_units)
    legend(loc='upper left')

    make_png('timing_ByFrameWallTime.png')




    # average cells updates per CPU second between frames:

    figure(41)
    clf()
    dc_max = 0
    for n in range(1,ntimes):
        dt = (time[n] - time[n-1])
        tt = array([time[n-1],time[n]])
        if dt == 0:
            continue



        total_cpu_frame = sum(cpu[n,0:nlevels])
        total_cells_frame = sum(cells[n,0:nlevels])
        cells_cpu = total_cells_frame / total_cpu_frame
        fill_between(tt, [cells_cpu, cells_cpu], color='c')
        plot(tt, [cells_cpu, cells_cpu], 'k')
        plot([time[n-1],time[n-1]], [0,cells_cpu], 'k')
        plot([time[n],time[n]], [0,cells_cpu], 'k')
        
        #dc_max = max(dc_max, dcn)
        dc_max = max(dc_max, cells_cpu)

                             
    xlim(xlimits)
    ylim(0, 1.2*dc_max)
    title('Average cells updated per CPU time, between output frames')
    xlabel('Simulation time t (%s)' % simtime_units)
    if cell_units in [None,'raw count']:
        ylabel('Grid cells updated / CPU (%s)' % comptime_units)
    else:
        ylabel('Grid cells updated (%s) / CPU (%s)' % (cell_units,comptime_units))

    #legend(loc='upper left')

    make_png('timing_ByFrameCellUpdatesPerCPU.png')

    if make_pngs:

        try:
            import datetime
            timing_text = open(outdir+'/timing.txt','r').read()
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            timing_text = "<h4>Datetime: %s   From: %s\n</h4>" \
                          % (date,os.path.abspath(outdir)) \
                          + timing_text
        except:
            timing_text = 'Error -- could not read timing.txt from %s' \
                           % outdir
        html_text = html_text1 + timing_text + html_text2

    if make_html:
        html_file = os.path.join(plotdir, 'timing.html')
        with open(html_file,'w') as h:
            h.write(html_text)
        print('Created %s' % html_file)


if __name__=='__main__':
    import sys
    print(sys.argv)
    if len(sys.argv) > 1:
        outdir = sys.argv[1]
    else:
        outdir = '_output'
    make_plots(outdir)
