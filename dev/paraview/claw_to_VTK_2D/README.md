# Convert Clawpack output data to VTK format

An example, water\_depth.avi can be found at:
https://github.com/xinshengqin/claw_to_vtk

It shows an example of visualizing result of the GeoClaw case in $CLAW/geoclaw/examples/tsunami/bowl-radial with Paraview.

## Usage:
    Run the python script convert_all_frames.py in a GeoClaw case directory:
    python $CLAW/visclaw/dev/paraview/claw_to_VTK_2D/convert_all_frames.py [geoclaw output format] [geoclaw output directory] [starting frame number] [ending frame number] 

    e.g.
    python $CLAW/visclaw/dev/paraview/claw_to_VTK_2D/convert_all_frames.py binary _output 1 10 
    will convert geoclaw output frame 1-10 in ./_output and output all VTK files in _output_vtk

    You can then open Paraview and read *.vthb files in _output_vtk

## Tip:
For 3D plots like the two examples in this directory, chile.png and bainbridge.png, one can do the following in Paraview.

1. Open *.vthb in _output_vtk

2. Add a mask to set \eta to 0 on dry land: 1) Add a "Calculator" filter and use "q_3*(q_0>0.001)" as criteria. This will create a new data variable. Assume we name it eta_new.

3. Add a "CellDatatoPointData" filter to convert cell data to point data.

4. Add a "WarpByScalar" filter to extrude the 2D surface in z direction based on eta_new.

5. Open *.vthb in _output_vtk again.

6. Add a "Calculator" filter based on new *.vthb files and use "q_3-q_0" as the formula. This computes topography as a new data variable. Let us name it B.

7. Add a "CellDatatoPointData" filter to convert cell data to point data.

8. Add a "WarpByScalar" filter to extrude the 2D surface in z direction based on B.

