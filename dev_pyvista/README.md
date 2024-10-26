# visclaw/dev_pyvista

Directory for developing new visualization tools using PyVista and GeoVista.
Currently it contains several examples that are works in progress.

### Documentation and installation instructions:

- https://docs.pyvista.org/
- https://geovista.readthedocs.io/en/latest/

It seems to work fine to just do:

    pip install pyvista
    pip install geovista


Contents:

amrclaw/

    unpack_frame_2d.py - module with code to read in a single frame of 2D AMR
        data with an iterator class that can be used to iterate over all the AMR
        patches for this frame, going from coarsest to finest levels.
        This can be used to plot each patch on top of coarser ones, as done
        normally in visclaw when frametools.py is used via specifying a
        setplot.py script.
        
        For PyVista plots, it is preferable to clip out rectanglar patches
        from the coarser grids anywhere a finer grid is available, particularly
        if the plot is warped into a 3D surface.
        
    test_amrclaw_2d_plots.py - some sample code illustrating how to plot AMR
        frame data in 2D.
        
    unpack_frame_3d.py - module with code to read in a single frame of 3D AMR
        data with an iterator class that can be used to iterate over all the AMR
        patches for this frame, going from coarsest to finest levels.    
        There are currently no matplotlib tools in visclaw for plotting such
        data, only some matlab code.
        
        For PyVista, this new module can be used to clip out 3D regions from
        the coarser grids anywhere a finer grid is available.
        
geoclaw/topo_plots/

    bg_image.py - module to facilitate downloading satellite image or map
        for background image, or to use as texture when plotting warped topo
        
    test_bg_image.py - a couple tests of bg_image.py
    
geoclaw/amr_frames/

    test_geoclaw_plots.py - some sample code illustrating how to plot AMR
        frame data in 2D for GeoClaw applications, on a projected plane,
        perhaps with 3D warping based on topography and/or surface elevation.
        
geoclaw/sphere/

    test_geoclaw_sphere_plots.py - some sample code illustrating how to plot
        GeoClaw AMR output on the sphere.
        
