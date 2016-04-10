c     ==================
      subroutine setprob
c     ==================

      implicit double precision (a-h,o-z)
      character*12 fname
      common /cparam/ coeff(3)
c
c     # for 3d Burgers' equation
c     #    q_t  +  u*(.5*q^2)_x + v*(.5*q^2)_y + w*(.5*q^2)_z = 0
c     # where u,v,w are a given scalars, stored in the vector coeff

      iunit = 7
      fname = 'setprob.data'
c     # open the unit with new routine from Clawpack 4.4 to skip over
c     # comment lines starting with #:
      call opendatafile(iunit, fname)

      read(7,*) coeff(1)
      read(7,*) coeff(2)
      read(7,*) coeff(3)

      return
      end
