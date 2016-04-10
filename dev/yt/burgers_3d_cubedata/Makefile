
# Makefile for Clawpack code in this directory.
# This version only sets the local files and frequently changed
# options, and then includes the standard makefile pointed to by CLAWMAKE.
CLAWMAKE = $(CLAW)/clawutil/src/Makefile.common

# See the above file for details and a list of make options, or type
#   make .help
# at the unix prompt.


# Adjust these variables if desired:
# ----------------------------------

CLAW_PKG = amrclaw                  # Clawpack package to use
EXE = xamr                          # Executable to create
SETRUN_FILE = setrun.py             # File containing function to make data
OUTDIR = _output                    # Directory for output
SETPLOT_FILE = setplot.py           # File containing function to set plots
PLOTDIR = _plots                    # Directory for plots

OVERWRITE ?= True                   # False ==> make a copy of OUTDIR first
RESTART ?= False                    # Should = clawdata.restart in setrun

# Environment variable FC should be set to fortran compiler, e.g. gfortran

# Compiler flags can be specified here or set as an environment variable
FFLAGS ?=  

# ---------------------------------
# List of sources for this program:
# ---------------------------------

AMRLIB = $(CLAW)/amrclaw/src/3d

MODULES = \
  $(AMRLIB)/amr_module.f90 \
  $(AMRLIB)/gauges_module.f90
#$(AMRLIB)/regions_module.f90 \

SOURCES = \
  qinit.f \
  setprob.f \
  $(CLAW)/riemann/src/rpn3_burgers.f90 \
  $(CLAW)/riemann/src/rpt3_burgers.f90 \
  $(CLAW)/riemann/src/rptt3_burgers.f90 \
  $(AMRLIB)/amr3.f90 \
  $(AMRLIB)/setaux.f90 \
  $(AMRLIB)/bc3amr.f \
  $(AMRLIB)/opendatafile.f \
  $(AMRLIB)/b4step3.f90 \
  $(AMRLIB)/qad.f \
  $(AMRLIB)/src3.f90 \
  $(AMRLIB)/src1d.f90 \
  $(AMRLIB)/advanc.f \
  $(AMRLIB)/bound.f \
  $(AMRLIB)/stepgrid.f \
  $(AMRLIB)/stepgrid_dimSplit.f \
  $(AMRLIB)/auxcoarsen.f \
  $(AMRLIB)/fixcapaq.f \
  $(AMRLIB)/estdt.f \
  $(AMRLIB)/igetsp.f \
  $(AMRLIB)/reclam.f \
  $(AMRLIB)/birect.f \
  $(AMRLIB)/cleanup.f \
  $(AMRLIB)/colate.f \
  $(AMRLIB)/errest.f \
  $(AMRLIB)/flag2refine.f \
  $(AMRLIB)/allowflag.f \
  $(AMRLIB)/bufnst.f \
  $(AMRLIB)/spest.f \
  $(AMRLIB)/errf1.f \
  $(AMRLIB)/gfixup.f \
  $(AMRLIB)/filval.f \
  $(AMRLIB)/filpatch.f \
  $(AMRLIB)/prefilp.f \
  $(AMRLIB)/flglvl.f \
  $(AMRLIB)/fluxad.f \
  $(AMRLIB)/fluxsv.f \
  $(AMRLIB)/ginit.f \
  $(AMRLIB)/grdfit.f \
  $(AMRLIB)/intfil.f \
  $(AMRLIB)/moment.f \
  $(AMRLIB)/nestck.f \
  $(AMRLIB)/prepc.f \
  $(AMRLIB)/prepf.f \
  $(AMRLIB)/projec.f \
  $(AMRLIB)/signs.f \
  $(AMRLIB)/findcut.f \
  $(AMRLIB)/smartbis.f \
  $(AMRLIB)/putnod.f \
  $(AMRLIB)/putsp.f \
  $(AMRLIB)/regrid.f \
  $(AMRLIB)/setgrd.f \
  $(AMRLIB)/setuse.f \
  $(AMRLIB)/stst1.f \
  $(AMRLIB)/tick.f \
  $(AMRLIB)/trimbd.f \
  $(AMRLIB)/update.f \
  $(AMRLIB)/nodget.f \
  $(AMRLIB)/upbnd.f  \
  $(AMRLIB)/basic.f \
  $(AMRLIB)/outval.f \
  $(AMRLIB)/copysol.f \
  $(AMRLIB)/outvar.f \
  $(AMRLIB)/outmsh.f \
  $(AMRLIB)/outtre.f \
  $(AMRLIB)/domain.f  \
  $(AMRLIB)/setflags.f \
  $(AMRLIB)/shiftset.f \
  $(AMRLIB)/conck.f \
  $(AMRLIB)/domshrink.f \
  $(AMRLIB)/domprep.f \
  $(AMRLIB)/domup.f \
  $(AMRLIB)/domcopy.f \
  $(AMRLIB)/coarsen.f \
  $(AMRLIB)/intcopy.f \
  $(AMRLIB)/preintcopy.f \
  $(AMRLIB)/icall.f \
  $(AMRLIB)/preicall.f \
  $(AMRLIB)/step3.f \
  $(AMRLIB)/step3x.f \
  $(AMRLIB)/step3y.f \
  $(AMRLIB)/step3z.f \
  $(AMRLIB)/flux3.f \
  $(AMRLIB)/flux3_dimSplit.f \
  $(AMRLIB)/limiter.f \
  $(AMRLIB)/philim.f \
  $(AMRLIB)/cstore.f \
  $(AMRLIB)/saveqc.f \
  $(AMRLIB)/valout.f \
  $(AMRLIB)/check.f \
  $(AMRLIB)/restrt.f \
  $(AMRLIB)/quick_sort1.f \
  $(AMRLIB)/init_alloc.f90 \
  $(AMRLIB)/resize_alloc.f90 \
  $(AMRLIB)/restrt_alloc.f90

#-------------------------------------------------------------------
# Include Makefile containing standard definitions and make options:
include $(CLAWMAKE)

