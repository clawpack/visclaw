"""
Tools for Lagrangian gauges (particle tracking).
First attempt, could be improved.
"""

import numpy

class ParticleSolutions(object):
    
    def __init__(self, outdir='.', gaugenos=None):
        """
        gaugenos should be a list of gauge numbers, a single number, or 'all'.
        """
        
        self.outdir = outdir  # where to find gaugeXXXXX.txt files
        
        # dictionaries to be indexed by gauge number:
        self.particle = {}  # values will be tuple of arrays (t,x,y)
        self.t0 = {}        # values will be start time at each gauge
        self.tend = {}      # values will be end time at each gauge
        
        self.gauge_numbers = []  # gauges that have been read in
        
        if gaugenos is not None:
            self.read(gaugenos)
            
    def read(self, gaugenos='all'):
        """
        Read gauges from self.outdir directory.
        gaugenos should be a list of gauge numbers, a single number, or 'all'.
        """
        
        from clawpack.amrclaw.data import GaugeData
        from clawpack.pyclaw.gauges import GaugeSolution
        import warnings
    
        gd = GaugeData(self.outdir)
        gd.read()
        
        if (type(gaugenos) is int) or (type(gaugenos) is str):
            gaugenos = [gaugenos]  # single gaugeno passed in
                
        for gaugeno in gd.gauge_numbers:
            if (gaugeno in gaugenos) or (gaugenos[0] == 'all'):
                g = GaugeSolution(gaugeno, self.outdir)
                if g.gtype == 'lagrangian':
                    tg = g.t
                    xg = g.q[1,:]
                    yg = g.q[2,:]
                    self.particle[gaugeno] = (tg,xg,yg)
                    self.t0[gaugeno] = tg[0]     # start time
                    self.tend[gaugeno] = tg[-1]  # end time
                elif gaugeno in gaugenos: 
                    warnings.warn("Gauge %i is not Lagrangian" % gaugeno)
                    
        self.gauge_numbers = list(self.particle.keys())
                
                
    def interp_particles(self, t, gaugenos='all'):
        """
        Interpolate (x,y) to the given time t for each specified gauge.
        Returns a dictionary of results indexed by gauge number.
        """
        
        if gaugenos=='all':
            gaugenos = self.particle.keys()
        elif type(gaugenos) is int:
            gaugenos = [gaugenos]  # single gaugeno passed in
            
        particle_positions = {}
        for gaugeno in gaugenos:
            tg,xg,yg = self.particle[gaugeno]
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


    def plot_particles(self, t, gaugenos='all', kwargs_plot=None):
        """
        Plot particle locations as points for some set of gauges.
        """
        from matplotlib import pyplot as plt
        
        if kwargs_plot is None:
            kwargs_plot = {'marker':'o','markersize':2,'color':'k'}
            
        pp = self.interp_particles(t, gaugenos)
        for k in pp.keys():
            x,y = pp[k]
            plt.plot([x],[y],**kwargs_plot)
            


    def plot_paths(self, t1=None, t2=None, gaugenos='all', kwargs_plot=None):
        """
        Plot the particle path for a set of gauges over some time interval.
        """
        from matplotlib import pyplot as plt
        
        if kwargs_plot is None:
            kwargs_plot = {'linestyle':'-','linewidth':0.7,'color':'k'}

        if gaugenos=='all':
            gaugenos = self.particle.keys()
        elif type(gaugenos) is int:
            gaugenos = [gaugenos]
            
        for k in gaugenos:
            t,x,y = self.particle[k] 
            try:
                if t1 is None:
                    i1 = 0
                else:
                    try:
                        i1 = numpy.where(t>=t1)[0][0]
                    except:
                        i1 = None
                if t2 is None:
                    i2 = -1
                else:
                    try:
                        i2 = numpy.where(t<=t2)[0][-1]
                    except:
                        i2 = None
                
                if (i1 is not None) and (i2 is not None):
                    pp1 = self.interp_particles(t1, k)
                    pp2 = self.interp_particles(t2, k)
                    xp = numpy.hstack((pp1[k][0], x[i1:i2], pp2[k][0]))
                    yp = numpy.hstack((pp1[k][1], y[i1:i2], pp2[k][1]))
                    plt.plot(xp, yp, **kwargs_plot)
                else:
                    pass # no points in this time range
            except:
                raise(Exception)
                #pass
    