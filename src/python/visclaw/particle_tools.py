"""
Tools for Lagrangian gauges (particle tracking).
First attempt, could be improved.
"""


from __future__ import absolute_import
from __future__ import print_function

import numpy
from clawpack.visclaw import gaugetools
from clawpack.pyclaw import gauges
from clawpack.amrclaw.data import GaugeData

def read_gauges(gaugenos='all', outdir=None):
    
    if (type(gaugenos) is int) or (type(gaugenos) is str):
        gaugenos = [gaugenos]  # single gaugeno passed in
        
    gd = GaugeData(outdir)
    gd.read()
    
    gauge_solutions = {}
    
    for gaugeno in gd.gauge_numbers:
        if (gaugeno in gaugenos) or (gaugenos[0] == 'all'):
            g = gauges.GaugeSolution(gaugeno, outdir)
            gauge_solutions[gaugeno] = g

    if 0:
        # for debugging:
        gaugenos_lagrangian = [k for k in gauge_solutions.keys() \
                    if gauge_solutions[k].gtype=='lagrangian']
        gaugenos_stationary = [k for k in gauge_solutions.keys() \
                    if gauge_solutions[k].gtype=='stationary']
        print('+++ Loaded %i stationary and %i Lagrangian gauges' \
            % (len(gaugenos_stationary),len(gaugenos_lagrangian)))
            
    return gauge_solutions
        
def check_gaugenos_input(gauge_solutions, gaugenos):
    """
    If `gaugenos` is 'all', replace by list of lagrangian gauges
    If `gaugenos` is a single integer, turn into list
    Then check if each gaugeno is lagrangian, and add to output
        list only if lagrangian
    Return modified list of lagrangian gaugenos
    """
    gaugenos_lagrangian = []
    gaugenos_stationary = []
    
    if gaugenos=='all':
        gaugenos = gauge_solutions.keys()    
    elif type(gaugenos) is int:
        gaugenos = [gaugenos]  # single gaugeno passed in
        
    for gaugeno in gaugenos:
        if gauge_solutions[gaugeno].gtype == 'lagrangian':
            gaugenos_lagrangian.append(gaugeno)
        else:
            gaugenos_stationary.append(gaugeno)
            
    if len(gaugenos_lagrangian) == 0:
        print('*** Warning, no lagrangian gauges in gaugenos')
        
    return gaugenos_lagrangian
               
                           
def interp_particles(gauge_solutions, t, gaugenos='all', extend='neither'):
    """
    Interpolate (x,y) to the given time t for each specified gauge.
    Returns a dictionary of results indexed by gauge number.
    """
        
    gaugenos = check_gaugenos_input(gauge_solutions, gaugenos)
    
    particle_positions = {}
    for gaugeno in gaugenos:
        g = gauge_solutions[gaugeno]
        if g.particle_path is None: 
            particle_positions[gaugeno] = (numpy.nan, numpy.nan)
            continue # no gauge data yet, go on to next gauge
        tg = g.particle_path[:,0]
        xg = g.particle_path[:,1]
        yg = g.particle_path[:,2]
        if t <= tg[0]:
            if extend in ['neither', 'max']:
                x = numpy.nan
                y = numpy.nan
            elif extend in ['min', 'both']:
                x = xg[0]
                y = yg[0]
            else:
                raise ValueError('Unrecognized extend')
        elif t > tg[-1]:
            if extend in ['neither', 'min']:
                x = numpy.nan
                y = numpy.nan
            elif extend in ['max', 'both']:
                x = xg[-1]
                y = yg[-1]
            else:
                raise ValueError('Unrecognized extend')
        else:
            i = numpy.where(tg<=t)[0][-1]
            if i > len(tg)-2: 
                i = len(tg)-2
            if i<len(tg)-1:
                alf = (t-tg[i])/(tg[i+1]-tg[i])
                x = xg[i] + alf*(xg[i+1]-xg[i])
                y = yg[i] + alf*(yg[i+1]-yg[i])
            else:
                x = xg[-1]
                y = yg[-1]
        particle_positions[gaugeno] = (x,y)
    return particle_positions


def plot_particles(gauge_solutions, t, gaugenos='all', kwargs_plot=None,
                   extend='neither'):
    """
    Plot particle locations as points for some set of gauges.
    """
    from matplotlib import pyplot as plt

    gaugenos = check_gaugenos_input(gauge_solutions, gaugenos)
        
    if kwargs_plot is None:
        kwargs_plot = {'marker':'o','markersize':2,'color':'k'}
        
    pp = interp_particles(gauge_solutions, t, gaugenos, extend)
    for k in pp.keys():
        x,y = pp[k]
        plt.plot([x],[y],**kwargs_plot)
        

def plot_paths(gauge_solutions, t1=None, t2=None, gaugenos='all', 
               kwargs_plot=None, extend='neither'):
    """
    Plot the particle path for a set of gauges over some time interval.
    """
    from matplotlib import pyplot as plt
    
    
    if kwargs_plot is None:
        kwargs_plot = {'linestyle':'-','linewidth':0.7,'color':'k'}

    gaugenos = check_gaugenos_input(gauge_solutions, gaugenos)
    
    for gaugeno in gaugenos:
        g = gauge_solutions[gaugeno]
        if g.particle_path is None: 
            continue # no gauge data yet, go on to next gauge
        tg = g.particle_path[:,0]
        xg = g.particle_path[:,1]
        yg = g.particle_path[:,2]
        if 1:
            if t1 is None:
                i1 = 0
                t1 = tg[0]
            else:
                try:
                    i1 = numpy.where(tg>=t1)[0][0]
                except:
                    i1 = None
            if t2 is None:
                i2 = -1
                t2 = tg[-1]
            else:
                try:
                    i2 = numpy.where(tg<=t2)[0][-1]
                except:
                    i2 = None
            
            if (i1 is not None) and (i2 is not None):
                pp1 = interp_particles(gauge_solutions, t1, gaugeno, extend)
                pp2 = interp_particles(gauge_solutions, t2, gaugeno, extend)
                xp = numpy.hstack((pp1[gaugeno][0], xg[i1:i2], pp2[gaugeno][0]))
                yp = numpy.hstack((pp1[gaugeno][1], yg[i1:i2], pp2[gaugeno][1]))
                plt.plot(xp, yp, **kwargs_plot)
            else:
                pass # no points in this time range

