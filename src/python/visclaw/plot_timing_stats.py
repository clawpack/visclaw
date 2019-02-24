"""
Plot timing info found in timing.csv file.
Requires modified valout function from Clawpack 5.5.0 to print this info.

To use:

    - Run the Clawpack or GeoClaw code, and insure that the file `timing.csv`
      was generated in the output directory `_output` (hard-wired below).

    - Run this script in an IPython shell, Jupyter notebook, or via::

         $ python $CLAW/visclaw/src/python/visclaw/plot_timing_stats.py

    - If run from the command line, view the plots created as png files.

This code should eventually be turned into a more general utility function with
more options. For now, copy this file and modify it for your needs if necessary.

Note: if you are doing a restart, the original `timing.csv` file will be
overwritten.  So if you want to compute timings for the original plus the
restarted runs together, you will have to save the original and 
then combine the times appropriately. This script does not do that.
"""

from __future__ import print_function
from pylab import *
import os

# Location of timing.csv files:
outdir = '_output'

make_pngs = True  # print plots?

def make_png(fname):
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
comptime_units = 'seconds'
if comptime_units == 'seconds':
    comptime_factor = 1
elif comptime_units == 'minutes':
    comptime_factor = 60.
elif comptime_units == 'hours':
    comptime_factor = 3600.
else:
    comptime_factor = 1

# for applications where t in the PDE is dimensionless, use this:
simtime_units = 'dimensionless'
simtime_factor = 1

# for GeoClaw or other applications where the simulation time is in
# seconds, set simtime_units to 'seconds', 'minutes' or 'hours' depending
# on time scale of simulation and use this:
#simtime_units = 'seconds'
if simtime_units == 'seconds':
    simtime_factor = 1
elif simtime_units == 'minutes':
    simtime_factor = 60.
elif simtime_units == 'hours':
    simtime_factor = 3600.

# if the time units in the application are different, set simtime_units
# and simtime_factor appropriately.
    
# Some useful units for cell updates:
#cell_units = None # for raw cell count
cell_units = 'millions'

if cell_units == 'millions':
    cell_factor = 1e6
elif cell_units == 'billions':
    cell_factor = 1e9
elif cell_units == 'trillions':
    cell_factor = 1e12
else:
    cell_factor = 1


# define colors, with colors[0] used for overhead, colors[j] for level j >= 1
colors = ['y'] + 3*['r','g','m','c','b']  # allow <= 15 levels


# Read in timing states from output directory:
timing_stats_file = os.path.join(outdir, 'timing.csv')
timing_stats = loadtxt(timing_stats_file, skiprows=1, delimiter=',')
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
                 color=colors[j+1],
                 label='Level %s' % (j+1))

plot(time, sum_cells_over_levels, 'k', lw=3, label='Total Cells')
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

if make_pngs:
    make_png('CumCellUpdates.png')


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
                 label='Level %s' % (j+1))
    plot(time, sum_cpu_over_levels, 'k')

fill_between(time, total_cpu,sum_cpu_over_levels,color=colors[0],
             label='Overhead')
plot(time, total_cpu, 'k', lw=3, label='Total CPU')
xlim(xlimits)
ylim(ylimits_comptime)
title('Cumulative CPU time on each level')
xlabel('Simulation time t (%s)' % simtime_units)
ylabel('CPU time (%s)' % comptime_units)
legend(loc='upper left')

if make_pngs:
    make_png('CumCPUtime.png')


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
color=colors[j+1],
                 label='Level %s' % (j+1))
    plot(time, sum_wtime_over_levels, 'k')

fill_between(time, total_wall, sum_wtime_over_levels, color=colors[0],
             label='Overhead')
plot(time, total_wall, 'k', lw=3, label='Total Wall')
title('Cumulative wall time on each level')
xlabel('Simulation time t (%s)' % simtime_units)
ylabel('CPU time (%s)' % comptime_units)
legend(loc='upper left')
xlim(xlimits)
ylim(ylimits_comptime)

