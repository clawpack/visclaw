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

geoclaw/topo_plots
    bg_image.py - module to facilitate downloading satellite image or map
        for background image or to use as texture when plotting warped topo
    test_bg_image.py - a couple tests of bg_image.py
    
    TODO: When image is loaded and used the extent is not quite right.
    
