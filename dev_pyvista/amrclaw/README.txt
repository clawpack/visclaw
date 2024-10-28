
Contents of dev_pyvista/amrclaw:

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
