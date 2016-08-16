# Convert Clawpack output data to VTK format

## How to use:

###Example:

1. Put all these files to a local directory, e.g. $HOME/claw\_to\_vtk

2. Set PATH environment variables to include that directory:

        export PATH=$PATH: $HOME/claw_to_vtk

3. Change working directory to clawpack case:

        cd $CLAW/amrclaw/examples/acoustics_2d_radial

4. Run clawpack case to get output from clawpack

5. Convert clawpack output to VTK format (will write VTK files in \_output\_vtk):

        python convert_all_frames.py ascii _output 1 10 


6. Open paraview and read *.vthb files in \_output\_vtk

    
