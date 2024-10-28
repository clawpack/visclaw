# visclaw/dev_pyvista

Directory for developing new visualization tools using PyVista and GeoVista.
Currently it contains several examples that are works in progress.

### Documentation and installation instructions:

- https://docs.pyvista.org/
- https://geovista.readthedocs.io/en/latest/

It seems to work fine to just do:

    pip install pyvista
    pip install geovista


### Contents:

- amrclaw/unpack_frame_patches.py - module with code to read in a single frame
  of AMR data with an iterator class that can be used to iterate over all the
  AMR patches for this frame.
          
- geoclaw/topo_plots/ - various modules and scripts to display topo data and
  water elevation on warped grids, with satellite images or maps draped on them.

- geoclaw/amr_frames/ - test codes to display time frames from GeoClaw.

- geoclaw/sphere/ - displaying global-scale simulations on the sphere.

**See amrclaw/README.txt and geoclaw/README.txt for more info.**
        

### Other examples:

See also the code:
https://github.com/rjleveque/NuuRefugeTsunami/blob/main/geoclaw_run/pyvista_fgout_Nuu_debris.py

used to create the animations found on this page:
https://faculty.washington.edu/rjl/pubs/NuuRefugeTsunami/
