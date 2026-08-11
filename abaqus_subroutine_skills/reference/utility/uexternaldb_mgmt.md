# UEXTERNALDB — External Database / Job Control — Detailed Reference

## Skill Description

UEXTERNALDB is called at job start/end and at every increment — it is the standard way
to:
1. **Read external data files** (moving-load paths, measurement data, temperature files)
   once at job start and keep them in COMMON blocks
2. **Write results/logs** during the run
3. **Coordinate multiple user subroutines** (initialize COMMON data used by
   DLOAD/UMAT/DFLUX/...)

> 中文提示：UEXTERNALDB 是子程序的「管家」——在 job 开始/每个增量/结束时被调用，
> 用来读外部数据文件（如移动荷载路径、实测温度曲线）并存入 COMMON 块供其他
> 子程序使用，或写日志。

## Interface

```fortran
      SUBROUTINE UEXTERNALDB(LOP,LRESTART,TIME,DTIME,KSTEP,KINC)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2)
C
C  LOP: operation code
C    0 - job start:  read files, initialize data
C    1 - increment start
C    2 - increment end
C    3 - job end:    write files, cleanup
C    4 - job abort
C    5 - restart:    read restart data
```

| Argument | Meaning |
|----------|---------|
| LOP | Input: operation code (0..5 above) |
| LRESTART | Input: 1 when this call is a restart step |
| TIME(2) | Input: step time / total time |
| DTIME | Input: current increment size |
| KSTEP, KINC | Input: step / increment number |

## Template: Load a Data File Once and Share via COMMON

```fortran
      SUBROUTINE UEXTERNALDB(LOP,LRESTART,TIME,DTIME,KSTEP,KINC)
C
C  Loads a moving-load path table at job start and exposes it to DLOAD
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2)
C
C  Shared path data (same COMMON block as in DLOAD)
      INTEGER NSEG, MAXSEG
      PARAMETER(MAXSEG=200)
      REAL*8 PATH_X, PATH_Y, PATH_Z, SEG_LEN, PATH_READY
      COMMON /PATHDATA/ PATH_X, PATH_Y, PATH_Z, SEG_LEN, NSEG,
     1                  PATH_READY
      DIMENSION PATH_X(MAXSEG), PATH_Y(MAXSEG), PATH_Z(MAXSEG),
     1          SEG_LEN(MAXSEG)
C
      INTEGER I, IOS, IU
C
      IF (LOP .EQ. 0) THEN
C       Job start: open and read the path file
        IU = 15
        OPEN(UNIT=IU, FILE='wheel_path.txt', STATUS='OLD', IOSTAT=IOS)
        IF (IOS .NE. 0) THEN
          WRITE(*,*) 'UEXTERNALDB: cannot open wheel_path.txt'
          PATH_READY = 0.0D0
          RETURN
        END IF
        NSEG = 0
  100   CONTINUE
        READ(IU,*,IOSTAT=IOS) PATH_X(NSEG+1), PATH_Y(NSEG+1),
     1                         PATH_Z(NSEG+1)
        IF (IOS .EQ. 0) THEN
          NSEG = NSEG + 1
          IF (NSEG .LT. MAXSEG) GOTO 100
        END IF
        CLOSE(IU)
C       Segment lengths from consecutive points
        DO I = 1, NSEG-1
          SEG_LEN(I) = SQRT((PATH_X(I+1)-PATH_X(I))**2
     1                   + (PATH_Y(I+1)-PATH_Y(I))**2
     1                   + (PATH_Z(I+1)-PATH_Z(I))**2)
        END DO
        PATH_READY = 1.0D0
        WRITE(*,*) 'UEXTERNALDB: loaded', NSEG, 'path points'
      ELSE IF (LOP .EQ. 3 .OR. LOP .EQ. 4) THEN
C       Job end / abort: cleanup
        PATH_READY = 0.0D0
      END IF
C
      RETURN
      END
```

The DLOAD subroutine then uses the same COMMON block:

```fortran
      INTEGER MAXSEG
      PARAMETER(MAXSEG=200)
      REAL*8 PATH_X, PATH_Y, PATH_Z, SEG_LEN, PATH_READY
      COMMON /PATHDATA/ PATH_X, PATH_Y, PATH_Z, SEG_LEN, NSEG,
     1                  PATH_READY
      DIMENSION PATH_X(MAXSEG), PATH_Y(MAXSEG), PATH_Z(MAXSEG),
     1          SEG_LEN(MAXSEG)
      ...   (use PATH_X etc. — see dload_moving.md path-following template)
```

> **IMPORTANT**: COMMON blocks shared between subroutines must declare the arrays
> with the SAME dimensions and order in every subroutine that uses them.

## Input File / Setup Notes

```abaqus
*User Defined Field, properties=0   ! not needed for UEXTERNALDB
*User Output Variables
```

UEXTERNALDB needs no keyword — it is always called when the job runs with any user
subroutine. Only ensure the data file (`wheel_path.txt`) exists in the working directory.

## Guidance

1. Always guard file I/O with `IOSTAT` — a missing file must not crash the job
2. Use `LOP=0` for reading and `LOP=3/4` for closing — never read every increment
3. For restart runs, `LRESTART=1` + `LOP=0` — re-read or reuse COMMON data
4. Keep COMMON blocks in a separate `.inc` file and `INCLUDE` it in every subroutine
5. `WRITE(*,*)` from UEXTERNALDB appears in the `.log` — useful for agent logs

## Related

- `dload_moving.md` / `vdload_moving.md` — consumers of the shared path data
- `umat_plasticity.md` — state data shared from UEXTERNALDB via COMMON
