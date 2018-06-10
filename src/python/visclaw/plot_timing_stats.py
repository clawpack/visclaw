"""
Plot timing info found in timing.csv file.
Requires modified valout function to print this info.

This should be turned into a callable function with default colors, etc.

"""


from __future__ import print_function
from pylab import *
import os

# Location of timing.csv files:
outdir = '_output'

make_pngs = False  # print plots?

def make_png(fname):
    savefig(fname)
    #savefig(fname, bbox_inches='tight')
    print('Created %s' % fname)

# set desired units for simulation time and computer time,
# based on length of run:

simtime_units = 'seconds'
comptime_units = 'seconds'

if simtime_units == 'seconds':
    simtime_factor = 1
elif simtime_units == 'minutes':
    simtime_factor = 60.
elif simtime_units == 'hours':
    simtime_factor = 3600.

if comptime_units == 'seconds':
    comptime_factor = 1
elif comptime_units == 'minutes':
    comptime_factor = 60.
elif comptime_units == 'hours':
    comptime_factor = 3600.


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
    time[j] = timing_stats[j,0]
    total_wall[j] = timing_stats[j,1]
    total_cpu[j] = timing_stats[j,2]
    for level in range(nlevels):
        wtime[j, level] = timing_stats[j,3*level + 3]
        cpu[j, level] = timing_stats[j,3*level + 4]
        cells[j, level] = timing_stats[j,3*level + 5]
    
xlimits = [time.min()/simtime_factor, time.max()/simtime_factor]
ylimits = [0, 1.1*total_cpu.max()/comptime_factor]

# define colors
#R = linspace(0.2,1,nlevels)
#B = linspace(1,0.2,nlevels)
#G = 0.2*ones(nlevels)
#RGB = vstack((R,G,B)).T

# define colors, with colors[0] used for overhead, colors[j] for level j >= 1
colors = ['y'] + 3*['r','g','m','c','b']  # allow lots of levels


figure(22)
clf()
sum_cells_over_levels = zeros(ntimes)
for j in range(nlevels):
    if max(cells[:,j]) == 0:
        break
    #plot(time/3600, cells[:,j], label='Level %s' % (j+1))
    last_sum_cells = sum_cells_over_levels.copy()
    sum_cells_over_levels += cells[:,j]
    plot(time/simtime_factor, sum_cells_over_levels, 'k')
    fill_between(time/simtime_factor, last_sum_cells, sum_cells_over_levels, 
                 color=colors[j+1],
                 label='Level %s' % (j+1))

plot(time/simtime_factor, sum_cells_over_levels, 'k', lw=3, label='Total Cells')
xlim(xlimits)
ylim(0, 1.1*sum_cells_over_levels[-1])
title('Cumulative cells updated on each level')
xlabel('Simulation time (%s)' % simtime_units)
ylabel('Grid cell updates')
legend(loc='upper left')

if make_pngs:
    make_png('CellUpdates.png')


figure(24)
clf()
sum_cpu_over_levels = zeros(ntimes)
for j in range(nlevels):
    if max(cpu[:,j]) == 0:
        break
    #plot(time/3600, cpu[:,j], label='Level %s' % (j+1))
    last_sum_cpu = sum_cpu_over_levels.copy()
    sum_cpu_over_levels += cpu[:,j]
    fill_between(time/simtime_factor, last_sum_cpu/comptime_factor, 
                 sum_cpu_over_levels/comptime_factor, 
                 color=colors[j+1],
                 label='Level %s' % (j+1))
    plot(time/simtime_factor, sum_cpu_over_levels/comptime_factor, 'k')

fill_between(time/simtime_factor, total_cpu/comptime_factor, 
             sum_cpu_over_levels/comptime_factor, 
             color=colors[0],
             label='Overhead')
plot(time/simtime_factor, total_cpu/comptime_factor, 'k', lw=3, label='Total CPU')
xlim(xlimits)
ylim(ylimits)
title('Cumulative CPU time on each level')
xlabel('Simulation time (%s)' % simtime_units)
ylabel('CPU time (%s)' % comptime_units)
legend(loc='upper left')

if make_pngs:
    make_png('CPUtime.png')


figure(25)
clf()
sum_wtime_over_levels = zeros(ntimes)
for j in range(nlevels):
    if max(wtime[:,j]) == 0:
        break
    last_sum_wtime = sum_wtime_over_levels.copy()
    sum_wtime_over_levels += wtime[:,j]
    fill_between(time/simtime_factor, last_sum_wtime/comptime_factor,
                 sum_wtime_over_levels/comptime_factor, 
                 color=colors[j+1],
                 label='Level %s' % (j+1))
    plot(time/simtime_factor, sum_wtime_over_levels/comptime_factor, 'k')

fill_between(time/simtime_factor, total_wall/comptime_factor, 
             sum_wtime_over_levels/comptime_factor, 
             color=colors[0],
             label='Overhead')
plot(time/simtime_factor, total_wall/comptime_factor, 'k', lw=3, label='Total Wall')
title('Cumulative wall time on each level')
xlabel('Simulation time (%s)' % simtime_units)
ylabel('CPU time (%s)' % comptime_units)
legend(loc='upper left')
xlim(xlimits)
ylim(ylimits)

if make_pngs:
    make_png('WallTime.png')


# d cells / dt:

figure(32)
clf()
dc_max = 0
dca = cells[1:,:] - cells[:-1,:]
for n in range(1,ntimes):
    dt = (time[n] - time[n-1])
    if dt == 0:
        break
    dcn = 0
    for j in range(nlevels):
        if dca[n-1,j] == 0:
            break
        tt = array([time[n-1],time[n]])/simtime_factor
        #last_dc = last_dc + dc
        dc = (cells[n,j] - cells[n-1,j]) / dt
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

                         
#plot(time/simtime_factor, sum_cells_over_levels, 'k', lw=3, label='Total Cells')
xlim(xlimits)
ylim(0, 1.2*dc_max)
title('Average Cells updated / sim time')
xlabel('Simulation time (%s)' % simtime_units)
ylabel('cell updates / sim time')
legend(loc='upper left')

if make_pngs:
    make_png('dCellUpdates.png')


# d cpu_time / dt:

figure(34)
clf()
dc_max = 0
dca = cpu[1:,:] - cpu[:-1,:]
for n in range(1,ntimes):
    dt = (time[n] - time[n-1])
    if dt == 0:
        break
    dcn = 0
    for j in range(nlevels):
        if dca[n-1,j] == 0:
            break
        tt = array([time[n-1],time[n]])/simtime_factor
        #last_dc = last_dc + dc
        dc = (cpu[n,j] - cpu[n-1,j]) / dt
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
     
    #plot(time/simtime_factor, total_cpu/comptime_factor, 'k', lw=3, label='Total CPU')

                         
#plot(time/simtime_factor, sum_cells_over_levels, 'k', lw=3, label='Total Cells')
xlim(xlimits)
ylim(0, 1.2*dc_max)
title('CPU time / simulation time')
xlabel('Simulation time (%s)' % simtime_units)
ylabel('CPU time / sim time')
legend(loc='upper left')

if make_pngs:
    make_png('dCellUpdates.png')

