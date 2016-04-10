c
c
c
c     =====================================================
       subroutine qinit(meqn,mbc,mx,my,mz,xlower,ylower,zlower,
     &                   dx,dy,dz,q,maux,aux)
c     =====================================================
c
c     # Set initial conditions for q.
c
       implicit double precision (a-h,o-z)
c
       dimension   q(meqn,1-mbc:mx+mbc,1-mbc:my+mbc,1-mbc:mz+mbc)
       dimension aux(maux,1-mbc:mx+mbc,1-mbc:my+mbc,1-mbc:mz+mbc)
c
c     # set concentration profile
c     ---------------------------
c
      do  k=1,mz
         zcell = zlower + (k-0.5d0)*dz
         do  j=1,my
            ycell = ylower + (j-0.5d0)*dy
            do  i=1,mx
               xcell = xlower + (i-0.5d0)*dx
 
               if (xcell .gt. 0.1d0 .and. xcell .lt. 0.5d0 .and.
     &             ycell .gt. 0.1d0 .and. ycell .lt. 0.5d0 .and.
     &             zcell .gt. 0.1d0 .and. zcell .lt. 0.5d0) then
                       q(1,i,j,k) = 1.d0
                    else
                       q(1,i,j,k) = 0.d0
                    endif
                end do  
             end do  
          end do  

       return
       end
