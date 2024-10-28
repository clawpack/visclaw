
Contents of dev_pyvista/geoclaw:

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
        
        Uses amrclaw/unpack_frame_patches.py module to load AMR frame data.
        
geoclaw/sphere/

    test_geoclaw_sphere_plots.py - some sample code illustrating how to plot
        GeoClaw AMR output on the sphere.
