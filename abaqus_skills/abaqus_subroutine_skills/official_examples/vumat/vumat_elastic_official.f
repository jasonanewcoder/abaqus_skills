C=======================================================================
C Abaqus Official Example: VUMAT for Linear Elastic Material
C For Abaqus/Explicit
C=======================================================================
      subroutine vumat(
C Read only (unmodifiable) variables -
     1  nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     2  stepTime, totalTime, dt, cmname, coordMp, charLength,
     3  props, density, strainInc, relSpinInc,
     4  tempOld, stretchOld, defgradOld, fieldOld,
     5  stressOld, stateOld, enerInternOld, enerInelasOld,
     6  tempNew, stretchNew, defgradNew, fieldNew,
C Write only (modifiable) variables -
     7  stressNew, stateNew, enerInternNew, enerInelasNew )
C
      include 'vaba_param.inc'
C
      dimension props(nprops), density(nblock), coordMp(nblock,*),
     1  charLength(nblock), strainInc(nblock,ndir+nshr),
     2  relSpinInc(nblock,nshr), tempOld(nblock),
     3  stretchOld(nblock,ndir+nshr),
     4  defgradOld(nblock,ndir+nshr+nshr),
     5  fieldOld(nblock,nfieldv), stressOld(nblock,ndir+nshr),
     6  stateOld(nblock,nstatev), enerInternOld(nblock),
     7  enerInelasOld(nblock), tempNew(nblock),
     8  stretchNew(nblock,ndir+nshr),
     9  defgradNew(nblock,ndir+nshr+nshr),
     1  fieldNew(nblock,nfieldv),
     2  stressNew(nblock,ndir+nshr), stateNew(nblock,nstatev),
     3  enerInternNew(nblock), enerInelasNew(nblock)
C
      character*80 cmname
C
      parameter( zero = 0.d0, one = 1.d0, two = 2.d0, three = 3.d0,
     1  third = one/three, half = .5d0, twoThirds = two/three,
     2  threeHalfs = 1.5d0 )
C
C     Read material properties
      e    = props(1)
      xnu  = props(2)
C
C     Compute lame constants
      alamda = xnu*e / ((one+xnu)*(one-two*xnu))
      amu    = half*e / (one+xnu)
C
C     Update stresses using Jaumann rate
C
      do 100 i = 1,nblock
C
C       Get old stress components
        trace = stressOld(i,1) + stressOld(i,2) + stressOld(i,3)
        sigOld1 = stressOld(i,1) + trace/three
        sigOld2 = stressOld(i,2) + trace/three
        sigOld3 = stressOld(i,3) + trace/three
        sigOld4 = stressOld(i,4)
        sigOld5 = stressOld(i,5)
        sigOld6 = stressOld(i,6)
C
C       Apply rotation (Jaumann rate)
        if (nshr .eq. 1) then
          sigNew1 = sigOld1 - sigOld4*relSpinInc(i,1)*two
          sigNew2 = sigOld2 + sigOld4*relSpinInc(i,1)*two
          sigNew3 = sigOld3
          sigNew4 = sigOld4 + (sigOld1-sigOld2)*relSpinInc(i,1)
        else
          sigNew1 = sigOld1 - sigOld4*relSpinInc(i,1)*two
     1                  + sigOld5*relSpinInc(i,2)*two
          sigNew2 = sigOld2 + sigOld4*relSpinInc(i,1)*two
     1                  - sigOld6*relSpinInc(i,3)*two
          sigNew3 = sigOld3 - sigOld5*relSpinInc(i,2)*two
     1                  + sigOld6*relSpinInc(i,3)*two
          sigNew4 = sigOld4 + (sigOld1-sigOld2)*relSpinInc(i,1)
     1                  - sigOld6*relSpinInc(i,2)
     2                  - sigOld5*relSpinInc(i,3)
          sigNew5 = sigOld5 + sigOld4*relSpinInc(i,2)
     1                  + (sigOld1-sigOld3)*relSpinInc(i,2)
     2                  - sigOld6*relSpinInc(i,1)
          sigNew6 = sigOld6 + sigOld4*relSpinInc(i,3)
     1                  + (sigOld2-sigOld3)*relSpinInc(i,3)
     2                  + sigOld5*relSpinInc(i,1)
        end if
C
C       Compute stress increment from strain increment
        traceStrainInc = strainInc(i,1) + strainInc(i,2) 
     1                   + strainInc(i,3)
C
        sigNew1 = sigNew1 + alamda*traceStrainInc 
     1                    + two*amu*strainInc(i,1)
        sigNew2 = sigNew2 + alamda*traceStrainInc 
     1                    + two*amu*strainInc(i,2)
        sigNew3 = sigNew3 + alamda*traceStrainInc 
     1                    + two*amu*strainInc(i,3)
        sigNew4 = sigNew4 + amu*strainInc(i,4)
        if (nshr .gt. 1) then
          sigNew5 = sigNew5 + amu*strainInc(i,5)
          sigNew6 = sigNew6 + amu*strainInc(i,6)
        end if
C
C       Store new stress
        stressNew(i,1) = sigNew1
        stressNew(i,2) = sigNew2
        stressNew(i,3) = sigNew3
        stressNew(i,4) = sigNew4
        if (nshr .gt. 1) then
          stressNew(i,5) = sigNew5
          stressNew(i,6) = sigNew6
        end if
C
C       Update internal energy
        enerInternNew(i) = enerInternOld(i) 
     1    + half * (
     2      (stressOld(i,1)+stressNew(i,1))*strainInc(i,1) +
     3      (stressOld(i,2)+stressNew(i,2))*strainInc(i,2) +
     4      (stressOld(i,3)+stressNew(i,3))*strainInc(i,3) +
     5      (stressOld(i,4)+stressNew(i,4))*strainInc(i,4) +
     6      (stressOld(i,5)+stressNew(i,5))*strainInc(i,5) +
     7      (stressOld(i,6)+stressNew(i,6))*strainInc(i,6) ) / density(i)
C
 100  continue
C
      return
      end