if make_pngs:
    make_png('CumWallTime.png')


# d cells / dt:

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
        dc = (cells[n,j] - cells[n-1,j]) / dt
        if dc >= 0:
            plot(tt, [dcn+dc, dcn+dc], 'k')
            if n == 1:
                fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                             color=colors[j+1],
                             label='Level %s' % (j+1))
            else:
                fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                             color=colors[j+1])
        dcn = dcn + dc

    plot([time[n-1],time[n-1]], [0,dcn], 'k')
    plot([time[n],time[n]], [0,dcn], 'k')
    dc_max = max(dc_max, dcn)

                         
xlim(xlimits)
ylim(0, 1.2*dc_max)
title('Average Cells updated / simulation time')
xlabel('Simulation time t (%s)' % simtime_units)
ylabel('cell updates / sim time')
if cell_units is None:
    ylabel('Grid cells updated / sim time')
else:
    ylabel('Grid cells updated (%s) / sim time' % cell_units)

legend(loc='upper left')

if make_pngs:
    make_png('AveCellUpdates.png')


# average cpu_time / dt:

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
        dc = (cpu[n,j] - cpu[n-1,j]) / dt
        if dc >= 0:
            plot(tt, [dcn+dc, dcn+dc], 'k')
            if n == 1:
                fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                             color=colors[j+1],
                             label='Level %s' % (j+1))
            else:
                fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                             color=colors[j+1])
        dcn = dcn + dc

    if n == 1:
        kwargs_label = {'label': 'Overhead'}
    else:
        kwargs_label = {}
    dtot = (total_cpu[n]-total_cpu[n-1]) / dt 
    plot(tt, [dtot,dtot], 'k')
    fill_between(tt, [dcn,dcn], [dtot,dtot], 
                 color=colors[0], alpha=1, edgecolors='k', **kwargs_label)

    plot([time[n-1],time[n-1]], [0,dtot], 'k')
    plot([time[n],time[n]], [0,dtot], 'k')
    
    dc_max = max(dc_max, dtot)
     
    #plot(time, total_cpu, 'k', lw=3, label='Total CPU')

                         
#plot(time, sum_cells_over_levels, 'k', lw=3, label='Total Cells')
xlim(xlimits)
ylimits_avecomptime = [0, 1.2*dc_max]
ylim(ylimits_avecomptime)

title('Average CPU time / simulation time')
xlabel('Simulation time t (%s)' % simtime_units)
ylabel('CPU time / sim time')
legend(loc='upper left')

if make_pngs:
    make_png('AveCPUTime.png')



# average wall time / dt:

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
        dc = (wtime[n,j] - wtime[n-1,j]) / dt
        if dc >= 0:
            plot(tt, [dcn+dc, dcn+dc], 'k')
            if n == 1:
                fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                             color=colors[j+1],
                             label='Level %s' % (j+1))
            else:
                fill_between(tt, [dcn,dcn], [dcn+dc,dcn+dc],
                             color=colors[j+1])
        dcn = dcn + dc

    if n == 1:
        kwargs_label = {'label': 'Overhead'}
    else:
        kwargs_label = {}
    dtot = (total_wall[n]-total_wall[n-1]) / dt 
    plot(tt, [dtot,dtot], 'k')
    fill_between(tt, [dcn,dcn], [dtot,dtot], 
                 color=colors[0], alpha=1, edgecolors='k', **kwargs_label)

    plot([time[n-1],time[n-1]], [0,dtot], 'k')
    plot([time[n],time[n]], [0,dtot], 'k')
    
    dc_max = max(dc_max, dtot)

                         
xlim(xlimits)
#ylim(0, 1.2*dc_max)
ylim(ylimits_avecomptime)
title('Average Wall time / simulation time')
xlabel('Simulation time t (%s)' % simtime_units)
ylabel('wtime time / sim time')
legend(loc='upper left')

if make_pngs:
    make_png('AveWallTime.png')
