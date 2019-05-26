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
    
    # for debugging:
    gaugenos_lagrangian = [k for k in gauge_solutions.keys() \
                if gauge_solutions[k].gtype=='lagrangian']
    gaugenos_stationary = [k for k in gauge_solutions.keys() \
                if gauge_solutions[k].gtype=='stationary']
    print('+++ Loaded %i stationary and %i Lagrangian gauges' \
        % (len(gaugenos_stationary),len(gaugenos_lagrangian)))
        
    return gauge_solutions
                
def interp_particles(gauge_solutions, t, gaugenos='all'):
    """
    Interpolate (x,y) to the given time t for each specified gauge.
    Returns a dictionary of results indexed by gauge number.
    """
    
    if gaugenos=='all':
        gaugenos = [k for k in gauge_solutions.keys() \
                    if gauge_solutions[k].gtype=='lagrangian']
    elif type(gaugenos) is int:
        gaugenos = [gaugenos]  # single gaugeno passed in
        
    particle_positions = {}
    for gaugeno in gaugenos:
        g = gauge_solutions[gaugeno]
        tg = g.particle_path[:,0]
        xg = g.particle_path[:,1]
        yg = g.particle_path[:,2]
        if t <= tg[0]:
            x = xg[0]
            y = yg[0]
        elif t > tg[-1]:
            x = numpy.nan
            y = numpy.nan
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


def plot_particles(gauge_solutions, t, gaugenos='all', kwargs_plot=None):
    """
    Plot particle locations as points for some set of gauges.
    """
    from matplotlib import pyplot as plt

    if gaugenos=='all':
        gaugenos = [k for k in gauge_solutions.keys() \
                    if gauge_solutions[k].gtype=='lagrangian']
    elif type(gaugenos) is int:
        gaugenos = [gaugenos]
        
    if kwargs_plot is None:
        kwargs_plot = {'marker':'o','markersize':2,'color':'k'}
        
    pp = interp_particles(gauge_solutions, t, gaugenos)
    for k in pp.keys():
        x,y = pp[k]
        plt.plot([x],[y],**kwargs_plot)
        

def plot_paths(gauge_solutions, t1=None, t2=None, gaugenos='all', kwargs_plot=None):
    """
    Plot the particle path for a set of gauges over some time interval.
    """
    from matplotlib import pyplot as plt
    
    if kwargs_plot is None:
        kwargs_plot = {'linestyle':'-','linewidth':0.7,'color':'k'}

    if gaugenos=='all':
        gaugenos = [k for k in gauge_solutions.keys() \
                    if gauge_solutions[k].gtype=='lagrangian']
    elif type(gaugenos) is int:
        gaugenos = [gaugenos]
        
    for gaugeno in gaugenos:
        g = gauge_solutions[gaugeno]
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
            
            #print('+++ gaugeno = %i, i1,i2: %i,%i' % (gaugeno,i1,i2))
            if (i1 is not None) and (i2 is not None):
                pp1 = interp_particles(gauge_solutions, t1, gaugeno)
                pp2 = interp_particles(gauge_solutions, t2, gaugeno)
                xp = numpy.hstack((pp1[gaugeno][0], xg[i1:i2], pp2[gaugeno][0]))
                yp = numpy.hstack((pp1[gaugeno][1], yg[i1:i2], pp2[gaugeno][1]))
                plt.plot(xp, yp, **kwargs_plot)
                #print('+++ gaugeno = %i, len(xp,py) = %i, %i' % (gaugeno,len(xp),len(yp)))
            else:
                pass # no points in this time range
            #import pdb; pdb.set_trace()
        #except:
        #    raise(Exception)
                
    