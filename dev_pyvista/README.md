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

    unpack_frame_patches.py - module with code to read in a single frame of AMR
        data with an iterator class that can be used to iterate over all the AMR
        patches for this frame, going from coarsest to finest levels.
        This can be used to plot each patch on top of coarser ones, as done
        normally in visclaw in 2D, when frametools.py is used via specifying a
        setplot.py script.  (There are currently no matplotlib tools in visclaw
        for plotting AMR data, only some matlab code.)
        
        For PyVista plots in 2D, it is preferable to clip out rectanglar patches
        from the coarser grids anywhere a finer grid is available, particularly
        if the plot is warped into a 3D surface.  In 3D it is necessary to
        clip out patches in order to properly insert finer grid patches.
        
        This module defines a PatchIterator class that can be used to read
        in a frame solution and yield one patch at a time.
        
    test_amrclaw_2d_plots.py - some sample code illustrating how to plot AMR
        frame data in 2D for a single frame.
        
    test_amrclaw_2d_animate.py - sample code to either provide a slider bar
        to adjust the frame being viewed, or to loop over a set of frames and
        create an animation of the plots at each frame.
        
geoclaw/topo_plots/

    bg_image.py - module to facilitate downloading satellite image or map
        for background image, or to use as texture when plotting warped topo
        
    test_bg_image.py - a couple tests of bg_image.py
    
geoclaw/topo_plots/Quillayute/

    Quillayute_sealevel.py - Plot topography around La Push, WA and provide
        a slider bar to adjust sea level.
    
geoclaw/amr_frames/

    test_geoclaw_plots.py - some sample code illustrating how to plot AMR
        frame data in 2D for GeoClaw applications, on a projected plane,
        perhaps with 3D warping based on topography and/or surface elevation.
        
geoclaw/sphere/

    test_geoclaw_sphere_plots.py - some sample code illustrating how to plot
        GeoClaw AMR output on the sphere.
        

Other examples
--------------

See also the code:
https://github.com/rjleveque/NuuRefugeTsunami/blob/main/geoclaw_run/pyvista_fgout_Nuu_debris.py

used to create the animations found on this page:
https://faculty.washington.edu/rjl/pubs/NuuRefugeTsunami/
